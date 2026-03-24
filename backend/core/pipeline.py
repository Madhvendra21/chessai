import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Callable
import sys
import os

# Add CV pipeline to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'cv-pipeline'))

from detector.board_detector import BoardDetector
from detector.piece_detector import PieceDetector
from detector.state_tracker import StateTracker

logger = logging.getLogger(__name__)


class ChessVisionPipeline:
    """Main pipeline for processing chess videos."""
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 confidence: float = 0.5,
                 progress_callback: Optional[Callable[[str, int], None]] = None):
        self.board_detector = BoardDetector()
        self.piece_detector = PieceDetector(model_path, confidence)
        self.state_tracker = StateTracker(history_size=5)
        self.progress_callback = progress_callback
    
    def process_video(self, video_path: str, frames_dir: str) -> Dict:
        """
        Process a chess video and extract moves.
        Returns dict with moves, PGN, and metadata.
        """
        logger.info(f"Starting pipeline for {video_path}")
        
        # Get list of frames
        frame_paths = sorted(Path(frames_dir).glob("*.jpg"))
        total_frames = len(frame_paths)
        
        if total_frames == 0:
            raise ValueError(f"No frames found in {frames_dir}")
        
        logger.info(f"Processing {total_frames} frames")
        
        # Detect board corners from first frame
        first_frame = cv2.imread(str(frame_paths[0]))
        board_corners = self.board_detector.detect_board(first_frame)
        
        if board_corners is None:
            logger.warning("Could not detect board corners, trying classical detection")
            # Try with edge detection
            board_corners = self._fallback_board_detection(first_frame)
        
        if board_corners is None:
            raise ValueError("Could not detect chess board in video")
        
        logger.info("Board detected successfully")
        
        # Warp board to get top-down view
        warped_board = self.board_detector.warp_board(first_frame, board_corners)
        board_size = warped_board.shape[0]
        
        # Process each frame
        last_detections = None
        stable_frame_count = 0
        
        for i, frame_path in enumerate(frame_paths):
            # Update progress
            if self.progress_callback and i % 10 == 0:
                progress = int((i / total_frames) * 100)
                self.progress_callback("processing", progress)
            
            # Load and warp frame
            frame = cv2.imread(str(frame_path))
            warped = self.board_detector.warp_board(frame, board_corners)
            
            # Detect pieces
            detections = self.piece_detector.detect_pieces(warped)
            
            # Map to squares
            board_state = self.piece_detector.map_detections_to_squares(detections, board_size)
            
            # Add to state tracker
            timestamp = i / 2.0  # Assuming 2 FPS
            move = self.state_tracker.add_frame_state(i, timestamp, board_state)
            
            if move:
                logger.info(f"Detected move: {move['san']}")
        
        # Generate PGN
        pgn = self.state_tracker.get_pgn({
            "Event": "ChessVision AI Analysis",
            "Site": "Local",
            "Date": "2024.01.01",
            "Round": "1",
            "White": "Player 1",
            "Black": "Player 2"
        })
        
        return {
            "pgn": pgn,
            "moves": self.state_tracker.moves_detected,
            "total_frames": total_frames,
            "total_moves": len(self.state_tracker.moves_detected)
        }
    
    def _fallback_board_detection(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Fallback method for board detection using classical CV."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Use Hough lines to find board edges
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return None
        
        # Find intersection points (potential corners)
        # This is a simplified version - real implementation would be more robust
        height, width = frame.shape[:2]
        
        # Assume board is roughly centered and takes up most of the frame
        margin = min(height, width) // 4
        corners = np.array([
            [margin, margin],
            [width - margin, margin],
            [width - margin, height - margin],
            [margin, height - margin]
        ], dtype=np.float32)
        
        return corners

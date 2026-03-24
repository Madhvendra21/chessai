import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from ultralytics import YOLO
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Class mapping for YOLO chess piece detection
PIECE_CLASSES = {
    0: ('white', 'pawn'),
    1: ('white', 'rook'),
    2: ('white', 'knight'),
    3: ('white', 'bishop'),
    4: ('white', 'queen'),
    5: ('white', 'king'),
    6: ('black', 'pawn'),
    7: ('black', 'rook'),
    8: ('black', 'knight'),
    9: ('black', 'bishop'),
    10: ('black', 'queen'),
    11: ('black', 'king'),
}


class PieceDetector:
    """Detects chess pieces using YOLO model."""
    
    def __init__(self, model_path: Optional[str] = None, confidence: float = 0.5):
        self.confidence = confidence
        self.model = None
        self.model_path = model_path
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load YOLO model for piece detection."""
        try:
            self.model = YOLO(model_path)
            logger.info(f"Loaded YOLO model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Fall back to CIFAR-based detection if YOLO fails
            self.model = None
    
    def detect_pieces(self, frame: np.ndarray, board_corners: Optional[np.ndarray] = None) -> List[Dict]:
        """
        Detect pieces in frame.
        Returns list of detections with class, confidence, and bounding box.
        """
        if self.model is None:
            # Fallback: use classical CV approach
            return self._classical_detection(frame, board_corners)
        
        try:
            results = self.model(frame, conf=self.confidence, verbose=False)
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    if cls_id in PIECE_CLASSES:
                        color, piece_type = PIECE_CLASSES[cls_id]
                        detections.append({
                            'class_id': cls_id,
                            'color': color,
                            'piece': piece_type,
                            'confidence': conf,
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'center': (int((x1 + x2) / 2), int((y1 + y2) / 2))
                        })
            
            return detections
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            return self._classical_detection(frame, board_corners)
    
    def _classical_detection(self, frame: np.ndarray, board_corners: Optional[np.ndarray] = None) -> List[Dict]:
        """
        Fallback classical CV-based piece detection.
        Uses contour analysis and color segmentation.
        """
        detections = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find pieces
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100 or area > 5000:  # Filter by size
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # Pieces are roughly square
            if 0.5 < aspect_ratio < 2.0:
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Determine color based on center pixel
                hue = hsv[center_y, center_x, 0]
                sat = hsv[center_y, center_y, 1]
                val = hsv[center_y, center_y, 2]
                
                # Simple color classification (white vs black)
                if val > 150 and sat < 50:
                    color = 'white'
                else:
                    color = 'black'
                
                detections.append({
                    'class_id': -1,
                    'color': color,
                    'piece': 'unknown',
                    'confidence': 0.5,
                    'bbox': (x, y, x + w, y + h),
                    'center': (center_x, center_y)
                })
        
        return detections
    
    def map_detections_to_squares(self, detections: List[Dict], board_size: int = 800) -> Dict[str, Dict]:
        """
        Map piece detections to chess board squares.
        Returns dict mapping square notation (e.g., 'e4') to piece info.
        """
        square_size = board_size // 8
        board_state = {}
        
        for det in detections:
            cx, cy = det['center']
            
            # Calculate square coordinates
            file_idx = cx // square_size
            rank_idx = cy // square_size
            
            if 0 <= file_idx < 8 and 0 <= rank_idx < 8:
                # Convert to chess notation (a1-h8)
                file_char = chr(ord('a') + file_idx)
                rank_char = str(8 - rank_idx)
                square = f"{file_char}{rank_char}"
                
                # Keep detection with highest confidence for each square
                if square not in board_state or det['confidence'] > board_state[square]['confidence']:
                    board_state[square] = det
        
        return board_state

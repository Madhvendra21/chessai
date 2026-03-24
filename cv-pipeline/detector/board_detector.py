import cv2
import numpy as np
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


class BoardDetector:
    """Detects chessboard corners and performs perspective correction."""
    
    def __init__(self, min_board_size: int = 400):
        self.min_board_size = min_board_size
    
    def detect_board(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect chessboard in frame and return corner points.
        Returns 4x2 array of corner coordinates (top-left, top-right, bottom-right, bottom-left).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter for rectangular contours (potential chessboards)
        candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_board_size * self.min_board_size:
                continue
            
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # Look for 4-sided polygons
            if len(approx) == 4:
                candidates.append(approx)
        
        if not candidates:
            return None
        
        # Select largest candidate
        largest = max(candidates, key=cv2.contourArea)
        corners = largest.reshape(4, 2).astype(np.float32)
        
        # Order corners: top-left, top-right, bottom-right, bottom-left
        return self._order_corners(corners)
    
    def _order_corners(self, corners: np.ndarray) -> np.ndarray:
        """Order corners in consistent order."""
        # Sort by y-coordinate
        corners = corners[np.argsort(corners[:, 1])]
        
        # Top two and bottom two
        top = corners[:2]
        bottom = corners[2:]
        
        # Sort top by x (left to right)
        top = top[np.argsort(top[:, 0])]
        # Sort bottom by x (left to right)
        bottom = bottom[np.argsort(bottom[:, 0])]
        
        return np.array([
            top[0],      # top-left
            top[1],      # top-right
            bottom[1],   # bottom-right
            bottom[0]    # bottom-left
        ], dtype=np.float32)
    
    def warp_board(self, frame: np.ndarray, corners: np.ndarray, output_size: int = 800) -> np.ndarray:
        """
        Apply perspective transform to get top-down view of board.
        """
        dst = np.array([
            [0, 0],
            [output_size - 1, 0],
            [output_size - 1, output_size - 1],
            [0, output_size - 1]
        ], dtype=np.float32)
        
        matrix = cv2.getPerspectiveTransform(corners, dst)
        warped = cv2.warpPerspective(frame, matrix, (output_size, output_size))
        
        return warped
    
    def get_square_regions(self, board_size: int = 800) -> List[Tuple[int, int, int, int]]:
        """
        Get coordinates for each of the 64 squares.
        Returns list of (x1, y1, x2, y2) for each square.
        """
        square_size = board_size // 8
        regions = []
        
        for rank in range(8):
            for file in range(8):
                x1 = file * square_size
                y1 = rank * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                regions.append((x1, y1, x2, y2))
        
        return regions

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import chess

logger = logging.getLogger(__name__)


@dataclass
class BoardState:
    """Represents a detected board state."""
    frame_index: int
    timestamp: float
    pieces: Dict[str, str]  # square -> piece (e.g., 'e4': 'wp')
    fen: Optional[str] = None
    confidence: float = 1.0


class StateTracker:
    """Tracks board states across frames and detects moves."""
    
    def __init__(self, history_size: int = 5):
        self.history: deque = deque(maxlen=history_size)
        self.current_board = chess.Board()
        self.moves_detected: List[Dict] = []
        self.last_stable_state: Optional[BoardState] = None
    
    def piece_to_notation(self, color: str, piece: str) -> str:
        """Convert piece detection to FEN notation character."""
        piece_map = {
            'king': 'k', 'queen': 'q', 'rook': 'r',
            'bishop': 'b', 'knight': 'n', 'pawn': 'p'
        }
        
        char = piece_map.get(piece.lower(), 'p')
        if color.lower() == 'white':
            char = char.upper()
        
        return char
    
    def detections_to_fen(self, detections: Dict[str, Dict], active_color: str = 'w') -> str:
        """
        Convert piece detections to FEN string.
        """
        board = [['' for _ in range(8)] for _ in range(8)]
        
        for square, det in detections.items():
            if 'piece' in det and 'color' in det:
                piece_char = self.piece_to_notation(det['color'], det['piece'])
                file_idx = ord(square[0]) - ord('a')
                rank_idx = 8 - int(square[1])
                if 0 <= file_idx < 8 and 0 <= rank_idx < 8:
                    board[rank_idx][file_idx] = piece_char
        
        # Build FEN board component
        fen_rows = []
        for row in board:
            fen_row = ''
            empty_count = 0
            for piece in row:
                if piece == '':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += piece
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        
        piece_placement = '/'.join(fen_rows)
        
        # Simplified FEN (just piece placement and active color)
        fen = f"{piece_placement} {active_color} - - 0 1"
        return fen
    
    def add_frame_state(self, frame_index: int, timestamp: float, 
                       detections: Dict[str, Dict]) -> Optional[Dict]:
        """
        Add a new frame state and detect if a move occurred.
        Returns move info if a move was detected, None otherwise.
        """
        # Create board state from detections
        fen = self.detections_to_fen(detections, 'w' if self.current_board.turn == chess.WHITE else 'b')
        
        state = BoardState(
            frame_index=frame_index,
            timestamp=timestamp,
            pieces={k: self.piece_to_notation(v['color'], v['piece']) 
                   for k, v in detections.items() if 'piece' in v and 'color' in v},
            fen=fen,
            confidence=sum(d.get('confidence', 0) for d in detections.values()) / max(len(detections), 1)
        )
        
        self.history.append(state)
        
        # Check for stable state (same FEN across multiple frames)
        if len(self.history) >= 3:
            recent_fens = [s.fen for s in list(self.history)[-3:]]
            if len(set(recent_fens)) == 1:  # All same FEN
                if self.last_stable_state is None or self.last_stable_state.fen != state.fen:
                    # New stable state detected
                    move = self._detect_move_between_states(self.last_stable_state, state)
                    if move:
                        self.moves_detected.append(move)
                        self.last_stable_state = state
                        return move
                    self.last_stable_state = state
        
        return None
    
    def _detect_move_between_states(self, prev_state: Optional[BoardState], 
                                   curr_state: BoardState) -> Optional[Dict]:
        """
        Detect what move occurred between two board states.
        """
        if prev_state is None:
            return None
        
        try:
            # Try to create boards from FEN
            prev_board = chess.Board(prev_state.fen.split()[0] + " w - - 0 1")
            curr_board = chess.Board(curr_state.fen.split()[0] + " w - - 0 1")
            
            # Find differences
            differences = []
            for square in chess.SQUARES:
                sq_name = chess.square_name(square)
                prev_piece = prev_board.piece_at(square)
                curr_piece = curr_board.piece_at(square)
                
                if prev_piece != curr_piece:
                    differences.append({
                        'square': sq_name,
                        'before': prev_piece.symbol() if prev_piece else None,
                        'after': curr_piece.symbol() if curr_piece else None
                    })
            
            if len(differences) < 2:
                return None
            
            # Try to find legal move that results in current state
            for move in prev_board.legal_moves:
                test_board = prev_board.copy()
                test_board.push(move)
                
                # Check if this move leads to current state
                if self._boards_match(test_board, curr_board):
                    san = prev_board.san(move)
                    return {
                        'move_number': len(self.moves_detected) + 1,
                        'uci': move.uci(),
                        'san': san,
                        'fen_before': prev_state.fen,
                        'fen_after': curr_state.fen,
                        'frame_index': curr_state.frame_index,
                        'timestamp': curr_state.timestamp
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error detecting move: {e}")
            return None
    
    def _boards_match(self, board1: chess.Board, board2: chess.Board) -> bool:
        """Check if two boards have the same piece placement."""
        for square in chess.SQUARES:
            if board1.piece_at(square) != board2.piece_at(square):
                return False
        return True
    
    def get_pgn(self, headers: Optional[Dict] = None) -> str:
        """Generate PGN from detected moves."""
        game = chess.pgn.Game()
        
        if headers:
            for key, value in headers.items():
                game.headers[key] = value
        
        node = game
        board = chess.Board()
        
        for move_info in self.moves_detected:
            try:
                move = chess.Move.from_uci(move_info['uci'])
                if move in board.legal_moves:
                    node = node.add_variation(move)
                    board.push(move)
                else:
                    logger.warning(f"Illegal move detected: {move_info['uci']}")
            except Exception as e:
                logger.error(f"Error adding move to PGN: {e}")
        
        # Set result
        if board.is_checkmate():
            result = "0-1" if board.turn == chess.WHITE else "1-0"
        elif board.is_stalemate() or board.is_insufficient_material():
            result = "1/2-1/2"
        else:
            result = "*"
        
        game.headers["Result"] = result
        
        return str(game)

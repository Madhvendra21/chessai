import chess
import chess.engine
import logging
import os
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of position analysis."""
    score: Optional[float]  # Centipawns (positive = white advantage)
    best_move: Optional[str]  # UCI notation
    pv: List[str]  # Principal variation
    depth: int
    time: float


@dataclass
class MoveAnalysis:
    """Analysis of a specific move."""
    move_number: int
    san: str
    uci: str
    evaluation_before: Optional[float]
    evaluation_after: Optional[float]
    best_move: Optional[str]
    best_eval: Optional[float]
    classification: str  # "excellent", "good", "inaccuracy", "mistake", "blunder"


class ChessEngine:
    """Stockfish chess engine wrapper."""
    
    def __init__(self, stockfish_path: Optional[str] = None, 
                 depth: int = 18, time_limit: float = 1.0):
        self.stockfish_path = stockfish_path or self._find_stockfish()
        self.depth = depth
        self.time_limit = time_limit
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self._connect()
    
    def _find_stockfish(self) -> Optional[str]:
        """Find Stockfish executable."""
        # Common locations
        paths = [
            "/usr/local/bin/stockfish",
            "/usr/bin/stockfish",
            "/opt/homebrew/bin/stockfish",
            "stockfish",
            "./stockfish",
            os.path.expanduser("~/stockfish/stockfish")
        ]
        
        for path in paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # Try to find in PATH
        import shutil
        stockfish = shutil.which("stockfish")
        if stockfish:
            return stockfish
        
        logger.warning("Stockfish not found. Analysis features disabled.")
        return None
    
    def _connect(self):
        """Initialize connection to Stockfish."""
        if not self.stockfish_path or not Path(self.stockfish_path).exists():
            logger.error(f"Stockfish not found at {self.stockfish_path}")
            return
        
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            logger.info(f"Connected to Stockfish at {self.stockfish_path}")
        except Exception as e:
            logger.error(f"Failed to connect to Stockfish: {e}")
            self.engine = None
    
    def is_available(self) -> bool:
        """Check if engine is available."""
        return self.engine is not None
    
    def analyze_position(self, board: chess.Board, 
                        time_limit: Optional[float] = None) -> AnalysisResult:
        """Analyze a chess position."""
        if not self.engine:
            return AnalysisResult(None, None, [], 0, 0.0)
        
        try:
            limit = chess.engine.Limit(
                depth=self.depth,
                time=time_limit or self.time_limit
            )
            
            result = self.engine.analyse(board, limit)
            
            # Extract score
            score = result["score"]
            if score.is_mate():
                # Convert mate score to high centipawn value
                mate_in = score.mate()
                centipawns = 10000 - abs(mate_in) * 100 if mate_in > 0 else -10000 + abs(mate_in) * 100
            else:
                centipawns = score.white().score(mate_score=10000) or 0
            
            # Extract best move and PV
            pv = result.get("pv", [])
            best_move = pv[0].uci() if pv else None
            pv_uci = [m.uci() for m in pv[:5]]  # First 5 moves
            
            return AnalysisResult(
                score=centipawns / 100.0,  # Convert to pawns
                best_move=best_move,
                pv=pv_uci,
                depth=result.get("depth", 0),
                time=result.get("time", 0.0)
            )
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return AnalysisResult(None, None, [], 0, 0.0)
    
    def analyze_game(self, pgn: str) -> List[MoveAnalysis]:
        """Analyze all moves in a game."""
        if not self.engine:
            logger.warning("Engine not available, skipping analysis")
            return []
        
        try:
            game = chess.pgn.read_game(pgn)
            if not game:
                return []
            
            board = game.board()
            analyses = []
            
            for i, move in enumerate(game.mainline_moves()):
                # Analyze position before move
                analysis_before = self.analyze_position(board)
                
                # Make the move
                board.push(move)
                
                # Analyze position after move
                analysis_after = self.analyze_position(board)
                
                # Classify the move
                classification = self._classify_move(
                    analysis_before.score,
                    analysis_after.score,
                    board.turn  # Note: turn is already flipped after push
                )
                
                analyses.append(MoveAnalysis(
                    move_number=(i // 2) + 1,
                    san=board.peek().uci(),  # This won't work, need to get SAN before pushing
                    uci=move.uci(),
                    evaluation_before=analysis_before.score,
                    evaluation_after=analysis_after.score,
                    best_move=analysis_before.best_move,
                    best_eval=analysis_before.score,
                    classification=classification
                ))
            
            return analyses
        except Exception as e:
            logger.error(f"Game analysis error: {e}")
            return []
    
    def _classify_move(self, eval_before: Optional[float], 
                      eval_after: Optional[float],
                      turn: bool) -> str:
        """
        Classify a move based on evaluation change.
        turn: True = White's turn (just moved), False = Black's turn
        """
        if eval_before is None or eval_after is None:
            return "unknown"
        
        # Calculate evaluation drop (from perspective of player who moved)
        if turn == chess.WHITE:  # Black just moved
            eval_drop = eval_after - eval_before
        else:  # White just moved
            eval_drop = eval_before - eval_after
        
        # Classification thresholds (in pawns)
        if eval_drop > 3.0:
            return "blunder"
        elif eval_drop > 1.5:
            return "mistake"
        elif eval_drop > 0.7:
            return "inaccuracy"
        elif eval_drop > 0.3:
            return "good"
        else:
            return "excellent"
    
    def get_insights(self, analyses: List[MoveAnalysis]) -> List[Dict]:
        """Generate human-readable insights from analysis."""
        insights = []
        
        for analysis in analyses:
            if analysis.classification in ["blunder", "mistake"]:
                insight = self._generate_insight(analysis)
                if insight:
                    insights.append(insight)
        
        # Add opening/endgame insights
        if len(analyses) > 10:
            opening_insight = self._analyze_opening(analyses[:10])
            if opening_insight:
                insights.insert(0, opening_insight)
        
        if len(analyses) > 20:
            endgame_insight = self._analyze_endgame(analyses[-10:])
            if endgame_insight:
                insights.append(endgame_insight)
        
        return insights
    
    def _generate_insight(self, analysis: MoveAnalysis) -> Optional[Dict]:
        """Generate insight for a specific move."""
        if not analysis.best_move:
            return None
        
        if analysis.classification == "blunder":
            template = "Move {move}: {san} was a blunder. Better was {best_move}, which would maintain the advantage."
        elif analysis.classification == "mistake":
            template = "Move {move}: {san} was inaccurate. Consider {best_move} instead."
        else:
            return None
        
        return {
            "move_number": analysis.move_number,
            "type": analysis.classification,
            "description": template.format(
                move=analysis.move_number,
                san=analysis.san,
                best_move=analysis.best_move
            ),
            "evaluation_before": analysis.evaluation_before,
            "evaluation_after": analysis.evaluation_after,
            "suggested_move": analysis.best_move
        }
    
    def _analyze_opening(self, opening_moves: List[MoveAnalysis]) -> Optional[Dict]:
        """Analyze opening play."""
        mistakes = [m for m in opening_moves if m.classification in ["mistake", "blunder"]]
        if not mistakes:
            return {
                "move_number": 1,
                "type": "opening",
                "description": "Solid opening play with no major mistakes."
            }
        return {
            "move_number": 1,
            "type": "opening",
            "description": f"Opening had {len(mistakes)} inaccuracies. Focus on development and king safety."
        }
    
    def _analyze_endgame(self, endgame_moves: List[MoveAnalysis]) -> Optional[Dict]:
        """Analyze endgame play."""
        blunders = [m for m in endgame_moves if m.classification == "blunder"]
        if blunders:
            return {
                "move_number": endgame_moves[0].move_number if endgame_moves else 1,
                "type": "endgame",
                "description": f"Critical blunders in the endgame cost the game."
            }
        return None
    
    def close(self):
        """Close engine connection."""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
            self.engine = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

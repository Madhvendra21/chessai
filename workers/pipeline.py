import logging
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_processor import VideoDownloader, FrameExtractor
from core.pipeline import ChessVisionPipeline
from core.chess_engine import ChessEngine
from core.config import settings

logger = logging.getLogger(__name__)


class PipelineWorker:
    """Worker for processing chess video jobs."""
    
    def __init__(self):
        self.downloader = VideoDownloader(settings.UPLOAD_DIR)
        self.frame_extractor = FrameExtractor(
            settings.FRAMES_DIR, 
            settings.FRAME_EXTRACTION_FPS
        )
        self.engine = ChessEngine(
            settings.STOCKFISH_PATH,
            settings.STOCKFISH_DEPTH,
            settings.STOCKFISH_TIME
        )
    
    async def process_job(self, job_id: str, url: str, db_session, update_progress):
        """Process a complete video analysis job."""
        try:
            # Stage 1: Download video
            await update_progress("downloading", 0, "Downloading video...")
            video_path = await self.downloader.download_from_url(url, job_id)
            
            if not video_path:
                raise Exception("Failed to download video")
            
            await update_progress("downloading", 100, "Download complete")
            
            # Get video info
            video_info = self.downloader.get_video_info(video_path)
            
            # Stage 2: Extract frames
            await update_progress("processing", 0, "Extracting frames...")
            
            def frame_progress(current, total):
                pct = int((current / total) * 30)  # First 30% is frame extraction
                
            frame_paths = self.frame_extractor.extract_frames(
                video_path, job_id, frame_progress
            )
            
            await update_progress("processing", 30, "Frames extracted")
            
            # Stage 3: Process frames
            await update_progress("processing", 30, "Analyzing board positions...")
            
            def pipeline_progress(stage, pct):
                overall = 30 + int(pct * 0.4)  # 30-70% is CV processing
                
            pipeline = ChessVisionPipeline(
                progress_callback=pipeline_progress
            )
            
            result = pipeline.process_video(video_path, 
                                           str(Path(settings.FRAMES_DIR) / job_id))
            
            await update_progress("processing", 70, "Board analysis complete")
            
            # Stage 4: Analyze with Stockfish
            await update_progress("analyzing", 0, "Running engine analysis...")
            
            if self.engine.is_available() and result['moves']:
                analyses = self.engine.analyze_game(result['pgn'])
                insights = self.engine.get_insights(analyses)
                
                # Update moves with analysis
                for i, move in enumerate(result['moves']):
                    if i < len(analyses):
                        move['evaluation'] = analyses[i].evaluation_after
                        move['best_move'] = analyses[i].best_move
                        move['is_blunder'] = analyses[i].classification == 'blunder'
                        move['is_mistake'] = analyses[i].classification in ['mistake', 'inaccuracy']
                
                result['insights'] = insights
                result['analysis'] = [
                    {
                        'move_number': a.move_number,
                        'san': a.san,
                        'evaluation': a.evaluation_after,
                        'best_move': a.best_move,
                        'classification': a.classification
                    }
                    for a in analyses
                ]
            else:
                result['insights'] = []
                result['analysis'] = []
            
            await update_progress("analyzing", 100, "Analysis complete")
            
            # Save results to database
            await self._save_results(job_id, result, video_info, db_session)
            
            # Cleanup frames
            self.frame_extractor.cleanup_frames(job_id)
            
            await update_progress("completed", 100, "Job complete")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error for job {job_id}: {e}")
            await update_progress("failed", 0, str(e))
            raise
    
    async def _save_results(self, job_id: str, result: dict, video_info, db_session):
        """Save processing results to database."""
        from db.models import Game, Move, AnalysisInsight, Job
        
        # Update job
        job = await db_session.get(Job, job_id)
        if job:
            job.title = video_info.title if video_info else "Unknown"
        
        # Create game record
        game = Game(
            job_id=job_id,
            pgn=result['pgn'],
            final_fen="",  # Extract from last move
            result="*",  # Determine from PGN
            total_moves=len(result['moves']),
            analysis_complete=bool(result.get('analysis'))
        )
        db_session.add(game)
        await db_session.flush()  # Get game.id
        
        # Create move records
        for i, move_data in enumerate(result['moves']):
            move = Move(
                game_id=game.id,
                move_number=i + 1,
                san=move_data['san'],
                uci=move_data['uci'],
                fen=move_data.get('fen_after', ''),
                evaluation=move_data.get('evaluation'),
                best_move=move_data.get('best_move'),
                is_blunder=move_data.get('is_blunder', False),
                is_mistake=move_data.get('is_mistake', False),
                time_in_video=move_data.get('timestamp')
            )
            db_session.add(move)
        
        # Create insight records
        for insight_data in result.get('insights', []):
            insight = AnalysisInsight(
                game_id=game.id,
                move_number=insight_data['move_number'],
                type=insight_data['type'],
                description=insight_data['description'],
                evaluation_before=insight_data.get('evaluation_before'),
                evaluation_after=insight_data.get('evaluation_after'),
                suggested_move=insight_data.get('suggested_move')
            )
            db_session.add(insight)
        
        await db_session.commit()

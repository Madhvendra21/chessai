import os
import sys
from pathlib import Path
from celery import Celery
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
backend_path = str(Path(__file__).parent.parent)
sys.path.insert(0, backend_path)

from core.config import settings
from db.database import AsyncSessionLocal
from db.models import Job, JobStatus

# Initialize Celery
celery_app = Celery(
    'chessvision',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.JOB_TIMEOUT,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def process_video_job(self, job_id: str, url: str):
    """Celery task to process a video job."""
    import asyncio
    
    async def run():
        from workers.pipeline import PipelineWorker
        
        worker = PipelineWorker()
        
        async with AsyncSessionLocal() as session:
            async def update_progress(stage: str, progress: int, message: str):
                """Update job progress in database."""
                job = await session.get(Job, job_id)
                if job:
                    job.status = getattr(JobStatus, stage.upper(), JobStatus.PROCESSING)
                    job.progress = progress
                    job.current_stage = message
                    await session.commit()
                
                # Update task state for real-time updates
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'stage': stage,
                        'progress': progress,
                        'message': message
                    }
                )
            
            try:
                result = await worker.process_job(job_id, url, session, update_progress)
                return {
                    'status': 'completed',
                    'job_id': job_id,
                    'total_moves': result['total_moves'],
                    'has_analysis': bool(result.get('analysis'))
                }
            except Exception as e:
                logger.error(f"Job {job_id} failed: {e}")
                
                # Update job status to failed
                job = await session.get(Job, job_id)
                if job:
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                    await session.commit()
                
                # Retry logic
                if self.request.retries < 3:
                    raise self.retry(countdown=60 * (self.request.retries + 1))
                
                raise
    
    return asyncio.run(run())


@celery_app.task
def cleanup_old_jobs(days: int = 7):
    """Cleanup old completed jobs."""
    import asyncio
    from datetime import datetime, timedelta
    
    async def run():
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select, delete
            from db.models import Job
            
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Delete old completed/failed jobs
            stmt = delete(Job).where(
                Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED]),
                Job.updated_at < cutoff
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            logger.info(f"Cleaned up {result.rowcount} old jobs")
            return {'deleted': result.rowcount}
    
    return asyncio.run(run())

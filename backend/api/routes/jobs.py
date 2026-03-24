import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import shutil
from pathlib import Path
import uuid

from db.database import get_db
from db.models import Job, JobStatus, VideoSource
from schemas.job import JobCreate, JobResponse
from workers.tasks import process_video_job
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=JobResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload a video file for processing."""
    # Validate file type
    allowed_types = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime']
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type. Allowed: {allowed_types}")
    
    # Create job
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        status=JobStatus.PENDING,
        source=VideoSource.UPLOAD,
        title=title or file.filename
    )
    db.add(job)
    await db.commit()
    
    # Save file
    file_path = Path(settings.UPLOAD_DIR) / f"{job_id}.mp4"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        job.status = JobStatus.FAILED
        job.error_message = "Failed to save uploaded file"
        await db.commit()
        raise HTTPException(500, "Failed to save file")
    
    job.video_path = str(file_path)
    await db.commit()
    
    # Start processing
    task = process_video_job.delay(job_id, str(file_path))
    
    logger.info(f"Created upload job {job_id}")
    return job


@router.post("/from-url", response_model=JobResponse)
async def create_job_from_url(
    background_tasks: BackgroundTasks,
    data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a job from a video URL (YouTube or direct)."""
    if not data.url:
        raise HTTPException(400, "URL is required")
    
    # Determine source type
    if "youtube.com" in data.url or "youtu.be" in data.url:
        source = VideoSource.YOUTUBE
    else:
        source = VideoSource.URL
    
    # Create job
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        status=JobStatus.PENDING,
        source=source,
        url=data.url,
        title=data.title or "Video from URL"
    )
    db.add(job)
    await db.commit()
    
    # Start processing
    task = process_video_job.delay(job_id, data.url)
    
    logger.info(f"Created URL job {job_id} from {data.url}")
    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get job status and details."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(404, "Job not found")
    
    return job


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List all jobs."""
    result = await db.execute(
        select(Job)
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    jobs = result.scalars().all()
    return jobs


@router.delete("/{job_id}")
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a job and its data."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(404, "Job not found")
    
    # Delete associated files
    if job.video_path and Path(job.video_path).exists():
        Path(job.video_path).unlink()
    
    # Delete frames
    frames_dir = Path(settings.FRAMES_DIR) / job_id
    if frames_dir.exists():
        import shutil
        shutil.rmtree(frames_dir)
    
    # Delete from database
    await db.delete(job)
    await db.commit()
    
    return {"message": "Job deleted"}

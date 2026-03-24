"""
Vercel serverless entry point for FastAPI backend.
This is a simplified version without Celery for serverless deployment.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import json
import tempfile
import shutil

# Mock database for serverless (in production use proper DB)
jobs_db = {}
games_db = {}

app = FastAPI(title="ChessVision AI API")

# CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobCreate(BaseModel):
    url: str
    title: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "ChessVision AI API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/jobs/from-url")
async def create_job_from_url(data: JobCreate):
    """Create a job from URL."""
    job_id = str(uuid.uuid4())
    
    job = {
        "id": job_id,
        "status": "pending",
        "url": data.url,
        "title": data.title or "Video Analysis",
        "progress": 0,
        "created_at": json.dumps({}),
    }
    
    jobs_db[job_id] = job
    
    # In production, trigger async processing here
    # For now return immediately
    return job


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status."""
    if job_id not in jobs_db:
        raise HTTPException(404, "Job not found")
    return jobs_db[job_id]


@app.get("/jobs/")
async def list_jobs():
    """List all jobs."""
    return list(jobs_db.values())


@app.get("/games/{game_id}")
async def get_game(game_id: str):
    """Get game by ID."""
    if game_id not in games_db:
        raise HTTPException(404, "Game not found")
    return games_db[game_id]


# Handler for Vercel serverless
handler = app
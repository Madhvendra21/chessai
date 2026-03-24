"""
Vercel Serverless Function Entry Point
Self-contained API without backend dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum
import uuid
from datetime import datetime

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo (use Redis in production)
jobs = {}

class JobCreate(BaseModel):
    url: str
    title: str = ""

class JobResponse(BaseModel):
    id: str
    status: str
    title: str
    created_at: str

@app.get("/")
def root():
    return {"message": "ChessVision API", "status": "active", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/jobs/from-url")
def create_job_from_url(job: JobCreate):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "title": job.title or "Untitled",
        "url": job.url,
        "created_at": datetime.now().isoformat()
    }
    return {"id": job_id, "status": "pending", "message": "Job created successfully"}

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/api/jobs")
def list_jobs():
    return list(jobs.values())

# Vercel serverless handler
mangum_handler = Mangum(app, lifespan="off")

def handler(request, context=None):
    """
    Vercel serverless function handler
    """
    return mangum_handler(request, context)
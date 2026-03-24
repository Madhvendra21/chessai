from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoSource(str, Enum):
    UPLOAD = "upload"
    YOUTUBE = "youtube"
    URL = "url"


class JobCreate(BaseModel):
    source: VideoSource
    url: Optional[str] = None
    title: Optional[str] = None


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    source: VideoSource
    title: Optional[str] = None
    video_path: Optional[str] = None
    progress: int = Field(0, ge=0, le=100)
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MoveData(BaseModel):
    move_number: int
    san: str
    uci: str
    fen: str
    evaluation: Optional[float] = None
    best_move: Optional[str] = None
    is_blunder: bool = False
    is_mistake: bool = False
    time_in_video: Optional[float] = None


class GameResult(BaseModel):
    id: str
    job_id: str
    pgn: str
    moves: List[MoveData]
    final_fen: str
    result: str
    white_player: Optional[str] = None
    black_player: Optional[str] = None
    event: Optional[str] = None
    date: Optional[str] = None
    total_moves: int
    analysis_complete: bool = False

    class Config:
        from_attributes = True


class AnalysisInsight(BaseModel):
    move_number: int
    type: str
    description: str
    evaluation_before: Optional[float] = None
    evaluation_after: Optional[float] = None
    suggested_move: Optional[str] = None


class GameAnalysis(BaseModel):
    game_id: str
    insights: List[AnalysisInsight]
    average_eval_white: Optional[float] = None
    average_eval_black: Optional[float] = None
    accuracy_white: Optional[float] = None
    accuracy_black: Optional[float] = None
    key_moments: List[Dict[str, Any]]

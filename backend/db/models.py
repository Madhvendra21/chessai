import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class JobStatus(enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoSource(enum.Enum):
    UPLOAD = "upload"
    YOUTUBE = "youtube"
    URL = "url"


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    source = Column(SQLEnum(VideoSource), nullable=False)
    url = Column(String(2048), nullable=True)
    title = Column(String(512), nullable=True)
    video_path = Column(String(1024), nullable=True)
    progress = Column(Integer, default=0)
    current_stage = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    game = relationship("Game", back_populates="job", uselist=False)


class Game(Base):
    __tablename__ = "games"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), unique=True, nullable=False)
    pgn = Column(Text, nullable=False)
    final_fen = Column(String(100), nullable=False)
    result = Column(String(20), nullable=False)
    white_player = Column(String(256), nullable=True)
    black_player = Column(String(256), nullable=True)
    event = Column(String(512), nullable=True)
    date = Column(String(20), nullable=True)
    total_moves = Column(Integer, default=0)
    analysis_complete = Column(Boolean, default=False)
    analysis_summary = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="game")
    moves = relationship("Move", back_populates="game", order_by="Move.move_number")


class Move(Base):
    __tablename__ = "moves"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String(36), ForeignKey("games.id"), nullable=False)
    move_number = Column(Integer, nullable=False)
    san = Column(String(20), nullable=False)
    uci = Column(String(10), nullable=False)
    fen = Column(String(100), nullable=False)
    evaluation = Column(Float, nullable=True)
    best_move = Column(String(10), nullable=True)
    is_blunder = Column(Boolean, default=False)
    is_mistake = Column(Boolean, default=False)
    is_inaccuracy = Column(Boolean, default=False)
    time_in_video = Column(Float, nullable=True)
    frame_index = Column(Integer, nullable=True)
    
    game = relationship("Game", back_populates="moves")


class AnalysisInsight(Base):
    __tablename__ = "analysis_insights"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String(36), ForeignKey("games.id"), nullable=False)
    move_number = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    evaluation_before = Column(Float, nullable=True)
    evaluation_after = Column(Float, nullable=True)
    suggested_move = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

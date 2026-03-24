import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.database import get_db
from db.models import Game, Move
from schemas.job import GameResult, MoveData

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{game_id}", response_model=GameResult)
async def get_game(game_id: str, db: AsyncSession = Depends(get_db)):
    """Get game by ID."""
    result = await db.execute(
        select(Game)
        .where(Game.id == game_id)
        .options(selectinload(Game.moves))
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(404, "Game not found")
    
    # Build response with moves
    moves_data = [
        MoveData(
            move_number=m.move_number,
            san=m.san,
            uci=m.uci,
            fen=m.fen,
            evaluation=m.evaluation,
            best_move=m.best_move,
            is_blunder=m.is_blunder,
            is_mistake=m.is_mistake,
            time_in_video=m.time_in_video
        )
        for m in game.moves
    ]
    
    return GameResult(
        id=game.id,
        job_id=game.job_id,
        pgn=game.pgn,
        moves=moves_data,
        final_fen=game.final_fen,
        result=game.result,
        white_player=game.white_player,
        black_player=game.black_player,
        event=game.event,
        date=game.date,
        total_moves=game.total_moves,
        analysis_complete=game.analysis_complete
    )


@router.get("/job/{job_id}", response_model=GameResult)
async def get_game_by_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get game by job ID."""
    result = await db.execute(
        select(Game)
        .where(Game.job_id == job_id)
        .options(selectinload(Game.moves))
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(404, "Game not found for this job")
    
    moves_data = [
        MoveData(
            move_number=m.move_number,
            san=m.san,
            uci=m.uci,
            fen=m.fen,
            evaluation=m.evaluation,
            best_move=m.best_move,
            is_blunder=m.is_blunder,
            is_mistake=m.is_mistake,
            time_in_video=m.time_in_video
        )
        for m in game.moves
    ]
    
    return GameResult(
        id=game.id,
        job_id=game.job_id,
        pgn=game.pgn,
        moves=moves_data,
        final_fen=game.final_fen,
        result=game.result,
        white_player=game.white_player,
        black_player=game.black_player,
        event=game.event,
        date=game.date,
        total_moves=game.total_moves,
        analysis_complete=game.analysis_complete
    )


@router.get("/", response_model=List[GameResult])
async def list_games(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List all games."""
    result = await db.execute(
        select(Game)
        .order_by(Game.created_at.desc())
        .offset(skip)
        .limit(limit)
        .options(selectinload(Game.moves))
    )
    games = result.scalars().all()
    
    return [
        GameResult(
            id=g.id,
            job_id=g.job_id,
            pgn=g.pgn,
            moves=[
                MoveData(
                    move_number=m.move_number,
                    san=m.san,
                    uci=m.uci,
                    fen=m.fen,
                    evaluation=m.evaluation,
                    best_move=m.best_move,
                    is_blunder=m.is_blunder,
                    is_mistake=m.is_mistake,
                    time_in_video=m.time_in_video
                )
                for m in g.moves
            ],
            final_fen=g.final_fen,
            result=g.result,
            white_player=g.white_player,
            black_player=g.black_player,
            event=g.event,
            date=g.date,
            total_moves=g.total_moves,
            analysis_complete=g.analysis_complete
        )
        for g in games
    ]

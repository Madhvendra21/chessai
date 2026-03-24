import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.database import get_db
from db.models import Game, AnalysisInsight
from schemas.job import AnalysisInsight as AnalysisInsightSchema, GameAnalysis

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/game/{game_id}/insights", response_model=List[AnalysisInsightSchema])
async def get_game_insights(game_id: str, db: AsyncSession = Depends(get_db)):
    """Get analysis insights for a game."""
    result = await db.execute(
        select(AnalysisInsight)
        .where(AnalysisInsight.game_id == game_id)
        .order_by(AnalysisInsight.move_number)
    )
    insights = result.scalars().all()
    
    return [
        AnalysisInsightSchema(
            move_number=i.move_number,
            type=i.type,
            description=i.description,
            evaluation_before=i.evaluation_before,
            evaluation_after=i.evaluation_after,
            suggested_move=i.suggested_move
        )
        for i in insights
    ]


@router.get("/game/{game_id}", response_model=GameAnalysis)
async def get_full_analysis(game_id: str, db: AsyncSession = Depends(get_db)):
    """Get complete analysis for a game."""
    result = await db.execute(
        select(Game)
        .where(Game.id == game_id)
        .options(selectinload(Game.moves))
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(404, "Game not found")
    
    # Get insights
    insights_result = await db.execute(
        select(AnalysisInsight)
        .where(AnalysisInsight.game_id == game_id)
        .order_by(AnalysisInsight.move_number)
    )
    insights = insights_result.scalars().all()
    
    # Calculate accuracy
    white_moves = [m for m in game.moves if m.move_number % 2 == 1]
    black_moves = [m for m in game.moves if m.move_number % 2 == 0]
    
    white_blunders = sum(1 for m in white_moves if m.is_blunder)
    black_blunders = sum(1 for m in black_moves if m.is_blunder)
    
    white_accuracy = max(0, 100 - (white_blunders * 20))
    black_accuracy = max(0, 100 - (black_blunders * 20))
    
    # Calculate average evaluations
    evals = [m.evaluation for m in game.moves if m.evaluation is not None]
    avg_eval = sum(evals) / len(evals) if evals else None
    
    return GameAnalysis(
        game_id=game_id,
        insights=[
            AnalysisInsightSchema(
                move_number=i.move_number,
                type=i.type,
                description=i.description,
                evaluation_before=i.evaluation_before,
                evaluation_after=i.evaluation_after,
                suggested_move=i.suggested_move
            )
            for i in insights
        ],
        average_eval_white=avg_eval,
        average_eval_black=avg_eval,
        accuracy_white=white_accuracy,
        accuracy_black=black_accuracy,
        key_moments=[
            {
                "move_number": i.move_number,
                "type": i.type,
                "description": i.description
            }
            for i in insights if i.type in ["blunder", "mistake"]
        ]
    )

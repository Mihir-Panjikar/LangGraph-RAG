from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict
from app.database import get_db
from app.repository import FeedbackRepository
from typing import Optional

router = APIRouter()

class FeedbackCreate(BaseModel):
    query_id: str
    rating: int = Field(..., ge=0, le=1, description="1 for thumbs up, 0 for thumbs down")
    comment: Optional[str] = None

class FeedbackResponse(FeedbackCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

@router.post("/feedback", response_model=FeedbackResponse)
async def post_feedback(feedback: FeedbackCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to submit user feedback for a specific query.
    """
    repo = FeedbackRepository(db)
    new_feedback = await repo.create_feedback(feedback.model_dump())
    return new_feedback

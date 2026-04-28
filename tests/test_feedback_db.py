import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import Feedback
from app.repository import FeedbackRepository

# Use a test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_feedback.db"

@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()
    if os.path.exists("./test_feedback.db"):
        os.remove("./test_feedback.db")

@pytest.mark.asyncio
async def test_create_feedback(db_session):
    repo = FeedbackRepository(db_session)
    feedback_data = {
        "query_id": "test-query-id",
        "rating": 1,
        "comment": "Great answer!"
    }
    
    feedback = await repo.create_feedback(feedback_data)
    
    assert feedback.id is not None
    assert feedback.query_id == "test-query-id"
    assert feedback.rating == 1
    assert feedback.comment == "Great answer!"

@pytest.mark.asyncio
async def test_get_feedback(db_session):
    repo = FeedbackRepository(db_session)
    feedback_data = {
        "query_id": "test-query-id-2",
        "rating": 0,
        "comment": "Needs improvement."
    }
    
    created = await repo.create_feedback(feedback_data)
    retrieved = await repo.get_feedback_by_query_id("test-query-id-2")
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.comment == "Needs improvement."

@pytest.mark.asyncio
async def test_get_db():
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        break

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Feedback

class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_feedback(self, feedback_data: dict) -> Feedback:
        feedback = Feedback(**feedback_data)
        self.session.add(feedback)
        await self.session.commit()
        await self.session.refresh(feedback)
        return feedback

    async def get_feedback_by_query_id(self, query_id: str) -> Feedback:
        result = await self.session.execute(
            select(Feedback).where(Feedback.query_id == query_id)
        )
        return result.scalars().first()

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.documents import router as documents_router
from app.api.query import router as query_router
from app.api.feedback import router as feedback_router
from app.database import engine, Base
from app.utils import rag_exception_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup on shutdown (if needed)

app = FastAPI(
    title="LangGraph RAG API",
    description="API for the self-corrective RAG system",
    version="0.1.0",
    lifespan=lifespan
)

app.add_exception_handler(Exception, rag_exception_handler)

app.include_router(documents_router)
app.include_router(query_router)
app.include_router(feedback_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the LangGraph RAG API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

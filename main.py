from fastapi import FastAPI
from app.api.documents import router as documents_router

app = FastAPI(
    title="LangGraph RAG API",
    description="API for the self-corrective RAG system",
    version="0.1.0"
)

app.include_router(documents_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the LangGraph RAG API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

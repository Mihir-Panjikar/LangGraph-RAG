from langchain_groq import ChatGroq
import os
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def get_llm(temperature: float = 0, model: str = "llama-3.3-70b-versatile"):
    """
    Centralized factory for LLM instances.
    """
    return ChatGroq(
        model=model,
        temperature=temperature,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

async def rag_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for RAG-related errors.
    """
    logger.error(f"Error processing request {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred while processing your RAG request. Please try again later."},
    )

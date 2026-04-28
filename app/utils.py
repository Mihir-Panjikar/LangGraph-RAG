from langchain_groq import ChatGroq
import os
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def get_llm(temperature: float = 0, model: str = "llama-3.3-70b-versatile", structured_output=None, **kwargs):
    """
    Centralized factory for LLM instances with fallbacks for rate limits.
    Uses only large models (non-slms) to ensure quality.
    """
    models = [
        model,
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    
    llms = [
        ChatGroq(
            model=m,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        ) for m in models
    ]
    
    if structured_output:
        llms = [l.with_structured_output(structured_output, **kwargs) for l in llms]
        
    primary_llm = llms[0]
    fallbacks = llms[1:]
    
    return primary_llm.with_fallbacks(fallbacks)

async def rag_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for RAG-related errors.
    """
    logger.error(f"Error processing request {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred while processing your RAG request. Please try again later."},
    )

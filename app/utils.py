from langchain_groq import ChatGroq
import os

def get_llm(temperature: float = 0, model: str = "llama-3.3-70b-versatile"):
    """
    Centralized factory for LLM instances.
    """
    return ChatGroq(
        model=model,
        temperature=temperature,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

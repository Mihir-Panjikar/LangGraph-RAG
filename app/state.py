from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict
from langchain_core.documents import Document

class GraphState(BaseModel):
    """
    Represents the state of the RAG graph.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_query: str = Field(..., description="The raw user input.")
    current_query: str = Field(None, description="The query currently being used for retrieval.")
    query_type: str = Field(default="general", description="The classification of the query (e.g., conceptual, how-to, API reference).")
    documents: List[Document] = Field(default_factory=list, description="The raw chunks retrieved from the vector store.")
    relevant_documents: List[Document] = Field(default_factory=list, description="The chunks that have passed the grading node.")
    retry_count: int = Field(default=0, description="Counter for tracking self-correction loops.")
    generation: str = Field(default="", description="The final generated answer.")

    @model_validator(mode="before")
    @classmethod
    def set_current_query(cls, data):
        """Set current_query to original_query if not provided."""
        if isinstance(data, dict):
            if "original_query" in data and ("current_query" not in data or data["current_query"] is None):
                data["current_query"] = data["original_query"]
        return data

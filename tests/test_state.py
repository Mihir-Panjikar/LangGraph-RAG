import pytest
from pydantic import ValidationError
from langchain_core.documents import Document
from app.state import GraphState

def test_graph_state_valid_initialization():
    """Test that GraphState can be initialized with valid data."""
    state = GraphState(
        original_query="What is LangGraph?",
        current_query="What is LangGraph?",
        documents=[Document(page_content="LangGraph is a library...")],
        relevant_documents=[],
        retry_count=0,
        generation=""
    )
    assert state.original_query == "What is LangGraph?"
    assert state.retry_count == 0
    assert len(state.documents) == 1

def test_graph_state_defaults():
    """Test that GraphState has correct defaults where applicable."""
    # Based on the spec, we might want some defaults, but let's see what's required.
    # For now, let's assume original_query is required.
    state = GraphState(original_query="test")
    assert state.current_query == "test"
    assert state.documents == []
    assert state.relevant_documents == []
    assert state.retry_count == 0
    assert state.generation == ""

def test_graph_state_type_validation():
    """Test that GraphState validates field types."""
    with pytest.raises(ValidationError):
        # retry_count should be an int
        GraphState(original_query="test", retry_count="not an int")

    with pytest.raises(ValidationError):
        # documents should be a list of Documents
        GraphState(original_query="test", documents=["not a document"])

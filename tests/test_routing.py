import pytest
from app.state import GraphState
from app.edges import decide_to_generate, check_retry_limit
from langchain_core.documents import Document

def test_decide_to_generate_with_relevant_docs():
    """Should route to 'generate' if relevant documents exist."""
    state = GraphState(
        original_query="test",
        relevant_documents=[Document(page_content="relevant info")]
    )
    result = decide_to_generate(state)
    assert result == "generate"

def test_decide_to_generate_without_relevant_docs():
    """Should route to 'transform_query' if no relevant documents exist."""
    state = GraphState(
        original_query="test",
        relevant_documents=[]
    )
    result = decide_to_generate(state)
    assert result == "transform_query"

def test_check_retry_limit_under_threshold():
    """Should route to 'retrieve' (via transform) if retry limit not reached."""
    # This logic might be slightly different depending on where it's called.
    # Usually, check_retry_limit is called before or after transform_query.
    state = GraphState(original_query="test", num_retries=2)
    result = check_retry_limit(state)
    assert result == "continue"

def test_check_retry_limit_at_threshold():
    """Should route to 'fallback' if retry limit reached."""
    state = GraphState(original_query="test", num_retries=3)
    result = check_retry_limit(state)
    assert result == "fallback"

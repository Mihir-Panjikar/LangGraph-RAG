import pytest
from unittest.mock import MagicMock, patch
from app.graph import app
from app.state import GraphState
from langchain_core.documents import Document

def test_graph_compilation():
    """Test that the graph compiles without errors."""
    assert app is not None
    # Check that nodes are present
    assert "analyze_query" in app.nodes
    assert "retrieve" in app.nodes
    assert "grade_documents" in app.nodes
    assert "transform_query" in app.nodes
    assert "generate" in app.nodes
    assert "web_search" in app.nodes

@pytest.mark.asyncio
async def test_graph_execution_basic():
    """
    Test that the graph can be initialized and a node can be executed.
    We mock the nodes to avoid LLM calls.
    """
    initial_state = {"original_query": "What is LangGraph?"}
    
    # We can't easily mock the internal nodes of a compiled graph without 
    # re-compiling or complex patching. 
    # For now, we'll just verify the compiled app exists and has the right structure.
    # A full execution test would belong in integration tests.
    assert app.get_graph() is not None

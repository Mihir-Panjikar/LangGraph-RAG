import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from app.state import GraphState
from app.nodes.retrieve import retrieve

def test_retrieve_node_updates_state():
    """Test that the retrieve node correctly populates the GraphState with documents."""
    # Mock data
    mock_docs = [
        Document(page_content="Test content 1", metadata={"source": "doc1.md"}),
        Document(page_content="Test content 2", metadata={"source": "doc2.md"}),
    ]
    
    # Mock the search_vector_store utility
    with patch("app.nodes.retrieve.search_vector_store") as mock_search:
        mock_search.return_value = mock_docs
        
        # Initial state
        state = GraphState(original_query="What is LangGraph?")
        
        # Run node
        new_state = retrieve(state)
        
        # Assertions
        assert "documents" in new_state
        assert len(new_state["documents"]) == 2
        assert new_state["documents"][0].page_content == "Test content 1"
        mock_search.assert_called_once_with("What is LangGraph?")

def test_retrieve_node_uses_current_query():
    """Test that the retrieve node uses current_query if it differs from original_query."""
    mock_docs = [Document(page_content="Rewritten result")]
    
    with patch("app.nodes.retrieve.search_vector_store") as mock_search:
        mock_search.return_value = mock_docs
        
        state = GraphState(
            original_query="initial",
            current_query="transformed query"
        )
        
        retrieve(state)
        
        # Should be called with current_query
        mock_search.assert_called_once_with("transformed query")

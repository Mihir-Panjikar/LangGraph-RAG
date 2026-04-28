import pytest
from unittest.mock import patch, MagicMock
from app.state import GraphState
from app.nodes.transform import transform_query

def test_transform_query_node_rewrites_query():
    """Test that the transform_query node optimizes the current_query."""
    state = GraphState(
        original_query="What is LangGraph?",
        current_query="What is LangGraph?"
    )
    
    with patch("app.nodes.transform.get_llm") as mock_get_llm, \
         patch("app.nodes.transform.ChatPromptTemplate") as mock_prompt_class:

        mock_llm = mock_get_llm.return_value

        mock_prompt = mock_prompt_class.from_messages.return_value
        
        mock_chain_1 = MagicMock()
        mock_prompt.__or__.return_value = mock_chain_1
        
        mock_chain_2 = MagicMock()
        mock_chain_1.__or__.return_value = mock_chain_2
        
        mock_chain_2.invoke.return_value = "Detailed explanation of LangGraph orchestration and state management"
        
        # Run node
        new_state = transform_query(state)
        
        # Assertions
        assert "current_query" in new_state
        assert new_state["current_query"] == "Detailed explanation of LangGraph orchestration and state management"
        assert mock_chain_2.invoke.call_count == 1

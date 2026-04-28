import pytest
from unittest.mock import patch, MagicMock
from app.state import GraphState
from app.nodes.analyze_query import analyze_query, QueryAnalysis

def test_analyze_query_node_rewrites_and_classifies():
    """Test that the analyze_query node correctly updates the state."""
    state = GraphState(original_query="how to install uv?")
    
    with patch("app.nodes.analyze_query.get_llm") as mock_get_llm, \
         patch("app.nodes.analyze_query.ChatPromptTemplate") as mock_prompt_class:
        
        mock_llm = mock_get_llm.return_value
        mock_analyzer = MagicMock()
        mock_llm.with_structured_output.return_value = mock_analyzer
        
        mock_prompt = mock_prompt_class.from_messages.return_value
        mock_chain = MagicMock()
        mock_prompt.__or__.return_value = mock_chain
        
        # Mock structured output
        mock_chain.invoke.return_value = QueryAnalysis(
            rewritten_query="installation guide for uv package manager",
            query_type="how-to"
        )
        
        # Run node
        new_state = analyze_query(state)
        
        # Assertions
        assert new_state["current_query"] == "installation guide for uv package manager"
        assert new_state["query_type"] == "how-to"
        assert mock_chain.invoke.call_count == 1

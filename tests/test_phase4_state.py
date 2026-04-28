import pytest
from pydantic import ValidationError
from app.state import GraphState

def test_graph_state_has_num_retries():
    """Test that GraphState has a num_retries field as per the new plan."""
    state = GraphState(original_query="test", num_retries=1)
    assert state.num_retries == 1

def test_graph_state_num_retries_default():
    """Test that num_retries defaults to 0."""
    state = GraphState(original_query="test")
    assert state.num_retries == 0

import pytest
from unittest.mock import MagicMock, patch
from app.state import GraphState
from app.nodes.web_search import web_search

@pytest.fixture
def mock_tavily_response():
    return {
        "query": "test query",
        "results": [
            {
                "title": "Result 1",
                "url": "https://example.com/1",
                "content": "Content of result 1"
            },
            {
                "title": "Result 2",
                "url": "https://example.com/2",
                "content": "Content of result 2"
            }
        ],
        "answer": "This is a synthesized answer from Tavily."
    }

@patch("app.nodes.web_search.TavilyClient")
@patch("os.getenv")
def test_web_search_node_success(mock_getenv, mock_tavily_class, mock_tavily_response):
    """Test that the web_search node correctly processes Tavily results."""
    # Setup mocks
    mock_getenv.return_value = "fake-key"
    mock_client = MagicMock()
    mock_tavily_class.return_value = mock_client
    mock_client.search.return_value = mock_tavily_response
    
    # Initial state
    state = GraphState(original_query="What is LangGraph?")
    
    # Execute node
    result = web_search(state)
    
    # Assertions
    assert "generation" in result
    assert "This is a synthesized answer from Tavily." in result["generation"]
    assert "https://example.com/1" in result["generation"]
    assert "https://example.com/2" in result["generation"]
    assert "WEB SEARCH FALLBACK" in result["generation"]
    
    assert "web_search_results" in result
    assert result["web_search_results"] == mock_tavily_response["answer"]

@patch("app.nodes.web_search.TavilyClient")
@patch("os.getenv")
def test_web_search_node_api_error(mock_getenv, mock_tavily_class):
    """Test that the web_search node handles API errors gracefully."""
    # Setup mocks
    mock_getenv.return_value = "fake-key"
    mock_client = MagicMock()
    mock_tavily_class.return_value = mock_client
    mock_client.search.side_effect = Exception("API Error")
    
    # Initial state
    state = GraphState(original_query="What is LangGraph?")
    
    # Execute node
    result = web_search(state)
    
    # Assertions
    assert "generation" in result
    assert "Error occurred during web search" in result["generation"]

@patch("app.nodes.web_search.TavilyClient")
@patch("os.getenv")
def test_web_search_node_missing_key(mock_getenv, mock_tavily_class):
    """Test that the web_search node handles missing API key."""
    # Setup mock to return None for TAVILY_API_KEY
    mock_getenv.return_value = None
    
    # Initial state
    state = GraphState(original_query="What is LangGraph?")
    
    # Execute node
    result = web_search(state)
    
    # Assertions
    assert "generation" in result
    assert "TAVILY_API_KEY not found" in result["generation"]

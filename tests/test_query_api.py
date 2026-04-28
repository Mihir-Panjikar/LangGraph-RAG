import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

def test_query_streaming_success():
    """
    Test that /query endpoint returns a streaming response.
    """
    # Mock the graph astream_events
    # We mock the internal graph instance in app.api.query
    with patch("app.api.query.graph.astream_events") as mock_stream:
        # Mocking an async generator
        async def mock_events(*args, **kwargs):
            yield {
                "event": "on_chat_model_stream",
                "name": "ChatGroq",
                "data": {"chunk": AsyncMock(content="Hello")},
                "metadata": {"langgraph_node": "generate"}
            }
            yield {
                "event": "on_chat_model_stream",
                "name": "ChatGroq",
                "data": {"chunk": AsyncMock(content=" world")},
                "metadata": {"langgraph_node": "generate"}
            }

        mock_stream.side_effect = mock_events

        with client.stream("POST", "/query", json={"query": "test query"}) as response:
            assert response.status_code == 200
            # Check if it's a streaming response
            chunks = list(response.iter_lines())
            assert len(chunks) > 0
            assert any("Hello" in chunk for chunk in chunks)
            assert any("world" in chunk for chunk in chunks)

def test_query_fallback_success():
    """
    Test that /query endpoint returns a response even if generate node is not hit (e.g. web_search fallback).
    """
    with patch("app.api.query.graph.astream_events") as mock_stream:
        async def mock_events(*args, **kwargs):
            # No on_chat_model_stream events
            yield {
                "event": "on_chain_end",
                "name": "web_search",
                "data": {"output": {"generation": "fallback message"}},
                "metadata": {"langgraph_node": "web_search"}
            }

        mock_stream.side_effect = mock_events

        with client.stream("POST", "/query", json={"query": "test query"}) as response:
            assert response.status_code == 200
            chunks = list(response.iter_lines())
            # Currently my implementation ONLY yields tokens from on_chat_model_stream
            # So this will fail (chunks will be empty)
            assert any("fallback message" in chunk for chunk in chunks)

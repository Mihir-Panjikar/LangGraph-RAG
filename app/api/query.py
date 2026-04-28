from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.graph import app as graph
import json
import asyncio

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

async def stream_tokens(query: str):
    """
    Generator that streams tokens from the LangGraph astream_events.
    """
    input_state = {"original_query": query}
    streamed_anything = False
    
    async for event in graph.astream_events(input_state, version="v2"):
        # 1. Stream tokens from the chat model
        if event["event"] == "on_chat_model_stream":
            if event.get("metadata", {}).get("langgraph_node") == "generate":
                chunk = event["data"].get("chunk")
                if chunk and hasattr(chunk, "content"):
                    if chunk.content:
                        streamed_anything = True
                        yield chunk.content
        
        # 2. Capture fallback or non-streaming node outputs
        # We look for on_chain_end of nodes like 'web_search' or 'generate'
        # specifically if they produce a 'generation' that wasn't streamed.
        elif event["event"] == "on_chain_end":
            node_name = event.get("metadata", {}).get("langgraph_node")
            if node_name in ["generate", "web_search"]:
                output = event["data"].get("output")
                if isinstance(output, dict) and "generation" in output:
                    gen = output["generation"]
                    if not streamed_anything and gen:
                        yield gen
                        streamed_anything = True

@router.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Endpoint to process a RAG query and stream the response.
    """
    return StreamingResponse(stream_tokens(request.query), media_type="text/plain")

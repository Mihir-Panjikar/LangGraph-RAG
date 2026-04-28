import os
from tavily import TavilyClient
from app.state import GraphState

def web_search(state: GraphState):
    """
    Fallback node that performs a web search using Tavily.

    Args:
        state (GraphState): The current graph state.

    Returns:
        dict: The synthesized answer and search results.
    """
    print("---WEB SEARCH FALLBACK---")
    query = state.current_query
    
    # Initialize Tavily client
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"generation": "Error: TAVILY_API_KEY not found in environment variables."}
    
    client = TavilyClient(api_key=api_key)
    
    try:
        # Perform search
        # include_answer=True gives us a synthesized answer
        response = client.search(query=query, search_depth="advanced", include_answer=True)
        
        answer = response.get("answer", "No synthesized answer available.")
        results = response.get("results", [])
        
        # Format sources
        sources = "\n".join([f"- {res['title']}: {res['url']}" for res in results[:3]])
        
        # Construct final generation
        disclaimer = "⚠️ **WEB SEARCH FALLBACK:** The following information was retrieved from the web as it was not found in the local documentation corpus."
        final_generation = f"{disclaimer}\n\n{answer}\n\n**Sources:**\n{sources}"
        
        return {
            "generation": final_generation,
            "web_search_results": answer
        }
    except Exception as e:
        print(f"Error during web search: {e}")
        return {"generation": f"Error occurred during web search: {str(e)}"}

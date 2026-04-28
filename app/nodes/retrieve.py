from app.ingestion import search_vector_store
from app.state import GraphState

def retrieve(state: GraphState):
    """
    Retrieve documents from the vector store based on the current query.

    Args:
        state (GraphState): The current graph state.

    Returns:
        dict: New documents to add to the state.
    """
    print("---RETRIEVING DOCUMENTS---")
    query = state.current_query
    
    # Search vector store
    documents = search_vector_store(query)
    
    return {"documents": documents}

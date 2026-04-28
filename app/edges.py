from app.state import GraphState

def decide_to_generate(state: GraphState) -> str:
    """
    Determines whether to generate an answer, or re-generate a query.

    Args:
        state (GraphState): The current graph state.

    Returns:
        str: Binary decision for next node to call.
    """
    print("---ASSESSING GRADED DOCUMENTS---")
    if not state.relevant_documents:
        # All documents have been filtered out
        # We will re-generate a new query
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"

def check_retry_limit(state: GraphState) -> str:
    """
    Checks if the retry limit has been reached.

    Args:
        state (GraphState): The current graph state.

    Returns:
        str: Decision whether to continue or fallback.
    """
    print("---CHECKING RETRY LIMIT---")
    if state.num_retries >= 3:
        print("---DECISION: RETRY LIMIT REACHED, FALLBACK---")
        return "fallback"
    else:
        print("---DECISION: CONTINUE RETRYING---")
        return "continue"

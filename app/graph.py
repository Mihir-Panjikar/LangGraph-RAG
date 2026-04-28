from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.nodes.analyze_query import analyze_query
from app.nodes.retrieve import retrieve
from app.nodes.grade import grade_documents
from app.nodes.transform import transform_query
from app.nodes.generate import generate
from app.nodes.web_search import web_search
from app.edges import decide_to_generate, check_retry_limit

def create_graph():
    """
    Compiles the LangGraph orchestration layer.
    """
    workflow = StateGraph(GraphState)

    # Define Nodes
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("transform_query", transform_query)
    workflow.add_node("generate", generate)
    workflow.add_node("web_search", web_search)

    # Build Graph
    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    # Conditional Edge: After grading, decide whether to generate or try transforming the query
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate"
        }
    )

    # Conditional Edge: After transforming the query, check if we should retry retrieval or fallback
    workflow.add_conditional_edges(
        "transform_query",
        check_retry_limit,
        {
            "continue": "retrieve",
            "fallback": "web_search"
        }
    )

    workflow.add_edge("generate", END)
    workflow.add_edge("web_search", END)

    return workflow.compile()

# Final graph instance
app = create_graph()

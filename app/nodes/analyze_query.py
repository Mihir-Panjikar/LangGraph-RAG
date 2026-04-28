from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.state import GraphState
from app.utils import get_llm

class QueryAnalysis(BaseModel):
    """Analysis of the user query for better retrieval."""
    rewritten_query: str = Field(description="The optimized version of the user question for vector search.")
    query_type: str = Field(description="Classification: conceptual, how-to, troubleshooting, or API reference.")

def analyze_query(state: GraphState):
    """
    Initial analysis of the raw question.
    """
    print("---ANALYZING INITIAL QUERY---")
    query = state.original_query

    structured_llm_analyzer = get_llm(temperature=0, structured_output=QueryAnalysis, method="json_mode")

    system = """You are a query analyzer for a technical documentation RAG system. \n
    Rewrite the question for vectorstore retrieval and classify it into: 'conceptual', 'how-to', 'troubleshooting', or 'API reference'. \n
    You MUST respond in JSON format with keys "rewritten_query" and "query_type"."""

    analysis_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "User question: {question}"),
        ]
    )

    analyzer_chain = analysis_prompt | structured_llm_analyzer
    res = analyzer_chain.invoke({"question": query})

    return {
        "current_query": res.rewritten_query,
        "query_type": res.query_type
    }

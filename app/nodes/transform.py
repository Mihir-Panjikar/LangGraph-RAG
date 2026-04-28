from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.state import GraphState

def transform_query(state: GraphState):
    """
    Transform the query to produce a better question for retrieval.

    Args:
        state (GraphState): The current graph state.

    Returns:
        dict: The transformed query.
    """
    print("---TRANSFORMING QUERY---")
    query = state.original_query

    # LLM
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    # Prompt
    system = """You are a query rewriter that converts an input question to a better version optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
    
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question.",
            ),
        ]
    )

    # Chain
    rewriter_chain = re_write_prompt | llm | StrOutputParser()

    # Run
    better_query = rewriter_chain.invoke({"question": query})
    
    return {"current_query": better_query}

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.state import GraphState
from app.utils import get_llm

def transform_query(state: GraphState):
    """
    Transform the query for a RE-RETRIEVAL attempt.
    """
    print("---TRANSFORMING QUERY FOR RETRY---")
    query = state.original_query
    query_type = state.query_type
    num_retries = state.num_retries

    llm = get_llm(temperature=0)

    system = f"""You are a query rewriter for a RAG system. The previous retrieval attempt for a '{query_type}' query failed. \n
    Formulate an improved version of the question that might find better results in the documentation. \n
    If it's 'conceptual', broaden the search. If it's 'API reference', ensure parameters are explicit."""

    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Initial question: {question}"),
        ]
    )

    rewriter_chain = re_write_prompt | llm | StrOutputParser()
    better_query = rewriter_chain.invoke({"question": query})

    return {"current_query": better_query, "num_retries": num_retries + 1}

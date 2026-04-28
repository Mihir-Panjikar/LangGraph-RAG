from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.state import GraphState
from app.utils import get_llm

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

def grade_documents(state: GraphState):
    """
    Determines whether the retrieved documents are relevant to the question.
    Uses parallel batching for efficiency.

    Args:
        state (GraphState): The current graph state.

    Returns:
        dict: Filtered relevant documents.
    """
    print("---CHECKING DOCUMENT RELEVANCE (BATCHED)---")
    query = state.current_query # Use optimized query for better matching
    documents = state.documents

    # LLM with structured output
    llm = get_llm(temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    # Prompt
    system = """You are a grader assessing relevance of a retrieved document to a user question. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )

    grader_chain = grade_prompt | structured_llm_grader

    # Prepare batch inputs
    inputs = [{"question": query, "document": d.page_content} for d in documents]
    
    # Run batch grading in parallel
    results = grader_chain.batch(inputs)

    relevant_docs = []
    for i, res in enumerate(results):
        if res.binary_score == "yes":
            print(f"---GRADE: DOCUMENT {i} RELEVANT---")
            relevant_docs.append(documents[i])
        else:
            print(f"---GRADE: DOCUMENT {i} NOT RELEVANT---")

    return {"relevant_documents": relevant_docs}

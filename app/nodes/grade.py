from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.state import GraphState

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

def grade_documents(state: GraphState):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (GraphState): The current graph state.

    Returns:
        dict: Filtered relevant documents.
    """
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    query = state.original_query
    documents = state.documents

    # LLM with structured output
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
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

    relevant_docs = []
    for d in documents:
        res = grader_chain.invoke({"question": query, "document": d.page_content})
        score = res.binary_score
        if score == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            relevant_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    
    return {"relevant_documents": relevant_docs}

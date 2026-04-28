from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.state import GraphState

def generate(state: GraphState):
    """
    Generate an answer using the retrieved relevant documents.

    Args:
        state (GraphState): The current graph state.

    Returns:
        dict: The generated answer.
    """
    print("---GENERATING ANSWER---")
    query = state.original_query
    documents = state.relevant_documents

    # LLM
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    # Prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a technical documentation assistant. Answer the user question strictly using the provided context. \n"
                       "Every claim must be supported by a citation in the format (Source: <source_name>). \n"
                       "If you cannot find the answer in the context, state that you do not know. \n\n"
                       "Context: \n {context}"),
            ("human", "{question}"),
        ]
    )

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Format context
    context = "\n\n".join([f"Content: {d.page_content}\nSource: {d.metadata.get('source', 'unknown')}" for d in documents])

    # Run
    generation = rag_chain.invoke({"context": context, "question": query})
    
    return {"generation": generation}

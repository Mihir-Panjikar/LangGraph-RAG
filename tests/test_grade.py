import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from app.state import GraphState
from app.nodes.grade import grade_documents

def test_grade_documents_filters_irrelevant():
    """Test that the grader filters out irrelevant documents and keeps relevant ones."""
    # Mock documents
    doc1 = Document(page_content="LangGraph is for building stateful agents.", metadata={"source": "lg.md"})
    doc2 = Document(page_content="The weather in London is rainy.", metadata={"source": "weather.txt"})
    
    state = GraphState(
        original_query="What is LangGraph?",
        documents=[doc1, doc2]
    )
    
    # Mock the chain
    with patch("app.nodes.grade.ChatGroq") as mock_llm_class, \
         patch("app.nodes.grade.ChatPromptTemplate") as mock_prompt_class:
        
        mock_llm = mock_llm_class.return_value
        mock_grader = MagicMock()
        mock_llm.with_structured_output.return_value = mock_grader
        
        mock_prompt = mock_prompt_class.from_messages.return_value
        
        # Mock the pipe operator: prompt | structured_llm
        # In the code: grader_chain = grade_prompt | structured_llm_grader
        mock_chain = MagicMock()
        mock_prompt.__or__.return_value = mock_chain
        
        # Return actual GradeDocuments instances
        from app.nodes.grade import GradeDocuments
        mock_chain.invoke.side_effect = [
            GradeDocuments(binary_score="yes"),
            GradeDocuments(binary_score="no")
        ]
        
        # Run node
        new_state = grade_documents(state)
        
        # Assertions
        assert len(new_state["relevant_documents"]) == 1
        assert new_state["relevant_documents"][0].page_content == "LangGraph is for building stateful agents."
        assert mock_chain.invoke.call_count == 2

def test_grade_documents_all_irrelevant():
    """Test behavior when no documents are relevant."""
    doc = Document(page_content="Irrelevant info")
    state = GraphState(original_query="Relevant query", documents=[doc])
    
    with patch("app.nodes.grade.ChatGroq") as mock_llm_class, \
         patch("app.nodes.grade.ChatPromptTemplate") as mock_prompt_class:
        
        mock_llm = mock_llm_class.return_value
        mock_grader = MagicMock()
        mock_llm.with_structured_output.return_value = mock_grader
        
        mock_prompt = mock_prompt_class.from_messages.return_value
        mock_chain = MagicMock()
        mock_prompt.__or__.return_value = mock_chain
        
        from app.nodes.grade import GradeDocuments
        mock_chain.invoke.return_value = GradeDocuments(binary_score="no")
        
        new_state = grade_documents(state)
        
        assert len(new_state["relevant_documents"]) == 0

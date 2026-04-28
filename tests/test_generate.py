import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from app.state import GraphState
from app.nodes.generate import generate

def test_generate_node_produces_answer():
    """Test that the generate node produces an answer grounded in documents."""
    doc1 = Document(page_content="LangGraph uses a state machine.", metadata={"source": "lg.md"})
    state = GraphState(
        original_query="How does LangGraph work?",
        relevant_documents=[doc1]
    )
    
    with patch("app.nodes.generate.ChatGroq") as mock_llm_class, \
         patch("app.nodes.generate.ChatPromptTemplate") as mock_prompt_class:
        
        mock_llm = mock_llm_class.return_value
        mock_prompt = mock_prompt_class.from_messages.return_value
        
        # Mock the chain: prompt | llm | StrOutputParser
        # This is a bit tricky to mock because of multiple | operators.
        # rag_chain = prompt | llm | StrOutputParser()
        
        mock_chain_1 = MagicMock() # prompt | llm
        mock_prompt.__or__.return_value = mock_chain_1
        
        mock_chain_2 = MagicMock() # (prompt | llm) | parser
        mock_chain_1.__or__.return_value = mock_chain_2
        
        # Mock the final invoke call
        mock_chain_2.invoke.return_value = "LangGraph works using a state machine (Source: lg.md)."
        
        # Run node
        new_state = generate(state)
        
        # Assertions
        assert "generation" in new_state
        assert "state machine" in new_state["generation"]
        assert mock_chain_2.invoke.call_count == 1
        
        # Check inputs to invoke
        args, _ = mock_chain_2.invoke.call_args
        context_arg = args[0]["context"]
        assert "LangGraph uses a state machine." in context_arg

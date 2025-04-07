# app/tests/test_decision_agent.py
import pytest
from unittest.mock import patch, MagicMock
from ..agents.decision_agent import create_decision_node, router

def test_router():
    """Test the router function."""
    # Test routing to weather
    state = {"decision": "weather"}
    assert router(state) == "weather"
    
    # Test routing to document
    state = {"decision": "document"}
    assert router(state) == "document"

@patch('langchain_openai.ChatOpenAI')
def test_create_decision_node(mock_chat_openai):
    """Test the decision node creation."""
    # Configure the mock
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm
    
    mock_response = MagicMock()
    mock_response.content = "Decision: weather\nCity: London\nReasoning: User asked about weather."
    mock_llm.invoke.return_value = mock_response
    
    # Create the decision node
    decide = create_decision_node()
    
    # Call the function with a test state
    state = {"query": "What's the weather in London?"}
    result = decide(state)
    
    # Verify the result
    assert result["decision"] == "weather"
    assert result["weather_city"] == "London"
    
    # Test with a document query
    mock_response.content = "Decision: document\nCity: none\nReasoning: User asked about PDF content."
    state = {"query": "What's in the document about climate change?"}
    result = decide(state)
    
    # Verify the result
    assert result["decision"] == "document"
    assert result["weather_city"] == ""
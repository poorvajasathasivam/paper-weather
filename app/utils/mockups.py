# app/utils/mockups.py
"""Mockup implementations for testing without API dependencies."""

from typing import Dict, Any
from langchain.schema import Document
from langchain.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import StrOutputParser

class MockEmbeddings:
    """Mock embedding model that returns random vectors."""
    
    def embed_documents(self, texts):
        """Return random embeddings for documents."""
        import random
        return [[random.random() for _ in range(10)] for _ in texts]
    
    def embed_query(self, text):
        """Return random embedding for query."""
        import random
        return [random.random() for _ in range(10)]

class MockRetriever(BaseRetriever):
    """Mock retriever that returns predefined documents."""
    
    def __init__(self):
        """Initialize with sample documents."""
        self.documents = [
            Document(page_content="Sample document 1", metadata={"source": "sample1"}),
            Document(page_content="Sample document 2", metadata={"source": "sample2"}),
            Document(page_content="Sample document 3", metadata={"source": "sample3"})
        ]
    
    def get_relevant_documents(self, query):
        """Return sample documents."""
        return self.documents

def create_mock_rag_chain():
    """Create a mock RAG chain for testing."""
    
    def get_answer(inputs):
        """Mock answer generation."""
        query = inputs["question"]
        context = "\n".join([doc.page_content for doc in inputs["context"]])
        return f"Mock answer to '{query}' based on context: {context}"
    
    # Create a simple chain
    retriever = MockRetriever()
    mock_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | get_answer
        | StrOutputParser()
    )
    
    return mock_chain

def get_mock_weather(city: str, api_key: str = "") -> str:
    """Return mock weather data."""
    return f"""
    Mock weather data for {city}:
    - Temperature: 22°C
    - Feels like: 24°C
    - Humidity: 45%
    - Conditions: Partly cloudy
    - Wind speed: 5 m/s
    """
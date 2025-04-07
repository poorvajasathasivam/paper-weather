from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
import os
import traceback
import importlib

# Try importing langsmith with a fallback
try:
    from langsmith import Client
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    
from ..utils.config import LANGCHAIN_PROJECT, OPENWEATHER_API_KEY, OPENAI_API_KEY
from ..utils.weather_api import get_weather
from ..utils.document_processor import DocumentProcessor
from ..models.llm import create_rag_chain, create_weather_chain
from .decision_agent import create_agent_graph, AgentState

# Check if we need mockups (for API problems)
USE_MOCKUPS = OPENAI_API_KEY == "" or "insufficient_quota" in os.environ.get("OPENAI_ERROR", "")

if USE_MOCKUPS:
    try:
        from ..utils.mockups import create_mock_rag_chain, get_mock_weather, MockRetriever
        MOCKUPS_AVAILABLE = True
    except ImportError:
        MOCKUPS_AVAILABLE = False
else:
    MOCKUPS_AVAILABLE = False

class Agent:
    """Main agent that coordinates the LangGraph workflow."""
    
    def __init__(self):
        """Initialize the agent components."""
        try:
            # Initialize the document processor
            self.doc_processor = DocumentProcessor()
            
            # Use mockups if needed
            if USE_MOCKUPS and MOCKUPS_AVAILABLE:
                print("Using mockups due to API limitations")
                self.vector_store = None
                self.retriever = MockRetriever()
                self.rag_chain = create_mock_rag_chain()
            else:
                # Get the vector store
                self.vector_store = self.doc_processor.get_vector_store()
                
                # Create the retriever
                self.retriever = self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                )
                
                # Create the RAG chain
                self.rag_chain = create_rag_chain(self.retriever)
                
        except Exception as e:
            print(f"Warning: Failed to initialize vector store: {e}. Will initialize on first document upload.")
            self.vector_store = None
            self.retriever = None
            self.rag_chain = None
            
            # Try using mockups as fallback
            if MOCKUPS_AVAILABLE:
                print("Using mockups as fallback")
                from ..utils.mockups import create_mock_rag_chain, MockRetriever
                self.retriever = MockRetriever()
                self.rag_chain = create_mock_rag_chain()
        
        # Create the weather chain
        self.weather_chain = create_weather_chain()
        
        # Create the agent graph
        self.graph = create_agent_graph()
        
        # Initialize conversation history
        self.conversation_history = []
        
    def process_weather(self, state: AgentState) -> AgentState:
        """Process weather request using actual weather API."""
        city = state["weather_city"]
        query = state["query"]
        
        if not city:
            state["weather_result"] = "I need a city name to provide weather information."
            return state
        
        try:
            # Get the weather data - use mockup if needed
            if USE_MOCKUPS and MOCKUPS_AVAILABLE:
                from ..utils.mockups import get_mock_weather
                weather_data = get_mock_weather(city)
            else:
                weather_data = get_weather(city, OPENWEATHER_API_KEY)
            
            # Process with the weather chain
            response = self.weather_chain.invoke({
                "weather_data": weather_data,
                "query": query
            })
            
            state["weather_result"] = response
        except Exception as e:
            state["weather_result"] = f"I couldn't get weather information for {city}. Error: {str(e)}"
        
        return state
    
    def process_document(self, state: AgentState) -> AgentState:
        """Process document search using RAG."""
        query = state["query"]
        
        if self.rag_chain is None:
            state["document_result"] = "No documents have been uploaded yet. Please upload a document first."
            return state
        
        # Get response from the RAG chain
        try:
            # Debug: Check what documents are retrieved
            retrieved_docs = self.retriever.get_relevant_documents(query)
            print(f"Retrieved {len(retrieved_docs)} documents")
            for i, doc in enumerate(retrieved_docs):
                print(f"Document {i+1}: {doc.page_content[:100]}...")
            
            # Use the RAG chain
            response = self.rag_chain.invoke(query)
            state["document_result"] = response
        except Exception as e:
            error_message = f"Error processing document query: {str(e)}"
            print(error_message)
            print(traceback.format_exc())
            state["document_result"] = error_message
        
        return state
    
    def generate_response(self, state: AgentState) -> AgentState:
        """Generate final response based on processing results."""
        if state["decision"] == "weather":
            state["final_response"] = state["weather_result"]
        else:
            state["final_response"] = state["document_result"]
        
        return state
    
    def update_graph(self):
        """Update the agent graph with actual implementations."""
        try:
            # Create a new graph with our custom implementations
            from .decision_agent import create_agent_graph
            self.graph = create_agent_graph(
                process_weather_fn=self.process_weather,
                process_document_fn=self.process_document,
                generate_response_fn=self.generate_response
            )
        except Exception as e:
            print(f"Warning: Could not update graph: {e}")
            print(traceback.format_exc())

    def query(self, user_input: str) -> str:
        """Process a user query through the agent."""
        try:
            # Debug logs
            print(f"Vector store initialized: {self.vector_store is not None}")
            print(f"Retriever initialized: {self.retriever is not None}")
            print(f"RAG chain initialized: {self.rag_chain is not None}")
            
            # Try to update the graph
            self.update_graph()
            
            # Add the user message to conversation history
            self.conversation_history.append(HumanMessage(content=user_input))
            
            # Create the initial state
            initial_state = AgentState(
                messages=self.conversation_history.copy(),
                query=user_input,
                decision="",
                weather_city="",
                weather_result="",
                document_result="",
                final_response=""
            )
            
            # Run the graph with LangSmith tracing if available
            try:
                if LANGSMITH_AVAILABLE and LANGCHAIN_PROJECT:
                    with Client().trace(
                        project_name=LANGCHAIN_PROJECT,
                        name="Agent Query"
                    ) as tracer:
                        result = self.graph.invoke(initial_state)
                else:
                    result = self.graph.invoke(initial_state)
            except Exception as e:
                print(f"Graph invocation error: {e}")
                print(traceback.format_exc())
                # If LangSmith tracing fails, run without it
                result = self.graph.invoke(initial_state)
            
            # Get the final response
            response = result["final_response"]
            
        except Exception as e:
            # If graph processing fails, fall back to a simpler implementation
            print(f"Graph processing failed: {e}")
            print(traceback.format_exc())
            
            # Simple decision logic
            if "weather" in user_input.lower() or "temperature" in user_input.lower() or "forecast" in user_input.lower():
                # Extract city name using a simple heuristic
                import re
                city_match = re.search(r"in\s+([A-Za-z\s]+)(?:\?|$)", user_input)
                city = city_match.group(1).strip() if city_match else "Unknown location"
                
                try:
                    # Use mockup if needed
                    if USE_MOCKUPS and MOCKUPS_AVAILABLE:
                        from ..utils.mockups import get_mock_weather
                        weather_data = get_mock_weather(city)
                    else:
                        weather_data = get_weather(city, OPENWEATHER_API_KEY)
                    response = f"Weather information for {city}:\n\n{weather_data}"
                except Exception as weather_e:
                    response = f"I couldn't get weather information for {city}. Error: {str(weather_e)}"
            else:
                # Document query
                if self.rag_chain is None:
                    response = "No documents have been uploaded yet. Please upload a document first."
                else:
                    try:
                        response = self.rag_chain.invoke(user_input)
                    except Exception as doc_e:
                        response = f"Error processing document query: {str(doc_e)}"
        
        # Add the AI message to conversation history
        self.conversation_history.append(AIMessage(content=response))
        
        return response
        
    def add_document_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add document text to the vector store."""
        try:
            if self.doc_processor is None:
                self.doc_processor = DocumentProcessor()
            
            # Use mockups if needed
            if USE_MOCKUPS and MOCKUPS_AVAILABLE:
                from ..utils.mockups import MockRetriever, create_mock_rag_chain
                self.retriever = MockRetriever()
                self.rag_chain = create_mock_rag_chain()
                return True
                
            # Process the text
            self.vector_store = self.doc_processor.process_text(text, metadata)
            
            # Update retriever and RAG chain
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            self.rag_chain = create_rag_chain(self.retriever)
            
            return True
        except Exception as e:
            print(f"Error adding document text: {e}")
            print(traceback.format_exc())
            
            # Use mockups as fallback
            if MOCKUPS_AVAILABLE:
                from ..utils.mockups import MockRetriever, create_mock_rag_chain
                self.retriever = MockRetriever()
                self.rag_chain = create_mock_rag_chain()
                return True
                
            return False
            
    def upload_pdf(self, pdf_path: str, file_name: str) -> bool:
        """Upload a PDF document to the vector store."""
        try:
            # Use mockups if needed
            if USE_MOCKUPS and MOCKUPS_AVAILABLE:
                from ..utils.mockups import MockRetriever, create_mock_rag_chain
                self.retriever = MockRetriever()
                self.rag_chain = create_mock_rag_chain()
                return True
                
            if self.doc_processor is None:
                self.doc_processor = DocumentProcessor()
                
            # Process and index the document
            chunks = self.doc_processor.load_pdf(pdf_path)
            
            # Store in vector store
            self.vector_store = self.doc_processor.store_documents(chunks)
            
            # Update retriever and RAG chain
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            self.rag_chain = create_rag_chain(self.retriever)
            
            # Delete temp file if needed
            if os.path.exists(pdf_path) and "temp" in pdf_path.lower():
                try:
                    os.unlink(pdf_path)
                except:
                    pass
                
            return True
        except Exception as e:
            print(f"Error uploading PDF: {e}")
            print(traceback.format_exc())
            
            # Use mockups as fallback
            if MOCKUPS_AVAILABLE:
                from ..utils.mockups import MockRetriever, create_mock_rag_chain
                self.retriever = MockRetriever()
                self.rag_chain = create_mock_rag_chain()
                return True
                
            return False
            
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []

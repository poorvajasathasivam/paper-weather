from typing import Literal, TypedDict, Annotated, Dict, Any, Callable, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from ..utils.config import OPENAI_API_KEY

# Define the states for our agent
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "Messages sent to the agent"]
    query: Annotated[str, "The user's original query"]
    decision: Annotated[str, "The decision on how to handle the query"]
    weather_city: Annotated[str, "City name for weather query if applicable"]
    weather_result: Annotated[str, "Result from the weather API if applicable"]
    document_result: Annotated[str, "Result from document search if applicable"]
    final_response: Annotated[str, "Final response to be sent back to the user"]

# Define the decision function to decide between weather and document
def create_decision_node():
    """Create a decision node that determines whether to use weather API or document search."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a decision-making assistant that determines how to handle user queries.
        
        Based on the user's input, decide whether:
        1. The query is asking for weather information (choose "weather")
        2. The query is asking for information from documents (choose "document")
        
        If it's a weather query, also extract the name of the city or location.
        
        Respond in the following format:
        Decision: [weather/document]
        City: [city name if applicable, otherwise "none"]
        Reasoning: [brief explanation of your decision]
        """),
        ("human", "{query}"),
    ])
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )
    
    chain = prompt | llm
    
    def decide(state: AgentState) -> AgentState:
        query = state["query"]
        response = chain.invoke({"query": query})
        response_text = response.content
        
        lines = response_text.strip().split("\n")
        decision = "document"  # Default
        city = "none"
        
        for line in lines:
            if line.startswith("Decision:"):
                decision_value = line.split(":", 1)[1].strip().lower()
                if decision_value == "weather":
                    decision = "weather"
            elif line.startswith("City:"):
                city = line.split(":", 1)[1].strip()
                if city.lower() == "none":
                    city = ""
        
        state["decision"] = decision
        state["weather_city"] = city
        return state
    
    return decide

# Define the weather processing function
def process_weather(state: AgentState) -> AgentState:
    """Process weather request in agent state."""
    state["weather_result"] = f"Weather data for {state['weather_city']} will be fetched."
    return state

# Define the document processing function
def process_document(state: AgentState) -> AgentState:
    """Process document search request in agent state."""
    state["document_result"] = "Document search results will go here."
    return state

# Define the response generation function
def generate_response(state: AgentState) -> AgentState:
    """Generate the final response based on the results."""
    if state["decision"] == "weather":
        state["final_response"] = f"Weather Response: {state['weather_result']}"
    else:
        state["final_response"] = f"Document Response: {state['document_result']}"
    return state

# Define the router function with the correct signature
def router(state: AgentState) -> str:
    """Route to the appropriate node based on the decision state field."""
    return state["decision"]

def create_agent_graph(
    process_weather_fn: Optional[Callable[[AgentState], AgentState]] = None,
    process_document_fn: Optional[Callable[[AgentState], AgentState]] = None,
    generate_response_fn: Optional[Callable[[AgentState], AgentState]] = None
):
    """
    Create the LangGraph for the agent with optional custom implementations.
    
    Args:
        process_weather_fn: Custom implementation for the weather processing node
        process_document_fn: Custom implementation for the document processing node
        generate_response_fn: Custom implementation for the response generation node
        
    Returns:
        Compiled StateGraph
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Use provided implementations or defaults
    _process_weather = process_weather_fn or process_weather
    _process_document = process_document_fn or process_document
    _generate_response = generate_response_fn or generate_response
    
    # Add nodes
    workflow.add_node("decide", create_decision_node())
    workflow.add_node("weather", _process_weather)
    workflow.add_node("document", _process_document)
    workflow.add_node("response", _generate_response)
    
    # Add edges
    workflow.add_edge(START, "decide")
    
    # Add conditional edges using strings for targets
    workflow.add_conditional_edges(
        "decide",
        router,
        {
            "weather": "weather",
            "document": "document"
        }
    )
    
    workflow.add_edge("weather", "response")
    workflow.add_edge("document", "response")
    workflow.add_edge("response", END)
    
    # Compile the graph
    return workflow.compile()
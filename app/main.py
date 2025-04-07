import os
import sys
import traceback

# Fix import path issues for standalone execution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.agents.agent import Agent
except ImportError:
    try:
        # Try relative import for running within the app directory
        from agents.agent import Agent
    except ImportError as e:
        print(f"Error importing Agent: {e}")
        print(f"sys.path: {sys.path}")
        
        # Define a mock Agent class for fallback
        class Agent:
            def __init__(self):
                self.conversation_history = []
                
            def query(self, text):
                return f"Mock response to: {text}"
                
            def upload_pdf(self, path, name):
                return True
                
            def add_document_text(self, text, metadata=None):
                return True
                
            def clear_conversation(self):
                self.conversation_history = []


class App:
    """Main application class that handles user queries and document uploads."""
    
    def __init__(self):
        """Initialize the application."""
        try:
            self.agent = Agent()
        except Exception as e:
            print(f"Error initializing agent: {e}")
            print(traceback.format_exc())
            raise
    
    def process_query(self, query: str) -> str:
        """
        Process a user query.
        
        Args:
            query: The user's query
            
        Returns:
            Response to the query
        """
        try:
            return self.agent.query(query)
        except Exception as e:
            error_message = f"Error processing query: {str(e)}"
            print(error_message)
            print(traceback.format_exc())
            return error_message
    
    def upload_pdf(self, pdf_path: str, file_name: str) -> bool:
        """
        Upload a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            file_name: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.agent.upload_pdf(pdf_path, file_name)
        except Exception as e:
            print(f"Error uploading PDF: {e}")
            print(traceback.format_exc())
            return False
    
    def add_text(self, text: str, source: str = "user_input") -> bool:
        """
        Add text directly to the document store.
        
        Args:
            text: Text content
            source: Source of the text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.agent.add_document_text(text, {"source": source})
        except Exception as e:
            print(f"Error adding text: {e}")
            print(traceback.format_exc())
            return False
    
    def clear_conversation(self):
        """Clear the conversation history."""
        try:
            self.agent.clear_conversation()
        except Exception as e:
            print(f"Error clearing conversation: {e}")
            print(traceback.format_exc())

def get_app():
    """
    Get the application instance.
    
    Returns:
        App instance
    """
    return App()

# For testing as standalone
if __name__ == "__main__":
    app = get_app()
    response = app.process_query("Hello, how are you?")
    print(f"Response: {response}")
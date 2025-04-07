import streamlit as st
import tempfile
import os
import sys
import traceback

st.set_page_config(
        page_title="PaperWeather",
        page_icon="🌤️",
        layout="wide"
    )

# Fix import path issues
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # app directory
project_root = os.path.dirname(parent_dir)  # project root

# Add paths to sys.path if not already there
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now try to import using absolute imports
try:
    # Try different import options
    from app.main import get_app
except ImportError as e1:
    try:
        # Try a different approach with project root on path
        sys.path.insert(0, project_root)
        from app.main import get_app
    except ImportError as e2:
        try:
            # Try direct import 
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
            from app.main import get_app
        except ImportError as e3:
            st.error(f"Error importing app: {str(e3)}")
            st.error(f"Current paths in sys.path: {sys.path}")
            
            # Create a simple mock app as fallback
            class MockApp:
                def process_query(self, query):
                    return f"Mock response to: {query}"
                
                def upload_pdf(self, *args, **kwargs):
                    return True
                    
                def clear_conversation(self):
                    pass
                
                def add_text(self, text, source="user_input"):
                    return True
            
            def get_app():
                return MockApp()

def main():
    # Initialize session state
    if "app" not in st.session_state:
        try:
            st.session_state.app = get_app()
            st.session_state.messages = []
        except Exception as e:
            st.error(f"Error initializing application: {str(e)}")
            st.code(traceback.format_exc())
            return
    
    # UI layout
    st.title("PaperWeather")
    st.subheader("Ask about weather or your documents")
    
    # Sidebar for uploads and settings
    with st.sidebar:
        st.header("Upload Documents")
        
        # PDF upload
        uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
        
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name
            
            if st.button("Process PDF Document"):
                with st.spinner("Processing document..."):
                    success = st.session_state.app.upload_pdf(temp_path, uploaded_file.name)
                
                if success:
                    st.success(f"Successfully processed {uploaded_file.name}")
                else:
                    st.error("Error processing document")
        
        # Text input for documents
        st.header("Or Add Text Directly")
        text_input = st.text_area("Enter document text")
        source_name = st.text_input("Source name (optional)", value="user_input")
        
        if st.button("Process Text as Document") and text_input:
            with st.spinner("Processing text..."):
                success = st.session_state.app.add_text(text_input, source_name)
            
            if success:
                st.success("Text processed successfully")
            else:
                st.error("Failed to process text")
        
        # Clear conversation button
        st.header("Conversation")
        if st.button("Clear Conversation"):
            st.session_state.app.clear_conversation()
            st.session_state.messages = []
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about weather or your documents"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from the agent
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.app.process_query(prompt)
            except Exception as e:
                response = f"Error: {str(e)}\n\n```\n{traceback.format_exc()}\n```"
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
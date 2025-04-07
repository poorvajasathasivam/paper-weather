# PaperWeather - Document Analysis and Weather Information

An AI assistant that combines document analysis and real-time weather data using LangChain, LangGraph, and Streamlit.

## Features

- **Dual Functionality**: Process both weather queries and document-based questions
- **Document Analysis**: Upload and analyze PDFs or text documents using RAG (Retrieval Augmented Generation)
- **Weather Information**: Get real-time weather data for any city
- **Agentic Decision-Making**: LangGraph workflow automatically routes queries to the right processing pipeline
- **Intuitive UI**: Clean Streamlit interface for easy interaction
- **Fallback Mode**: Works even without API keys using mockup implementations

## Architecture

The application is structured as a modular system:

1. **Decision Agent**: Analyzes queries and routes them to the appropriate processing pipeline
2. **RAG System**: Processes documents, stores them in a vector database, and retrieves relevant information
3. **Weather API**: Fetches real-time weather data for requested locations
4. **Response Generation**: Formats answers based on the processing results

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional - mockups work without it)
- OpenWeather API key (optional - mockups work without it)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/paper-weather.git
   cd paper-weather
   ```

2. Run the setup script to create directories and check dependencies:
   ```bash
   python setup.py
   ```

3. Edit the `.env` file created by the setup script:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   
   # Uncomment if you're having OpenAI API quota issues
   # OPENAI_ERROR=insufficient_quota
   ```

4. Run the application:
   ```bash
   python run_streamlit.py
   ```




## Usage

### Adding Documents

1. **Upload PDF**: Use the file uploader in the sidebar to add PDF documents
2. **Add Text**: Paste text directly into the text area and click "Process Text as Document"

### Asking Questions

- **Weather Queries**: "What's the weather like in New York?"
- **Document Questions**: "Summarize the key points in my document"

### Offline Mode

If you don't have API keys or are experiencing quota issues:
1. Set `OPENAI_ERROR=insufficient_quota` in the `.env` file
2. The system will use mockups to simulate responses

## Deployment

### Local Deployment

Run the application locally with:
```bash
python run_streamlit.py
```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Create a Streamlit Cloud account and connect your repository
3. Set the main file path to: `app/ui/streamlit_app.py`
4. Add `OPENAI_API_KEY` and `OPENWEATHER_API_KEY` as secrets
5. Deploy the app

## Dependencies

- langchain - Framework for LLM applications
- streamlit - Web interface
- langchain-openai - OpenAI integration
- langchain-qdrant - Vector store integration
- langgraph - Decision-making workflow
- python-dotenv - Environment variable management
- qdrant-client - Vector database client

## Troubleshooting

- **Import Errors**: Make sure all `__init__.py` files exist in the directory structure
- **API Errors**: Check your API keys in the `.env` file
- **Vector Store Errors**: Ensure the data directories exist and are writable

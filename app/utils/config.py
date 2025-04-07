
# app/utils/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# LangSmith Configuration
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "weather-rag-agent")

# Set up directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
PDF_DATA_PATH = os.path.join(DATA_DIR, "pdfs")
VECTOR_DB_PATH = os.path.join(DATA_DIR, "vector_db")

# Create directories if they don't exist
for directory in [DATA_DIR, DOCUMENTS_DIR, PDF_DATA_PATH, VECTOR_DB_PATH]:
    os.makedirs(directory, exist_ok=True)
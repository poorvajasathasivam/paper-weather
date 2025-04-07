import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant as QdrantVectorStore  # Corrected import
from qdrant_client import QdrantClient
from langchain.schema import Document
from .config import OPENAI_API_KEY, PDF_DATA_PATH, VECTOR_DB_PATH, DOCUMENTS_DIR
# from .sample_loader import get_sample_documents

class DocumentProcessor:
    """Process and store documents in vector database."""
    
    def __init__(self, collection_name: str = "pdf_documents"):
        """
        Initialize the document processor.
        
        Args:
            collection_name: Name of the vector database collection
        """
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.collection_name = collection_name
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        
        # Initialize Qdrant client
        os.makedirs(VECTOR_DB_PATH, exist_ok=True)
        self.client = QdrantClient(path=VECTOR_DB_PATH)
        
    def load_pdf(self, pdf_path: str) -> List:
        """
        Load and split a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of document chunks
        """
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return chunks
    
    def load_text_document(self, text_path: str) -> List:
        """
        Load and split a text document.
        
        Args:
            text_path: Path to the text file
            
        Returns:
            List of document chunks
        """
        loader = TextLoader(text_path)
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return chunks
        
    def load_all_documents(self) -> List:
        """
        Load all documents from the data directories.
        
        Returns:
            List of document chunks
        """
        all_chunks = []
        
        # Ensure directories exist
        os.makedirs(PDF_DATA_PATH, exist_ok=True)
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)
        
        # Load PDFs
        for filename in os.listdir(PDF_DATA_PATH):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(PDF_DATA_PATH, filename)
                chunks = self.load_pdf(pdf_path)
                all_chunks.extend(chunks)
        
        # Load text documents
        for filename in os.listdir(DOCUMENTS_DIR):
            if filename.endswith('.txt'):
                text_path = os.path.join(DOCUMENTS_DIR, filename)
                chunks = self.load_text_document(text_path)
                all_chunks.extend(chunks)
        
        # # If no documents found, use sample documents
        # if not all_chunks:
        #     print("No documents found. Using sample documents.")
        #     sample_docs = get_sample_documents()
        #     chunks = self.text_splitter.split_documents(sample_docs)
        #     all_chunks.extend(chunks)
            
        return all_chunks
    
    def process_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> QdrantVectorStore:
        """
        Process text and add it to the vector store.
        
        Args:
            text: Text content to process
            metadata: Metadata for the document
            
        Returns:
            QdrantVectorStore instance
        """
        if metadata is None:
            metadata = {"source": "user_input"}
        
        # Split the text into chunks
        doc = Document(page_content=text, metadata=metadata)
        chunks = self.text_splitter.split_documents([doc])
        
        try:
            # Try to get existing vector store
            vector_store = self.get_vector_store()
            
            # Add documents to the existing store
            vector_store.add_documents(chunks)
            return vector_store
        except Exception as e:
            print(f"Error adding to existing store: {e}")
            # If failed, create a new vector store
            return self._create_vector_store_from_docs(chunks)
    
    def _create_vector_store_from_docs(self, chunks: List[Document]) -> QdrantVectorStore:
        """
        Create a new vector store from document chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            QdrantVectorStore instance
        """
        # If chunks is empty, create a dummy document to initialize
        if not chunks:
            chunks = [Document(page_content="Initial document", metadata={"source": "init"})]
            
        # Create the vector store
        vector_store = QdrantVectorStore.from_documents(
            chunks,
            self.embeddings,
            url=None,  # Local storage
            client=self.client,
            collection_name=self.collection_name
        )
        
        return vector_store
    
    def store_documents(self, chunks: List = None) -> QdrantVectorStore:
        """
        Store document chunks in vector database.
        
        Args:
            chunks: List of document chunks. If None, all documents will be loaded.
            
        Returns:
            QdrantVectorStore instance
        """
        if chunks is None:
            chunks = self.load_all_documents()
        
        try:
            # Try to get existing vector store first
            vector_store = self.get_vector_store()
            
            # Add new documents to existing store
            if chunks:
                vector_store.add_documents(chunks)
            
            return vector_store
        except Exception as e:
            print(f"Creating new vector store: {e}")
            # Create new vector store
            return self._create_vector_store_from_docs(chunks)
    
    def get_vector_store(self) -> QdrantVectorStore:
        """
        Get the existing vector store or create a new one if it doesn't exist.
        
        Returns:
            QdrantVectorStore instance
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            
            if self.collection_name not in collection_names:
                raise ValueError(f"Collection {self.collection_name} does not exist.")
            
            # Collection exists, create vector store instance
            vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )
            
            return vector_store
        except Exception as e:
            print(f"Error getting vector store: {e}")
            # Create a new vector store with an initial document
            return self._create_vector_store_from_docs([])
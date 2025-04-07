# app/tests/test_document_processor.py
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from ..utils.document_processor import DocumentProcessor

@pytest.fixture
def sample_pdf_path():
    # Create a temporary PDF file for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_file.write(b"%PDF-1.7\nsample content")
        temp_path = temp_file.name
    
    yield temp_path
    
    # Clean up the temporary file
    if os.path.exists(temp_path):
        os.remove(temp_path)

@patch('langchain_community.document_loaders.PyPDFLoader.load')
def test_load_pdf(mock_load, sample_pdf_path):
    """Test PDF loading."""
    # Configure the mock
    mock_documents = [MagicMock(page_content="Test content")]
    mock_load.return_value = mock_documents
    
    # Create processor with mocked text_splitter
    processor = DocumentProcessor()
    processor.text_splitter = MagicMock()
    processor.text_splitter.split_documents.return_value = ["chunk1", "chunk2"]
    
    # Call the function
    result = processor.load_pdf(sample_pdf_path)
    
    # Verify the result
    assert result == ["chunk1", "chunk2"]
    mock_load.assert_called_once()
    processor.text_splitter.split_documents.assert_called_once_with(mock_documents)

@patch('os.listdir')
@patch('app.utils.document_processor.DocumentProcessor.load_pdf')
def test_load_all_pdfs(mock_load_pdf, mock_listdir):
    """Test loading all PDFs."""
    # Configure the mocks
    mock_listdir.return_value = ["doc1.pdf", "doc2.pdf", "not_a_pdf.txt"]
    mock_load_pdf.side_effect = [["chunk1", "chunk2"], ["chunk3"]]
    
    # Create processor
    processor = DocumentProcessor()
    
    # Call the function
    result = processor.load_all_pdfs()
    
    # Verify the result
    assert result == ["chunk1", "chunk2", "chunk3"]
    assert mock_load_pdf.call_count == 2
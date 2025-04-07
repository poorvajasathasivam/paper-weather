#!/usr/bin/env python3
"""
Setup script for Paper-Weather app.
This script installs dependencies and sets up the environment.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def create_env_file():
    """Create a .env file if it doesn't exist."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("Creating .env file with template values...")
        with open(env_path, "w") as f:
            f.write("""# API Keys
OPENAI_API_KEY=
OPENWEATHER_API_KEY=

# LangSmith Settings (optional)
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=paper-weather
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# If OpenAI API has quota issues, set this to use mockups
# OPENAI_ERROR=insufficient_quota
""")
        print("Created .env file. Please edit it to add your API keys.")
    else:
        print(".env file already exists.")

def check_dependencies():
    """Check for required Python packages."""
    required_packages = [
        "langchain", 
        "langchain-community",
        "langchain-openai",
        "langchain-core",
        "langchain-qdrant",
        "langgraph",
        "streamlit",
        "python-dotenv",
        "qdrant-client",
        "openai"
    ]
    
    # Check if packages are installed
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    return missing

def install_dependencies(missing_packages):
    """Install missing dependencies."""
    print(f"Installing {len(missing_packages)} missing packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies from requirements.txt.")
        
        # Try installing missing packages individually
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}")

def create_directories():
    """Create required directories."""
    directories = [
        "data",
        "data/pdfs",
        "data/documents",
        "data/vector_db"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Setup script for Paper-Weather app")
    parser.add_argument("--skip-install", action="store_true", help="Skip dependency installation")
    parser.add_argument("--run", action="store_true", help="Run the app after setup")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    print("Setting up Paper-Weather app...")
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check and install dependencies
    if not args.skip_install:
        missing_packages = check_dependencies()
        if missing_packages:
            install_dependencies(missing_packages)
        else:
            print("All dependencies are already installed.")
    
    # Create a sample text file in documents directory
    documents_dir = Path("data/documents")
    sample_file = documents_dir / "sample_document.txt"
    
    if not any(documents_dir.glob("*.*")):
        print("Creating a sample document...")
        with open(sample_file, "w") as f:
            f.write("""# Sample Document for Paper-Weather

This is a sample document that can be used to test the document processing functionality of the Paper-Weather application.

## Key Features
- Process documents and PDFs
- Query document content
- Get weather information

## Usage
You can upload your own documents through the Streamlit interface or add them to the data/documents directory.

## Additional Information
This sample document was created by the setup script to help you get started with the application.
""")
        print(f"Created sample document: {sample_file}")
    else:
        print("Documents already exist in data/documents directory.")
    
    print("\nSetup complete!")
    print("\nTo run the app, use the following command:")
    print("  python3 run_streamlit.py")
    
    # Run the app if requested
    if args.run:
        print("\nStarting the app...")
        subprocess.call([sys.executable, "run_streamlit.py"])

if __name__ == "__main__":
    main()
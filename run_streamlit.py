#!/usr/bin/env python3
"""
Startup script for running the Paper-Weather Streamlit app.
This script handles path setup and environment configuration.
"""

import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Run the Streamlit app with proper environment setup."""
    
    # Set the current working directory to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add the current directory to sys.path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Load environment variables
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        print("Loaded environment variables from .env file")
    else:
        print("No .env file found. API keys may be missing.")
    
    # Check for API keys and set mockup flag if needed
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        print("Warning: OPENAI_API_KEY not set. Using mockup implementations.")
        os.environ["OPENAI_ERROR"] = "insufficient_quota"
    
    # Get the path to the Streamlit app
    app_path = os.path.join(script_dir, "app", "ui", "streamlit_app.py")
    
    # Verify the app exists
    if not os.path.exists(app_path):
        print(f"Error: Could not find Streamlit app at {app_path}")
        sys.exit(1)
    
    # Run the Streamlit app using os.system to avoid path issues
    cmd = f"{sys.executable} -m streamlit run {app_path}"
    return os.system(cmd)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error starting the application: {e}")
        print(traceback.format_exc())
        sys.exit(1)
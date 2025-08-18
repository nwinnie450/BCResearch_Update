#!/bin/bash

echo "==============================================="
echo "  BlockChain Research AI Agent - Startup"
echo "==============================================="
echo

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    echo "Please make sure the virtual environment exists in the venv folder"
    echo "Run setup.sh first to create the environment"
    exit 1
fi

echo "Virtual environment activated successfully!"
echo

# Start the Streamlit application
echo "Starting Streamlit application..."
echo "Open your browser to http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application"
echo

streamlit run app.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Application failed to start"
    read -p "Press Enter to continue..."
fi
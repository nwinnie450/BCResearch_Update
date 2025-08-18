#!/bin/bash

echo "==============================================="
echo "  BlockChain Research AI Agent - Setup"
echo "==============================================="
echo

# Change to project directory
cd "$(dirname "$0")"

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

python3 --version
echo "Python found successfully!"
echo

echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old version..."
    rm -rf venv
fi

python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "Virtual environment created successfully!"
echo

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Make scripts executable
chmod +x run_app.sh setup.sh

echo
echo "==============================================="
echo "  SETUP COMPLETE!"
echo "==============================================="
echo
echo "Next steps:"
echo "1. (Optional) Configure API keys in .env file for enhanced accuracy"
echo "2. Run './run_app.sh' to start the application"
echo "3. Open http://localhost:8501 in your browser"
echo
echo "For API key setup, see API_KEYS_SETUP.md"
echo
read -p "Press Enter to continue..."
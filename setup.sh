#!/bin/bash
# Setup script for Banking Automation Agent

echo "=========================================="
echo "Banking Automation Agent - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install reportlab for PDF generation
echo ""
echo "Installing reportlab for PDF generation..."
pip install reportlab

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OpenAI API key!"
fi

# Create logs directory
mkdir -p logs

# Generate sample PDFs
echo ""
echo "Generating sample PDF documents..."
python create_sample_pdfs.py

# Initialize database
echo ""
echo "Initializing database..."
python -c "from src.database import get_db_manager; get_db_manager().init_db(); print('✓ Database initialized')"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the dashboard:"
echo "   streamlit run app.py"
echo "   OR run the pipeline:"
echo "   python pipeline.py"
echo ""
echo "For testing:"
echo "   pytest tests/ -v"
echo ""
echo "Enjoy using the Banking Automation Agent! 🏦"
echo ""

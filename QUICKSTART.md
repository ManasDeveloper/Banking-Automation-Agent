# Quick Start Guide

## Installation Steps

### 1. Activate Virtual Environment

**Important:** You need to activate the virtual environment in your terminal:

```bash
# Navigate to project directory
cd "/Users/manaskulkarni/Desktop/Resume projects/Banking workflow automation"

# Activate virtual environment
source venv/bin/activate

# You should see (venv) prefix in your terminal prompt
```

### 2. Verify Installation

```bash
# Check Python version
python --version

# Verify packages are installed
pip list

# You should see openai, streamlit, sqlalchemy, etc.
```

### 3. Generate Sample PDFs

```bash
# Install reportlab for PDF generation
pip install reportlab

# Generate sample banking documents
python create_sample_pdfs.py
```

### 4. Initialize Database

```bash
python -c "from src.database import get_db_manager; db = get_db_manager(); db.init_db(); print('✅ Database initialized')"
```

### 5. Test Email Loading

```bash
python -c "from src.email_processor import EmailProcessor; ep = EmailProcessor(); emails = ep.load_all_emails(); print(f'✅ Loaded {len(emails)} emails')"
```

### 6. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at http://localhost:8501

### 7. Or Run the Pipeline

```bash
python pipeline.py
```

This will process all emails through the complete workflow and save results to the database.

## Troubleshooting

### If imports fail:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
pip install reportlab
```

### If OpenAI API errors occur:

1. Check your .env file has the correct API key
2. Verify the key is valid and has credits
3. Test: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:20])"`

### Common Commands

```bash
# Activate venv (must do this in every new terminal)
source venv/bin/activate

# Run dashboard
streamlit run app.py

# Run pipeline
python pipeline.py

# Run tests
pytest tests/ -v

# Test individual modules
python src/email_processor.py
python src/ocr_engine.py

# Deactivate venv
deactivate
```

## What to Expect

1. **Dashboard**: Interactive UI to process emails, view classifications, and generate responses
2. **Pipeline**: Batch process all emails and store results in database
3. **Tests**: Verify all components work correctly

## Next Steps

1. Open .env and ensure your OpenAI API key is set
2. Activate the virtual environment: `source venv/bin/activate`
3. Run: `streamlit run app.py`
4. Click "Load Emails" in the sidebar
5. Click "Process All Emails"
6. View results in the dashboard!

## Notes

- **Always activate venv first**: `source venv/bin/activate`
- **Dashboard**: Best for interactive exploration
- **Pipeline**: Best for batch processing
- **Logs**: Check logs/ directory for debugging
- **Database**: banking_automation.db stores all results

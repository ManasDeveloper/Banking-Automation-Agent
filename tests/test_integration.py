"""
Integration tests for the complete email processing pipeline
"""
import pytest
from pathlib import Path
from src.email_processor import EmailProcessor
from src.ocr_engine import OCREngine
from src.classifier import IntentClassifier
from src.response_generator import ResponseGenerator
from src.database import get_db_manager


class TestEmailProcessingPipeline:
    """Integration tests for end-to-end email processing"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.email_processor = EmailProcessor()
        self.ocr_engine = OCREngine()
        self.classifier = IntentClassifier()
        self.response_generator = ResponseGenerator()
        self.db_manager = get_db_manager(":memory:")  # Use in-memory database for tests
        self.db_manager.init_db()

    def test_load_and_process_emails(self):
        """Test loading and basic processing of emails"""
        emails = self.email_processor.load_all_emails()
        assert len(emails) > 0, "Should load sample emails"

        # Test processing first email
        email = emails[0]
        assert 'email_id' in email
        assert 'subject' in email
        assert 'body' in email

        # Validate email structure
        is_valid, errors = self.email_processor.validate_email_structure(email)
        assert is_valid, f"Email should be valid, errors: {errors}"

    def test_email_to_database(self):
        """Test storing email in database"""
        emails = self.email_processor.load_all_emails()
        if not emails:
            pytest.skip("No emails available for testing")

        email = emails[0]

        # Create session and store email
        session = next(self.db_manager.get_session())
        try:
            # Prepare email data for database
            email_data = {
                'email_id': email['email_id'],
                'sender': email['sender'],
                'sender_name': email.get('sender_name', ''),
                'subject': email['subject'],
                'body': email['body'],
                'date': email['date'],
                'priority': email.get('priority', 'medium'),
                'requires_response': email.get('requires_response', True)
            }

            db_email = self.db_manager.create_email(session, email_data)
            assert db_email.id is not None
            assert db_email.email_id == email['email_id']

            # Retrieve email
            retrieved = self.db_manager.get_email_by_id(session, email['email_id'])
            assert retrieved is not None
            assert retrieved.subject == email['subject']

        finally:
            session.close()

    def test_complete_pipeline_without_llm(self):
        """Test complete pipeline without LLM calls (structure only)"""
        emails = self.email_processor.load_all_emails()
        if not emails:
            pytest.skip("No emails available for testing")

        email = emails[0]

        # Step 1: Validate email
        is_valid, errors = self.email_processor.validate_email_structure(email)
        assert is_valid

        # Step 2: Extract metadata
        metadata = self.email_processor.extract_metadata(email)
        assert metadata['email_id'] == email['email_id']

        # Step 3: Check for attachments
        attachments = email.get('attachments', [])
        if attachments:
            attachment_paths = self.email_processor.get_attachment_paths(email)
            assert isinstance(attachment_paths, list)

        # Step 4: Store in database
        session = next(self.db_manager.get_session())
        try:
            email_data = {
                'email_id': email['email_id'],
                'sender': email['sender'],
                'sender_name': email.get('sender_name', ''),
                'subject': email['subject'],
                'body': email['body'],
                'date': email['date'],
                'priority': email.get('priority', 'medium'),
                'requires_response': email.get('requires_response', True)
            }
            db_email = self.db_manager.create_email(session, email_data)
            assert db_email.id is not None

        finally:
            session.close()

    def test_ocr_processing(self):
        """Test OCR processing on sample PDFs if available"""
        pdf_dir = Path("data/sample_pdfs")
        if not pdf_dir.exists():
            pytest.skip("PDF directory not found")

        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files found")

        # Test processing first PDF
        pdf_file = pdf_files[0]
        result = self.ocr_engine.process_pdf(str(pdf_file))

        assert 'raw_text' in result
        assert 'structured_data' in result
        assert 'success' in result

        # Test structured data extraction
        structured = result['structured_data']
        assert 'account_numbers' in structured
        assert 'amounts' in structured
        assert 'dates' in structured

    def test_database_relationships(self):
        """Test database relationships between tables"""
        session = next(self.db_manager.get_session())
        try:
            # Create email
            email_data = {
                'email_id': 'test_rel_001',
                'sender': 'test@example.com',
                'sender_name': 'Test User',
                'subject': 'Test Subject',
                'body': 'Test body',
                'date': Path(__file__).stat().st_mtime,
                'priority': 'medium',
                'requires_response': True
            }
            from datetime import datetime
            email_data['date'] = datetime.now()

            db_email = self.db_manager.create_email(session, email_data)

            # Create classification
            classification_data = {
                'email_id': db_email.id,
                'intent': 'general_inquiry',
                'confidence': 0.85,
                'reasoning': 'Test reasoning'
            }
            classification = self.db_manager.create_classification(session, classification_data)
            assert classification.email_id == db_email.id

            # Create response
            response_data = {
                'email_id': db_email.id,
                'response_text': 'Test response',
                'template_used': 'general_inquiry'
            }
            response = self.db_manager.create_response(session, response_data)
            assert response.email_id == db_email.id

            # Create action
            action_data = {
                'email_id': db_email.id,
                'action_type': 'reply',
                'priority': 'medium',
                'reason': 'Test reason',
                'assigned_to': 'customer_support'
            }
            action = self.db_manager.create_action(session, action_data)
            assert action.email_id == db_email.id

            # Test retrieval through relationships
            retrieved_email = self.db_manager.get_email_by_id(session, 'test_rel_001')
            assert len(retrieved_email.classifications) == 1
            assert len(retrieved_email.responses) == 1
            assert len(retrieved_email.actions) == 1

        finally:
            session.close()

    def test_workflow_metrics(self):
        """Test workflow metrics and statistics"""
        emails = self.email_processor.load_all_emails()
        if not emails:
            pytest.skip("No emails available")

        # Count by priority
        priority_counts = {}
        for email in emails:
            priority = email.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        assert sum(priority_counts.values()) == len(emails)

        # Count emails with attachments
        with_attachments = sum(1 for email in emails if email.get('attachments'))
        assert with_attachments >= 0  # Should be non-negative

        # Validate all emails
        valid_count = 0
        for email in emails:
            is_valid, _ = self.email_processor.validate_email_structure(email)
            if is_valid:
                valid_count += 1

        # Most emails should be valid
        assert valid_count / len(emails) > 0.8  # At least 80% valid

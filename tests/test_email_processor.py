"""
Unit tests for email processor module
"""
import pytest
from pathlib import Path
from datetime import datetime
from src.email_processor import EmailProcessor


@pytest.fixture
def email_processor():
    """Create email processor instance"""
    return EmailProcessor("data/sample_emails")


@pytest.fixture
def sample_email():
    """Create sample email data"""
    return {
        'email_id': 'test_001',
        'sender': 'test@example.com',
        'sender_name': 'Test User',
        'subject': 'Test Email',
        'body': 'This is a test email body.',
        'date': datetime.now(),
        'priority': 'medium',
        'requires_response': True,
        'attachments': []
    }


class TestEmailProcessor:
    """Test cases for EmailProcessor class"""

    def test_initialization(self, email_processor):
        """Test email processor initialization"""
        assert email_processor is not None
        assert isinstance(email_processor.email_dir, Path)

    def test_validate_email_structure_valid(self, email_processor, sample_email):
        """Test email validation with valid email"""
        is_valid, errors = email_processor.validate_email_structure(sample_email)
        assert is_valid
        assert len(errors) == 0

    def test_validate_email_structure_missing_field(self, email_processor, sample_email):
        """Test email validation with missing field"""
        del sample_email['sender']
        is_valid, errors = email_processor.validate_email_structure(sample_email)
        assert not is_valid
        assert len(errors) > 0
        assert any('sender' in error.lower() for error in errors)

    def test_validate_email_structure_invalid_priority(self, email_processor, sample_email):
        """Test email validation with invalid priority"""
        sample_email['priority'] = 'invalid_priority'
        is_valid, errors = email_processor.validate_email_structure(sample_email)
        assert not is_valid
        assert any('priority' in error.lower() for error in errors)

    def test_extract_metadata(self, email_processor, sample_email):
        """Test metadata extraction"""
        metadata = email_processor.extract_metadata(sample_email)
        assert metadata['email_id'] == 'test_001'
        assert metadata['sender'] == 'test@example.com'
        assert metadata['has_attachments'] is False
        assert metadata['attachment_count'] == 0
        assert 'word_count' in metadata

    def test_extract_metadata_with_attachments(self, email_processor, sample_email):
        """Test metadata extraction with attachments"""
        sample_email['attachments'] = ['document1.pdf', 'document2.pdf']
        metadata = email_processor.extract_metadata(sample_email)
        assert metadata['has_attachments'] is True
        assert metadata['attachment_count'] == 2

    def test_format_email_for_display(self, email_processor, sample_email):
        """Test email formatting"""
        formatted = email_processor.format_email_for_display(sample_email)
        assert 'Test Email' in formatted
        assert 'test@example.com' in formatted
        assert 'This is a test email body' in formatted

    def test_get_attachment_paths(self, email_processor, sample_email):
        """Test attachment path resolution"""
        sample_email['attachments'] = ['nonexistent.pdf']
        paths = email_processor.get_attachment_paths(sample_email)
        # Should return empty list for non-existent files
        assert isinstance(paths, list)


def test_load_all_emails():
    """Integration test for loading all emails"""
    processor = EmailProcessor()
    emails = processor.load_all_emails()
    # Should load emails from sample data
    assert isinstance(emails, list)
    # Should have at least some emails
    if emails:
        assert 'email_id' in emails[0]
        assert 'subject' in emails[0]

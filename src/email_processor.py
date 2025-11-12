"""
Email Processor for loading and parsing mock email data.
Handles JSON email files and attachment processing.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailProcessor:
    """Process mock email data from JSON files"""

    def __init__(self, email_dir: str = "data/sample_emails"):
        """
        Initialize email processor.

        Args:
            email_dir: Directory containing email JSON files
        """
        self.email_dir = Path(email_dir)
        if not self.email_dir.exists():
            logger.warning(f"Email directory not found: {self.email_dir}")
        logger.info(f"Email processor initialized with directory: {self.email_dir}")

    def load_email(self, email_file: str) -> Optional[Dict[str, Any]]:
        """
        Load a single email from JSON file.

        Args:
            email_file: Path to email JSON file

        Returns:
            Email data as dictionary, or None if error
        """
        try:
            email_path = Path(email_file)
            if not email_path.exists():
                logger.error(f"Email file not found: {email_path}")
                return None

            with open(email_path, 'r', encoding='utf-8') as f:
                email_data = json.load(f)

            # Validate required fields
            required_fields = ['email_id', 'sender', 'subject', 'body', 'date']
            for field in required_fields:
                if field not in email_data:
                    logger.error(f"Missing required field '{field}' in {email_file}")
                    return None

            # Parse date string to datetime
            if isinstance(email_data['date'], str):
                email_data['date'] = datetime.fromisoformat(email_data['date'].replace('Z', '+00:00'))

            logger.info(f"Loaded email: {email_data['email_id']} - {email_data['subject']}")
            return email_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {email_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading email {email_file}: {e}")
            return None

    def load_all_emails(self) -> List[Dict[str, Any]]:
        """
        Load all emails from the email directory.

        Returns:
            List of email dictionaries
        """
        if not self.email_dir.exists():
            logger.error(f"Email directory does not exist: {self.email_dir}")
            return []

        emails = []
        email_files = sorted(self.email_dir.glob("email_*.json"))

        logger.info(f"Found {len(email_files)} email files")

        for email_file in email_files:
            email_data = self.load_email(str(email_file))
            if email_data:
                emails.append(email_data)

        logger.info(f"Successfully loaded {len(emails)} emails")
        return emails

    def get_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific email by its ID.

        Args:
            email_id: Email ID to search for

        Returns:
            Email data dictionary or None if not found
        """
        all_emails = self.load_all_emails()
        for email in all_emails:
            if email['email_id'] == email_id:
                return email
        logger.warning(f"Email not found: {email_id}")
        return None

    def get_emails_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """
        Get emails filtered by priority level.

        Args:
            priority: Priority level (critical, high, medium, low)

        Returns:
            List of matching emails
        """
        all_emails = self.load_all_emails()
        filtered = [email for email in all_emails if email.get('priority') == priority]
        logger.info(f"Found {len(filtered)} emails with priority: {priority}")
        return filtered

    def get_emails_with_attachments(self) -> List[Dict[str, Any]]:
        """
        Get emails that have attachments.

        Returns:
            List of emails with attachments
        """
        all_emails = self.load_all_emails()
        filtered = [email for email in all_emails
                   if email.get('attachments') and len(email['attachments']) > 0]
        logger.info(f"Found {len(filtered)} emails with attachments")
        return filtered

    def validate_email_structure(self, email_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate email data structure.

        Args:
            email_data: Email dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        required_fields = {
            'email_id': str,
            'sender': str,
            'subject': str,
            'body': str,
            'date': (str, datetime),
        }

        for field, expected_type in required_fields.items():
            if field not in email_data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(email_data[field], expected_type):
                errors.append(f"Invalid type for {field}: expected {expected_type}, got {type(email_data[field])}")

        # Optional fields with type checking
        optional_fields = {
            'sender_name': str,
            'priority': str,
            'requires_response': bool,
            'attachments': list,
        }

        for field, expected_type in optional_fields.items():
            if field in email_data and not isinstance(email_data[field], expected_type):
                errors.append(f"Invalid type for {field}: expected {expected_type}, got {type(email_data[field])}")

        # Validate priority values
        if 'priority' in email_data:
            valid_priorities = ['critical', 'high', 'medium', 'low']
            if email_data['priority'] not in valid_priorities:
                errors.append(f"Invalid priority value: {email_data['priority']}. Must be one of {valid_priorities}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def extract_metadata(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from email.

        Args:
            email_data: Email dictionary

        Returns:
            Dictionary with extracted metadata
        """
        metadata = {
            'email_id': email_data.get('email_id'),
            'sender': email_data.get('sender'),
            'sender_name': email_data.get('sender_name', ''),
            'subject': email_data.get('subject'),
            'date': email_data.get('date'),
            'priority': email_data.get('priority', 'medium'),
            'requires_response': email_data.get('requires_response', True),
            'has_attachments': bool(email_data.get('attachments')),
            'attachment_count': len(email_data.get('attachments', [])),
            'body_length': len(email_data.get('body', '')),
            'word_count': len(email_data.get('body', '').split()),
        }
        return metadata

    def format_email_for_display(self, email_data: Dict[str, Any]) -> str:
        """
        Format email data for display.

        Args:
            email_data: Email dictionary

        Returns:
            Formatted string representation
        """
        date_str = email_data['date'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(email_data['date'], datetime) else email_data['date']

        output = f"""
{'=' * 70}
Email ID: {email_data['email_id']}
From: {email_data.get('sender_name', '')} <{email_data['sender']}>
Subject: {email_data['subject']}
Date: {date_str}
Priority: {email_data.get('priority', 'N/A')}
Attachments: {', '.join(email_data.get('attachments', [])) or 'None'}
{'=' * 70}

{email_data['body']}

{'=' * 70}
"""
        return output

    def get_attachment_paths(self, email_data: Dict[str, Any], attachment_dir: str = "data/sample_pdfs") -> List[str]:
        """
        Get full paths to attachment files.

        Args:
            email_data: Email dictionary
            attachment_dir: Directory containing attachments

        Returns:
            List of attachment file paths
        """
        attachments = email_data.get('attachments', [])
        attachment_dir_path = Path(attachment_dir)

        paths = []
        for attachment in attachments:
            attachment_path = attachment_dir_path / attachment
            if attachment_path.exists():
                paths.append(str(attachment_path))
            else:
                logger.warning(f"Attachment not found: {attachment_path}")

        return paths

    def get_processing_queue(self, sort_by_priority: bool = True) -> List[Dict[str, Any]]:
        """
        Get email processing queue.

        Args:
            sort_by_priority: Whether to sort by priority (critical first)

        Returns:
            List of emails in processing order
        """
        emails = self.load_all_emails()

        if sort_by_priority:
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            emails.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 2))

        logger.info(f"Processing queue prepared with {len(emails)} emails")
        return emails


def test_email_processor():
    """Test email processor functionality"""
    processor = EmailProcessor()

    print("\n=== Testing Email Processor ===\n")

    # Test loading all emails
    print("1. Loading all emails...")
    emails = processor.load_all_emails()
    print(f"   Loaded {len(emails)} emails\n")

    # Test loading specific email
    print("2. Loading specific email (email_001)...")
    email = processor.get_email_by_id("001")
    if email:
        print(f"   Subject: {email['subject']}")
        print(f"   From: {email['sender']}\n")

    # Test priority filtering
    print("3. High priority emails...")
    high_priority = processor.get_emails_by_priority("high")
    print(f"   Found {len(high_priority)} high priority emails\n")

    # Test emails with attachments
    print("4. Emails with attachments...")
    with_attachments = processor.get_emails_with_attachments()
    print(f"   Found {len(with_attachments)} emails with attachments\n")

    # Test email validation
    if emails:
        print("5. Validating first email...")
        is_valid, errors = processor.validate_email_structure(emails[0])
        print(f"   Valid: {is_valid}")
        if errors:
            print(f"   Errors: {errors}\n")
        else:
            print()

    # Test metadata extraction
    if emails:
        print("6. Extracting metadata from first email...")
        metadata = processor.extract_metadata(emails[0])
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        print()

    # Test processing queue
    print("7. Getting processing queue...")
    queue = processor.get_processing_queue(sort_by_priority=True)
    print("   Priority order:")
    for email in queue[:5]:  # Show first 5
        print(f"   - [{email.get('priority', 'N/A')}] {email['subject']}")


if __name__ == "__main__":
    test_email_processor()

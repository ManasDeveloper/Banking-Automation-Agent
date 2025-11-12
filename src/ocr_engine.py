"""
OCR Engine for extracting text and structured data from PDF documents.
Uses pdfplumber for text extraction and pytesseract as fallback for images.
"""
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from typing import Dict, Any, Optional, List
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """Extract text and structured data from PDF documents"""

    def __init__(self):
        """Initialize OCR engine"""
        self.account_number_pattern = re.compile(r'(ACC|BUS-ACC)-\d{4}-\d{4}')
        self.amount_pattern = re.compile(r'\$[\d,]+\.?\d*')
        self.date_pattern = re.compile(
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|'
            r'\d{1,2}/\d{1,2}/\d{4}|'
            r'\d{4}-\d{2}-\d{2}'
        )
        self.phone_pattern = re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}')
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        logger.info("OCR Engine initialized")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber.
        Falls back to OCR if no text found.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return ""

            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            # If no text extracted, try OCR
            if not text.strip():
                logger.info(f"No text found via pdfplumber, attempting OCR for: {pdf_path}")
                text = self._ocr_from_pdf_images(str(pdf_path))

            logger.info(f"Extracted {len(text)} characters from {pdf_path.name}")
            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""

    def _ocr_from_pdf_images(self, pdf_path: str) -> str:
        """
        Convert PDF to images and perform OCR using pytesseract.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text from OCR
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            text = ""

            for i, image in enumerate(images):
                logger.info(f"Performing OCR on page {i + 1}/{len(images)}")
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"

            return text.strip()

        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return ""

    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from text using regex patterns.

        Args:
            text: Raw text from document

        Returns:
            Dictionary with extracted structured data
        """
        structured_data = {
            'account_numbers': [],
            'amounts': [],
            'dates': [],
            'phone_numbers': [],
            'emails': [],
        }

        try:
            # Extract account numbers
            account_matches = self.account_number_pattern.findall(text)
            structured_data['account_numbers'] = list(set(account_matches))

            # Extract amounts
            amount_matches = self.amount_pattern.findall(text)
            structured_data['amounts'] = [self._parse_amount(amt) for amt in amount_matches]

            # Extract dates
            date_matches = self.date_pattern.findall(text)
            structured_data['dates'] = list(set(date_matches))

            # Extract phone numbers
            phone_matches = self.phone_pattern.findall(text)
            structured_data['phone_numbers'] = list(set(phone_matches))

            # Extract email addresses
            email_matches = self.email_pattern.findall(text)
            structured_data['emails'] = list(set(email_matches))

            # Extract names (simple heuristic - capitalized words, 2-3 words)
            structured_data['names'] = self._extract_names(text)

            logger.info(f"Extracted structured data: {len(structured_data['account_numbers'])} accounts, "
                       f"{len(structured_data['amounts'])} amounts, {len(structured_data['dates'])} dates")

        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")

        return structured_data

    def _parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float.

        Args:
            amount_str: Amount string (e.g., "$1,234.56")

        Returns:
            Float value
        """
        try:
            # Remove $ and commas
            cleaned = amount_str.replace('$', '').replace(',', '')
            return float(cleaned)
        except ValueError:
            return 0.0

    def _extract_names(self, text: str) -> List[str]:
        """
        Extract potential person names from text.
        Simple heuristic: 2-3 consecutive capitalized words.

        Args:
            text: Text to search

        Returns:
            List of potential names
        """
        # Pattern for capitalized words (potential names)
        name_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b')
        names = name_pattern.findall(text)

        # Filter out common false positives
        false_positives = {
            'Account Number', 'Business Name', 'Loan Amount', 'Annual Income',
            'Credit Score', 'Date Birth', 'Phone Number', 'Email Address',
            'Net Profit', 'Total Revenue', 'Account Holder', 'Primary Account',
            'Secondary Account', 'Business Information', 'Loan Request',
            'Financial Summary', 'Supporting Documents', 'New Address',
            'Previous Address', 'Effective Date', 'Employment Update',
            'Return Date', 'Transaction Date', 'Credit Card'
        }

        filtered_names = [name for name in names if name not in false_positives]
        return list(set(filtered_names))

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Complete processing of PDF: extract text and structured data.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with raw text and structured data
        """
        logger.info(f"Processing PDF: {pdf_path}")

        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)

        # Extract structured data
        structured_data = self.extract_structured_data(raw_text)

        result = {
            'pdf_path': pdf_path,
            'raw_text': raw_text,
            'structured_data': structured_data,
            'success': bool(raw_text),
            'character_count': len(raw_text)
        }

        logger.info(f"PDF processing {'successful' if result['success'] else 'failed'} for {pdf_path}")
        return result

    def extract_key_fields(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract key banking fields from text.

        Args:
            text: Raw text from document

        Returns:
            Dictionary with key fields
        """
        fields = {
            'account_number': None,
            'amount': None,
            'date': None,
            'name': None,
            'address': None
        }

        try:
            # Get account number (first occurrence)
            account_matches = self.account_number_pattern.findall(text)
            if account_matches:
                fields['account_number'] = account_matches[0]

            # Get amount (highest amount found)
            amount_matches = self.amount_pattern.findall(text)
            if amount_matches:
                amounts = [self._parse_amount(amt) for amt in amount_matches]
                fields['amount'] = max(amounts)

            # Get date (first occurrence)
            date_matches = self.date_pattern.findall(text)
            if date_matches:
                fields['date'] = date_matches[0]

            # Get name (first person name found)
            names = self._extract_names(text)
            if names:
                fields['name'] = names[0]

            # Extract address (simple heuristic - line with street number and name)
            address_pattern = re.compile(r'\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,?\s+(?:Street|Avenue|Road|Boulevard|Lane|Drive|Apt|Suite))')
            address_matches = address_pattern.findall(text)
            if address_matches:
                fields['address'] = address_matches[0]

        except Exception as e:
            logger.error(f"Error extracting key fields: {e}")

        return fields


def test_ocr_engine():
    """Test OCR engine functionality"""
    import os

    ocr = OCREngine()
    pdf_dir = Path("data/sample_pdfs")

    if not pdf_dir.exists():
        print("PDF directory not found. Please run create_sample_pdfs.py first.")
        return

    print("\n=== Testing OCR Engine ===\n")

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in data/sample_pdfs/")
        return

    for pdf_file in pdf_files[:3]:  # Test first 3 PDFs
        print(f"\nProcessing: {pdf_file.name}")
        print("-" * 50)

        result = ocr.process_pdf(str(pdf_file))

        print(f"Success: {result['success']}")
        print(f"Characters extracted: {result['character_count']}")
        print(f"\nStructured Data:")
        for key, value in result['structured_data'].items():
            print(f"  {key}: {value}")

        print(f"\nKey Fields:")
        key_fields = ocr.extract_key_fields(result['raw_text'])
        for key, value in key_fields.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    test_ocr_engine()

"""
Complete email processing pipeline script.
Run this to process all emails through the entire workflow.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
import json

from src.email_processor import EmailProcessor
from src.ocr_engine import OCREngine
from src.classifier import IntentClassifier
from src.response_generator import ResponseGenerator
from src.database import get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailProcessingPipeline:
    """Complete email processing pipeline"""

    def __init__(self):
        """Initialize all components"""
        logger.info("Initializing email processing pipeline...")

        self.email_processor = EmailProcessor()
        self.ocr_engine = OCREngine()
        self.classifier = IntentClassifier()
        self.response_generator = ResponseGenerator()
        self.db_manager = get_db_manager()

        # Initialize database
        self.db_manager.init_db()

        logger.info("Pipeline initialized successfully")

    def process_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single email through the complete pipeline.

        Args:
            email: Email dictionary

        Returns:
            Complete processing result
        """
        logger.info(f"Processing email: {email['email_id']} - {email['subject']}")

        result = {
            'email_id': email['email_id'],
            'subject': email['subject'],
            'success': False,
            'error': None
        }

        try:
            # Step 1: Extract data from attachments
            extracted_data = None
            attachments = email.get('attachments', [])

            if attachments:
                logger.info(f"Processing {len(attachments)} attachments")
                all_text = ""
                structured_data = {}

                for attachment in attachments:
                    pdf_path = Path("data/sample_pdfs") / attachment
                    if pdf_path.exists():
                        ocr_result = self.ocr_engine.process_pdf(str(pdf_path))
                        all_text += ocr_result['raw_text'] + "\n"
                        structured_data.update(ocr_result['structured_data'])

                extracted_data = {
                    'all_text': all_text,
                    'structured_data': structured_data
                }
                result['extracted_data'] = structured_data

            # Step 2: Classify intent
            logger.info("Classifying email intent...")
            classification = self.classifier.classify(email, extracted_data)
            result['classification'] = {
                'intent': classification['intent'],
                'confidence': classification['confidence'],
                'sub_category': classification.get('sub_category'),
                'reasoning': classification['reasoning']
            }

            # Step 3: Generate response
            logger.info("Generating response...")
            response = self.response_generator.generate(
                email,
                classification['intent'],
                extracted_data
            )
            result['response'] = {
                'text': response['response_text'],
                'word_count': response['word_count'],
                'template_used': response['template_used']
            }

            # Evaluate response quality
            quality = self.response_generator.evaluate_response_quality(response)
            result['response']['quality_score'] = quality['quality_score']

            # Step 4: Determine action
            logger.info("Determining recommended action...")
            action = self.classifier.llm_agent.determine_action(
                email,
                classification['intent'],
                classification['confidence']
            )
            result['action'] = action

            # Step 5: Store in database
            logger.info("Storing results in database...")
            self._store_results(email, classification, response, action, extracted_data)

            result['success'] = True
            logger.info(f"Successfully processed email {email['email_id']}")

        except Exception as e:
            logger.error(f"Error processing email {email['email_id']}: {str(e)}")
            result['error'] = str(e)

        return result

    def _store_results(self,
                      email: Dict[str, Any],
                      classification: Dict[str, Any],
                      response: Dict[str, Any],
                      action: Dict[str, Any],
                      extracted_data: Dict[str, Any] = None):
        """Store processing results in database"""
        session = next(self.db_manager.get_session())

        try:
            # Store email
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

            # Store extracted data
            if extracted_data and extracted_data.get('structured_data'):
                structured = extracted_data['structured_data']
                extracted_data_dict = {
                    'email_id': db_email.id,
                    'attachment_name': email.get('attachments', [''])[0] if email.get('attachments') else None,
                    'raw_text': extracted_data.get('all_text', ''),
                    'account_number': ','.join(structured.get('account_numbers', [])),
                    'names': json.dumps(structured.get('names', [])),
                    'amounts': json.dumps([str(amt) for amt in structured.get('amounts', [])]),
                    'other_data': json.dumps(structured)
                }
                self.db_manager.create_extracted_data(session, extracted_data_dict)

            # Store classification
            classification_data = {
                'email_id': db_email.id,
                'intent': classification['intent'],
                'confidence': classification['confidence'],
                'sub_category': classification.get('sub_category'),
                'reasoning': classification['reasoning']
            }
            self.db_manager.create_classification(session, classification_data)

            # Store response
            response_data = {
                'email_id': db_email.id,
                'response_text': response['response_text'],
                'template_used': response['template_used'],
                'personalization_data': json.dumps(response['personalization_data'])
            }
            self.db_manager.create_response(session, response_data)

            # Store action
            action_data = {
                'email_id': db_email.id,
                'action_type': action['action_type'],
                'priority': action['priority'],
                'reason': action['reason'],
                'assigned_to': action['assigned_to']
            }
            self.db_manager.create_action(session, action_data)

            logger.info(f"Results stored in database for email {email['email_id']}")

        except Exception as e:
            logger.error(f"Error storing results: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def process_all_emails(self) -> List[Dict[str, Any]]:
        """
        Process all emails in the sample data.

        Returns:
            List of processing results
        """
        logger.info("Starting batch email processing...")

        # Load all emails
        emails = self.email_processor.load_all_emails()
        logger.info(f"Loaded {len(emails)} emails")

        # Process each email
        results = []
        for i, email in enumerate(emails, 1):
            logger.info(f"Processing email {i}/{len(emails)}")
            result = self.process_email(email)
            results.append(result)

        # Generate summary
        successful = sum(1 for r in results if r['success'])
        logger.info(f"\nProcessing complete: {successful}/{len(emails)} emails processed successfully")

        return results

    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics from processing results.

        Args:
            results: List of processing results

        Returns:
            Summary dictionary
        """
        summary = {
            'total_emails': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'intents': {},
            'actions': {},
            'avg_confidence': 0.0,
            'high_confidence': 0,
            'low_confidence': 0
        }

        confidences = []

        for result in results:
            if result['success']:
                # Count intents
                intent = result['classification']['intent']
                summary['intents'][intent] = summary['intents'].get(intent, 0) + 1

                # Count actions
                action = result['action']['action_type']
                summary['actions'][action] = summary['actions'].get(action, 0) + 1

                # Track confidence
                confidence = result['classification']['confidence']
                confidences.append(confidence)

                if confidence >= 0.8:
                    summary['high_confidence'] += 1
                elif confidence < 0.6:
                    summary['low_confidence'] += 1

        # Calculate average confidence
        if confidences:
            summary['avg_confidence'] = sum(confidences) / len(confidences)

        return summary


def main():
    """Main entry point"""
    logger.info("=" * 70)
    logger.info("Banking Email Processing Pipeline")
    logger.info("=" * 70)

    # Create pipeline
    pipeline = EmailProcessingPipeline()

    # Process all emails
    results = pipeline.process_all_emails()

    # Generate and display summary
    summary = pipeline.generate_summary(results)

    print("\n" + "=" * 70)
    print("PROCESSING SUMMARY")
    print("=" * 70)
    print(f"Total Emails:        {summary['total_emails']}")
    print(f"Successful:          {summary['successful']}")
    print(f"Failed:              {summary['failed']}")
    print(f"Average Confidence:  {summary['avg_confidence']:.1%}")
    print(f"High Confidence:     {summary['high_confidence']}")
    print(f"Low Confidence:      {summary['low_confidence']}")
    print("\nIntent Distribution:")
    for intent, count in summary['intents'].items():
        print(f"  {intent:20s}: {count}")
    print("\nAction Distribution:")
    for action, count in summary['actions'].items():
        print(f"  {action:20s}: {count}")
    print("=" * 70)

    logger.info("Pipeline execution completed")


if __name__ == "__main__":
    main()

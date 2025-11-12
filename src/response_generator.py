"""
Response generator for banking emails.
Generates professional, context-aware responses using LLM with templates.
"""
from typing import Dict, Any, Optional
import logging
from src.llm_agent import LLMAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generate professional banking responses using LLM"""

    # Response templates for different intents
    RESPONSE_TEMPLATES = {
        'loan_request': {
            'greeting': 'Thank you for your interest in our loan services.',
            'acknowledgment': 'We have received your loan application and appreciate you choosing our bank.',
            'next_steps': [
                'Our loan department will review your application',
                'A loan officer will contact you within 2-3 business days',
                'Please ensure all required documents are submitted',
                'You can track your application status through online banking'
            ],
            'closing': 'We look forward to helping you achieve your financial goals.'
        },
        'kyc_update': {
            'greeting': 'Thank you for contacting us regarding your account information.',
            'acknowledgment': 'We have received your request to update your KYC details.',
            'next_steps': [
                'We will verify the documents you have provided',
                'Updates will be processed within 1-2 business days',
                'You will receive a confirmation email once completed',
                'Please ensure all documents are clear and valid'
            ],
            'closing': 'Thank you for keeping your information up to date.'
        },
        'account_issue': {
            'greeting': 'Thank you for bringing this matter to our attention.',
            'acknowledgment': 'We understand your concern regarding your account.',
            'next_steps': [
                'Our technical team is investigating the issue',
                'We will resolve this as quickly as possible',
                'You will be notified once the issue is resolved',
                'If urgent, please call our support hotline'
            ],
            'closing': 'We apologize for any inconvenience and appreciate your patience.'
        },
        'fraud_complaint': {
            'greeting': 'Thank you for reporting this security concern.',
            'acknowledgment': 'We take fraud and security issues very seriously and have immediately flagged your account.',
            'next_steps': [
                'Your card/account has been temporarily secured',
                'Our fraud department is investigating immediately',
                'You will be contacted by a fraud specialist within 24 hours',
                'Please do not respond to any suspicious communications',
                'Monitor your account for any additional unauthorized activity'
            ],
            'closing': 'Your security is our top priority. We are committed to resolving this matter swiftly.'
        },
        'general_inquiry': {
            'greeting': 'Thank you for your inquiry.',
            'acknowledgment': 'We are happy to assist you with information about our services.',
            'next_steps': [
                'Our customer service team will provide detailed information',
                'You can also visit our website for more details',
                'Feel free to visit any branch for in-person assistance',
                'We are here to help with any questions you may have'
            ],
            'closing': 'Thank you for choosing our bank.'
        }
    }

    def __init__(self, llm_agent: LLMAgent = None):
        """
        Initialize response generator.

        Args:
            llm_agent: LLMAgent instance (creates new one if not provided)
        """
        self.llm_agent = llm_agent or LLMAgent()
        logger.info("Response generator initialized")

    def generate(self,
                email_data: Dict[str, Any],
                intent: str,
                extracted_data: Optional[Dict[str, Any]] = None,
                use_template: bool = True) -> Dict[str, Any]:
        """
        Generate response for email.

        Args:
            email_data: Email dictionary
            intent: Classified intent
            extracted_data: Optional extracted data from attachments
            use_template: Whether to use template-based approach

        Returns:
            Dictionary with response_text, template_used, and personalization_data
        """
        logger.info(f"Generating response for intent: {intent}")

        # Generate personalized response using LLM
        response_text = self.llm_agent.generate_response(email_data, intent, extracted_data)

        # Get template info
        template_used = intent if use_template else None

        # Extract personalization data
        personalization_data = self._extract_personalization_data(email_data, extracted_data)

        result = {
            'response_text': response_text,
            'template_used': template_used,
            'personalization_data': personalization_data,
            'word_count': len(response_text.split()) if response_text else 0,
            'character_count': len(response_text) if response_text else 0
        }

        logger.info(f"Generated response: {result['word_count']} words")
        return result

    def _extract_personalization_data(self,
                                     email_data: Dict[str, Any],
                                     extracted_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract personalization data for response.

        Args:
            email_data: Email dictionary
            extracted_data: Optional extracted data

        Returns:
            Dictionary with personalization fields
        """
        personalization = {
            'customer_name': email_data.get('sender_name', ''),
            'sender_email': email_data.get('sender'),
            'subject': email_data.get('subject'),
        }

        # Add extracted data if available
        if extracted_data:
            if 'account_numbers' in extracted_data and extracted_data['account_numbers']:
                personalization['account_number'] = extracted_data['account_numbers'][0]
            if 'amounts' in extracted_data and extracted_data['amounts']:
                personalization['amount'] = extracted_data['amounts'][0]
            if 'names' in extracted_data and extracted_data['names']:
                personalization['mentioned_names'] = extracted_data['names']

        return personalization

    def generate_with_template(self, intent: str, personalization: Dict[str, Any]) -> str:
        """
        Generate response using template.

        Args:
            intent: Intent category
            personalization: Personalization data

        Returns:
            Generated response text
        """
        if intent not in self.RESPONSE_TEMPLATES:
            logger.warning(f"No template found for intent: {intent}")
            return self._generate_generic_response(personalization)

        template = self.RESPONSE_TEMPLATES[intent]
        customer_name = personalization.get('customer_name', 'Valued Customer')

        # Build response
        lines = []

        # Greeting
        lines.append(f"Dear {customer_name},\n")
        lines.append(template['greeting'])
        lines.append("")

        # Acknowledgment
        lines.append(template['acknowledgment'])
        lines.append("")

        # Next steps
        lines.append("Next Steps:")
        for i, step in enumerate(template['next_steps'], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

        # Closing
        lines.append(template['closing'])
        lines.append("")
        lines.append("Best regards,")
        lines.append("Customer Service Team")
        lines.append("Your Bank")

        response = "\n".join(lines)
        return response

    def _generate_generic_response(self, personalization: Dict[str, Any]) -> str:
        """
        Generate generic response when no template available.

        Args:
            personalization: Personalization data

        Returns:
            Generic response text
        """
        customer_name = personalization.get('customer_name', 'Valued Customer')

        response = f"""Dear {customer_name},

Thank you for contacting us. We have received your message and our team will review it carefully.

One of our representatives will respond to you within 1-2 business days.

If you need immediate assistance, please call our customer service hotline at 1-800-BANK-HELP.

Thank you for your patience.

Best regards,
Customer Service Team
Your Bank
"""
        return response

    def enhance_response(self, response_text: str, tone: str = 'professional') -> str:
        """
        Enhance response with specified tone using LLM.

        Args:
            response_text: Original response text
            tone: Desired tone (professional, friendly, empathetic)

        Returns:
            Enhanced response text
        """
        prompt = f"""
Rewrite the following banking response with a more {tone} tone, while maintaining
all the key information and professional standards.

Original Response:
{response_text}

Enhanced Response:
"""

        enhanced = self.llm_agent.generate_completion(prompt, temperature=0.7, max_tokens=600)
        return enhanced if enhanced else response_text

    def add_disclaimer(self, response_text: str, intent: str) -> str:
        """
        Add appropriate disclaimer to response based on intent.

        Args:
            response_text: Response text
            intent: Intent category

        Returns:
            Response with disclaimer added
        """
        disclaimers = {
            'loan_request': '\n\n---\nDisclaimer: Loan approval is subject to credit verification and underwriting standards. Terms and conditions apply.',
            'fraud_complaint': '\n\n---\nSecurity Reminder: Never share your password, PIN, or OTP with anyone, including bank employees.',
            'account_issue': '\n\n---\nNote: This is an automated response. For urgent matters, please call our 24/7 support line.',
        }

        disclaimer = disclaimers.get(intent, '')
        return response_text + disclaimer

    def evaluate_response_quality(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate quality of generated response.

        Args:
            response: Response dictionary

        Returns:
            Dictionary with quality metrics
        """
        response_text = response['response_text']
        word_count = response['word_count']

        quality = {
            'has_greeting': 'dear' in response_text.lower()[:100],
            'has_closing': any(word in response_text.lower()[-200:] for word in ['regards', 'sincerely', 'thank you']),
            'appropriate_length': 50 <= word_count <= 300,
            'has_next_steps': any(word in response_text.lower() for word in ['will', 'next', 'steps', 'process']),
            'professional_tone': not any(word in response_text.lower() for word in ['hey', 'gonna', 'wanna']),
        }

        # Calculate quality score (0-100)
        quality_score = sum([
            30 if quality['has_greeting'] else 0,
            20 if quality['has_closing'] else 0,
            20 if quality['appropriate_length'] else 0,
            15 if quality['has_next_steps'] else 0,
            15 if quality['professional_tone'] else 0,
        ])

        quality['quality_score'] = quality_score
        quality['quality_level'] = 'high' if quality_score >= 80 else 'medium' if quality_score >= 60 else 'low'

        return quality


def test_response_generator():
    """Test response generator functionality"""
    from src.email_processor import EmailProcessor
    from src.classifier import IntentClassifier

    print("\n=== Testing Response Generator ===\n")

    generator = ResponseGenerator()

    if not generator.llm_agent.client:
        print("⚠ OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
        print("Response generation tests will be skipped.\n")
        return

    # Load sample emails
    processor = EmailProcessor()
    emails = processor.load_all_emails()

    if not emails:
        print("⚠ No sample emails found.")
        return

    # Test response generation
    print("1. Generating responses for sample emails...\n")

    classifier = IntentClassifier()

    for i, email in enumerate(emails[:2]):
        print(f"Email {i+1}: {email['subject']}")

        # Classify
        classification = classifier.classify(email)
        print(f"   Intent: {classification['intent']}")

        # Generate response
        response = generator.generate(email, classification['intent'])

        print(f"   Response ({response['word_count']} words):")
        print(f"   {response['response_text'][:200]}...")
        print()

        # Evaluate quality
        quality = generator.evaluate_response_quality(response)
        print(f"   Quality Score: {quality['quality_score']}/100 ({quality['quality_level']})")
        print(f"   Has greeting: {quality['has_greeting']}")
        print(f"   Has closing: {quality['has_closing']}")
        print(f"   Appropriate length: {quality['appropriate_length']}")
        print()

    # Test template-based response
    print("2. Testing template-based response...")
    template_response = generator.generate_with_template('loan_request', {'customer_name': 'John Doe'})
    print(f"   {template_response[:200]}...")
    print()


if __name__ == "__main__":
    test_response_generator()

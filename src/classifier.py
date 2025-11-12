"""
Email intent classifier using LLM.
Classifies banking emails into predefined categories with confidence scoring.
"""
from typing import Dict, Any, List
import logging
from src.llm_agent import LLMAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classify banking email intents with LLM"""

    # Define intent categories with descriptions
    INTENT_CATEGORIES = {
        'loan_request': {
            'description': 'Customer requesting a loan (home, auto, business, personal)',
            'keywords': ['loan', 'mortgage', 'financing', 'borrow', 'credit'],
            'typical_actions': ['escalate'],
            'priority_boost': True
        },
        'kyc_update': {
            'description': 'Customer updating KYC/personal information (address, employment, documents)',
            'keywords': ['update', 'kyc', 'address', 'employment', 'change', 'verify'],
            'typical_actions': ['reply'],
            'priority_boost': False
        },
        'account_issue': {
            'description': 'Problems with account access, transactions, statements, or technical issues',
            'keywords': ['problem', 'issue', 'error', 'unable', 'cannot', 'access', 'login'],
            'typical_actions': ['reply', 'escalate'],
            'priority_boost': True
        },
        'fraud_complaint': {
            'description': 'Reporting fraud, unauthorized transactions, security concerns, or suspicious activity',
            'keywords': ['fraud', 'unauthorized', 'suspicious', 'theft', 'hack', 'scam', 'phishing'],
            'typical_actions': ['escalate'],
            'priority_boost': True
        },
        'general_inquiry': {
            'description': 'General questions about products, services, rates, or information requests',
            'keywords': ['question', 'inquiry', 'information', 'rate', 'fee', 'service', 'product'],
            'typical_actions': ['reply'],
            'priority_boost': False
        }
    }

    def __init__(self, llm_agent: LLMAgent = None):
        """
        Initialize classifier.

        Args:
            llm_agent: LLMAgent instance (creates new one if not provided)
        """
        self.llm_agent = llm_agent or LLMAgent()
        logger.info("Intent classifier initialized")

    def classify(self, email_data: Dict[str, Any], extracted_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify email intent using LLM.

        Args:
            email_data: Email dictionary with subject, body, etc.
            extracted_data: Optional extracted data from attachments

        Returns:
            Dictionary with intent, confidence, sub_category, and reasoning
        """
        logger.info(f"Classifying email: {email_data.get('email_id', 'unknown')}")

        # Use LLM agent for classification
        classification = self.llm_agent.classify_intent(email_data, extracted_data)

        # Validate intent
        if classification['intent'] not in self.INTENT_CATEGORIES:
            logger.warning(f"Unknown intent: {classification['intent']}, defaulting to general_inquiry")
            classification['intent'] = 'general_inquiry'
            classification['confidence'] = max(0.5, classification['confidence'] * 0.7)

        # Add category metadata
        classification['category_info'] = self.INTENT_CATEGORIES.get(classification['intent'], {})

        logger.info(f"Classified as {classification['intent']} with confidence {classification['confidence']:.2f}")
        return classification

    def classify_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify multiple emails.

        Args:
            emails: List of email dictionaries

        Returns:
            List of classification results
        """
        logger.info(f"Batch classifying {len(emails)} emails")
        results = []

        for email in emails:
            classification = self.classify(email)
            classification['email_id'] = email.get('email_id')
            results.append(classification)

        return results

    def get_intent_summary(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics from classifications.

        Args:
            classifications: List of classification results

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total': len(classifications),
            'by_intent': {},
            'high_confidence': 0,
            'low_confidence': 0,
            'avg_confidence': 0.0
        }

        confidence_sum = 0.0

        for classification in classifications:
            intent = classification['intent']
            confidence = classification['confidence']

            # Count by intent
            summary['by_intent'][intent] = summary['by_intent'].get(intent, 0) + 1

            # Confidence tracking
            confidence_sum += confidence
            if confidence >= 0.8:
                summary['high_confidence'] += 1
            elif confidence < 0.6:
                summary['low_confidence'] += 1

        # Calculate average confidence
        if classifications:
            summary['avg_confidence'] = confidence_sum / len(classifications)

        return summary

    def should_escalate(self, classification: Dict[str, Any], email_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Determine if email should be escalated based on classification.

        Args:
            classification: Classification result
            email_data: Original email data

        Returns:
            Tuple of (should_escalate, reason)
        """
        intent = classification['intent']
        confidence = classification['confidence']
        priority = email_data.get('priority', 'medium')

        # Low confidence classification
        if confidence < 0.6:
            return True, f"Low confidence classification ({confidence:.2f})"

        # Critical priority
        if priority == 'critical':
            return True, "Critical priority email"

        # Fraud complaints always escalate
        if intent == 'fraud_complaint':
            return True, "Fraud complaint requires immediate review"

        # Loan requests escalate
        if intent == 'loan_request':
            return True, "Loan application requires specialist review"

        # High priority account issues
        if intent == 'account_issue' and priority == 'high':
            return True, "High priority account issue"

        return False, "Standard processing"

    def get_category_description(self, intent: str) -> str:
        """
        Get description for an intent category.

        Args:
            intent: Intent category name

        Returns:
            Description string
        """
        return self.INTENT_CATEGORIES.get(intent, {}).get('description', 'Unknown intent category')

    def analyze_classification_quality(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze quality of a classification result.

        Args:
            classification: Classification result

        Returns:
            Dictionary with quality metrics
        """
        confidence = classification['confidence']
        intent = classification['intent']

        quality = {
            'confidence': confidence,
            'confidence_level': 'high' if confidence >= 0.8 else 'medium' if confidence >= 0.6 else 'low',
            'needs_review': confidence < 0.6,
            'valid_intent': intent in self.INTENT_CATEGORIES,
            'has_reasoning': bool(classification.get('reasoning')),
            'has_sub_category': bool(classification.get('sub_category'))
        }

        # Overall quality score (0-100)
        quality_score = 0
        quality_score += confidence * 60  # Confidence is 60% of score
        quality_score += 20 if quality['valid_intent'] else 0
        quality_score += 10 if quality['has_reasoning'] else 0
        quality_score += 10 if quality['has_sub_category'] else 0

        quality['quality_score'] = round(quality_score, 1)

        return quality


def test_classifier():
    """Test classifier functionality"""
    from src.email_processor import EmailProcessor

    print("\n=== Testing Intent Classifier ===\n")

    classifier = IntentClassifier()

    if not classifier.llm_agent.client:
        print("⚠ OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
        print("Classification tests will be skipped.\n")
        return

    # Load sample emails
    processor = EmailProcessor()
    emails = processor.load_all_emails()

    if not emails:
        print("⚠ No sample emails found. Run create_sample_emails first.")
        return

    print(f"Loaded {len(emails)} sample emails\n")

    # Test classification on first 3 emails
    print("1. Classifying sample emails...\n")
    classifications = []

    for i, email in enumerate(emails[:3]):
        print(f"Email {i+1}: {email['subject']}")
        classification = classifier.classify(email)
        classifications.append(classification)

        print(f"   Intent: {classification['intent']}")
        print(f"   Confidence: {classification['confidence']:.2f}")
        print(f"   Sub-category: {classification.get('sub_category', 'N/A')}")
        print(f"   Reasoning: {classification['reasoning'][:100]}...")

        # Check if should escalate
        should_escalate, reason = classifier.should_escalate(classification, email)
        print(f"   Escalate: {should_escalate} - {reason}")

        # Quality analysis
        quality = classifier.analyze_classification_quality(classification)
        print(f"   Quality Score: {quality['quality_score']}/100 ({quality['confidence_level']} confidence)")
        print()

    # Generate summary
    print("2. Classification Summary:")
    summary = classifier.get_intent_summary(classifications)
    print(f"   Total classified: {summary['total']}")
    print(f"   Average confidence: {summary['avg_confidence']:.2f}")
    print(f"   High confidence (>=0.8): {summary['high_confidence']}")
    print(f"   Low confidence (<0.6): {summary['low_confidence']}")
    print(f"   By intent: {summary['by_intent']}")
    print()


if __name__ == "__main__":
    test_classifier()

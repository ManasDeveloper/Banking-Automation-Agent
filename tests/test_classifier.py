"""
Unit tests for classifier module
"""
import pytest
from src.classifier import IntentClassifier
from src.llm_agent import LLMAgent


@pytest.fixture
def classifier():
    """Create classifier instance"""
    return IntentClassifier()


@pytest.fixture
def sample_loan_email():
    """Create sample loan request email"""
    return {
        'email_id': 'test_loan_001',
        'sender': 'customer@example.com',
        'sender_name': 'John Doe',
        'subject': 'Home Loan Application',
        'body': 'I would like to apply for a home loan of $300,000.',
        'priority': 'high'
    }


@pytest.fixture
def sample_fraud_email():
    """Create sample fraud complaint email"""
    return {
        'email_id': 'test_fraud_001',
        'sender': 'customer@example.com',
        'sender_name': 'Jane Smith',
        'subject': 'URGENT: Unauthorized Transaction',
        'body': 'I noticed unauthorized transactions on my account. Please help immediately!',
        'priority': 'critical'
    }


class TestIntentClassifier:
    """Test cases for IntentClassifier class"""

    def test_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier is not None
        assert isinstance(classifier.llm_agent, LLMAgent)

    def test_intent_categories_defined(self, classifier):
        """Test that intent categories are properly defined"""
        assert 'loan_request' in classifier.INTENT_CATEGORIES
        assert 'kyc_update' in classifier.INTENT_CATEGORIES
        assert 'account_issue' in classifier.INTENT_CATEGORIES
        assert 'fraud_complaint' in classifier.INTENT_CATEGORIES
        assert 'general_inquiry' in classifier.INTENT_CATEGORIES

    def test_category_metadata(self, classifier):
        """Test that categories have required metadata"""
        for category, info in classifier.INTENT_CATEGORIES.items():
            assert 'description' in info
            assert 'keywords' in info
            assert 'typical_actions' in info
            assert 'priority_boost' in info

    def test_get_category_description(self, classifier):
        """Test getting category description"""
        description = classifier.get_category_description('loan_request')
        assert isinstance(description, str)
        assert len(description) > 0

    def test_get_category_description_invalid(self, classifier):
        """Test getting description for invalid category"""
        description = classifier.get_category_description('invalid_category')
        assert 'Unknown' in description

    def test_should_escalate_low_confidence(self, classifier, sample_loan_email):
        """Test escalation decision with low confidence"""
        classification = {
            'intent': 'loan_request',
            'confidence': 0.5  # Low confidence
        }
        should_escalate, reason = classifier.should_escalate(classification, sample_loan_email)
        assert should_escalate
        assert 'confidence' in reason.lower()

    def test_should_escalate_fraud(self, classifier, sample_fraud_email):
        """Test escalation decision for fraud"""
        classification = {
            'intent': 'fraud_complaint',
            'confidence': 0.9
        }
        should_escalate, reason = classifier.should_escalate(classification, sample_fraud_email)
        assert should_escalate
        assert 'fraud' in reason.lower()

    def test_should_escalate_critical_priority(self, classifier, sample_fraud_email):
        """Test escalation decision for critical priority"""
        classification = {
            'intent': 'general_inquiry',
            'confidence': 0.9
        }
        should_escalate, reason = classifier.should_escalate(classification, sample_fraud_email)
        assert should_escalate
        assert 'critical' in reason.lower()

    def test_should_not_escalate_normal(self, classifier, sample_loan_email):
        """Test no escalation for normal case"""
        sample_loan_email['priority'] = 'low'
        classification = {
            'intent': 'general_inquiry',
            'confidence': 0.9
        }
        should_escalate, reason = classifier.should_escalate(classification, sample_loan_email)
        assert not should_escalate

    def test_analyze_classification_quality_high(self, classifier):
        """Test quality analysis for high-quality classification"""
        classification = {
            'intent': 'loan_request',
            'confidence': 0.95,
            'reasoning': 'Customer explicitly mentions loan application',
            'sub_category': 'home_loan'
        }
        quality = classifier.analyze_classification_quality(classification)
        assert quality['confidence_level'] == 'high'
        assert quality['quality_score'] >= 80
        assert not quality['needs_review']

    def test_analyze_classification_quality_low(self, classifier):
        """Test quality analysis for low-quality classification"""
        classification = {
            'intent': 'unknown',
            'confidence': 0.4,
            'reasoning': None,
            'sub_category': None
        }
        quality = classifier.analyze_classification_quality(classification)
        assert quality['confidence_level'] == 'low'
        assert quality['needs_review']

    def test_get_intent_summary(self, classifier):
        """Test intent summary generation"""
        classifications = [
            {'intent': 'loan_request', 'confidence': 0.9},
            {'intent': 'loan_request', 'confidence': 0.8},
            {'intent': 'kyc_update', 'confidence': 0.7},
            {'intent': 'fraud_complaint', 'confidence': 0.95},
        ]
        summary = classifier.get_intent_summary(classifications)
        assert summary['total'] == 4
        assert summary['by_intent']['loan_request'] == 2
        assert summary['by_intent']['kyc_update'] == 1
        assert summary['high_confidence'] == 2  # >= 0.8
        assert 0.8 < summary['avg_confidence'] < 0.9

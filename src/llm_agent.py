"""
LLM Agent for interacting with OpenAI API.
Handles prompt templates, context management, and response parsing.
"""
from openai import OpenAI
from typing import Dict, Any, List, Optional
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAgent:
    """Agent for interacting with OpenAI API for banking automation tasks"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM agent.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

        # Banking domain context
        self.banking_context = """
You are an AI assistant for a banking institution. You help process customer emails,
classify their intent, and generate appropriate professional responses.

Key banking services include:
- Loan applications (home, auto, business)
- Account management (checking, savings, credit cards)
- KYC updates (address changes, employment updates, documentation)
- Fraud and security issues
- General inquiries and customer support

Always maintain a professional, helpful, and empathetic tone. Prioritize security
and compliance in all responses.
"""
        logger.info(f"LLM Agent initialized with model: {self.model}")

    def _create_messages(self, system_prompt: str, user_prompt: str) -> List[Dict[str, str]]:
        """
        Create messages array for OpenAI API.

        Args:
            system_prompt: System instruction
            user_prompt: User message

        Returns:
            List of message dictionaries
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return messages

    def generate_completion(self,
                          prompt: str,
                          system_prompt: Optional[str] = None,
                          temperature: float = 0.7,
                          max_tokens: int = 1000) -> Optional[str]:
        """
        Generate completion using OpenAI API.

        Args:
            prompt: User prompt
            system_prompt: System prompt (defaults to banking context)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text or None if error
        """
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return None

        try:
            system_prompt = system_prompt or self.banking_context
            messages = self._create_messages(system_prompt, prompt)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            completion = response.choices[0].message.content
            logger.info(f"Generated completion: {len(completion)} characters")
            return completion

        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return None

    def classify_intent(self, email_data: Dict[str, Any], extracted_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify email intent using LLM.

        Args:
            email_data: Email dictionary with subject, body, etc.
            extracted_data: Optional extracted data from attachments

        Returns:
            Dictionary with intent, confidence, and reasoning
        """
        # Create classification prompt
        prompt = f"""
Classify the intent of the following banking customer email into ONE of these categories:

Categories:
1. loan_request - Customer requesting a loan (home, auto, business, personal)
2. kyc_update - Customer updating KYC information (address, employment, documents)
3. account_issue - Problems with account access, transactions, or statements
4. fraud_complaint - Reporting fraud, unauthorized transactions, or security concerns
5. general_inquiry - General questions about products, services, or information requests

Email Details:
Subject: {email_data['subject']}
From: {email_data.get('sender_name', '')} <{email_data['sender']}>
Body:
{email_data['body']}
"""

        if extracted_data:
            prompt += f"\n\nExtracted Data from Attachments:\n{extracted_data}\n"

        prompt += """
Respond in this exact format:
INTENT: <category_name>
CONFIDENCE: <0.0-1.0>
SUB_CATEGORY: <specific type if applicable>
REASONING: <brief explanation>
"""

        response = self.generate_completion(prompt, temperature=0.3, max_tokens=300)

        if not response:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'sub_category': None,
                'reasoning': 'Failed to classify'
            }

        # Parse response
        result = self._parse_classification_response(response)
        logger.info(f"Classified as: {result['intent']} (confidence: {result['confidence']})")
        return result

    def _parse_classification_response(self, response: str) -> Dict[str, Any]:
        """
        Parse classification response from LLM.

        Args:
            response: Raw LLM response

        Returns:
            Parsed dictionary with intent, confidence, etc.
        """
        result = {
            'intent': 'unknown',
            'confidence': 0.0,
            'sub_category': None,
            'reasoning': ''
        }

        try:
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('INTENT:'):
                    result['intent'] = line.replace('INTENT:', '').strip().lower()
                elif line.startswith('CONFIDENCE:'):
                    conf_str = line.replace('CONFIDENCE:', '').strip()
                    result['confidence'] = float(conf_str)
                elif line.startswith('SUB_CATEGORY:'):
                    sub_cat = line.replace('SUB_CATEGORY:', '').strip()
                    result['sub_category'] = sub_cat if sub_cat.lower() != 'none' else None
                elif line.startswith('REASONING:'):
                    result['reasoning'] = line.replace('REASONING:', '').strip()

        except Exception as e:
            logger.error(f"Error parsing classification response: {e}")

        return result

    def generate_response(self,
                         email_data: Dict[str, Any],
                         intent: str,
                         extracted_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate professional response to customer email.

        Args:
            email_data: Email dictionary
            intent: Classified intent
            extracted_data: Optional extracted data from attachments

        Returns:
            Generated response text
        """
        # Create response generation prompt
        prompt = f"""
Generate a professional banking response to the following customer email.

Customer Email:
Subject: {email_data['subject']}
From: {email_data.get('sender_name', '')}
Body:
{email_data['body']}

Classified Intent: {intent}
"""

        if extracted_data:
            prompt += f"\nExtracted Information: {extracted_data}\n"

        prompt += f"""
Requirements:
1. Address the customer by name if available
2. Acknowledge their {intent.replace('_', ' ')}
3. Provide relevant information or next steps
4. Be professional, empathetic, and helpful
5. Include appropriate disclaimers if needed
6. Sign off appropriately

Generate ONLY the email response body (no subject line).
"""

        response = self.generate_completion(prompt, temperature=0.7, max_tokens=500)
        return response or "I apologize, but I'm unable to generate a response at this time. Please contact our customer service team directly."

    def determine_action(self, email_data: Dict[str, Any], intent: str, confidence: float) -> Dict[str, Any]:
        """
        Determine recommended action for email.

        Args:
            email_data: Email dictionary
            intent: Classified intent
            confidence: Classification confidence

        Returns:
            Dictionary with action_type, priority, reason, and assigned_to
        """
        priority = email_data.get('priority', 'medium')

        # Determine action type based on intent and confidence
        if confidence < 0.6:
            action_type = 'escalate'
            reason = 'Low confidence in classification, requires human review'
            assigned_to = 'human_review_team'
        elif intent == 'fraud_complaint' or priority == 'critical':
            action_type = 'escalate'
            reason = 'Urgent issue requiring immediate attention'
            assigned_to = 'fraud_department' if intent == 'fraud_complaint' else 'escalation_team'
        elif intent == 'loan_request':
            action_type = 'escalate'
            reason = 'Loan application requires underwriting review'
            assigned_to = 'loan_department'
        elif intent == 'kyc_update':
            action_type = 'reply'
            reason = 'Standard KYC update, can be processed automatically'
            assigned_to = 'kyc_team'
        elif intent == 'account_issue':
            if priority == 'high':
                action_type = 'escalate'
                reason = 'High priority account issue'
                assigned_to = 'customer_support_tier2'
            else:
                action_type = 'reply'
                reason = 'Standard account issue'
                assigned_to = 'customer_support'
        else:  # general_inquiry
            action_type = 'reply'
            reason = 'General inquiry, can be handled with standard response'
            assigned_to = 'customer_support'

        return {
            'action_type': action_type,
            'priority': priority,
            'reason': reason,
            'assigned_to': assigned_to
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract banking entities from text using LLM.

        Args:
            text: Text to extract entities from

        Returns:
            Dictionary with entity types and values
        """
        prompt = f"""
Extract banking-related entities from the following text:

{text}

Extract these entity types:
- ACCOUNT_NUMBERS: Account numbers mentioned
- AMOUNTS: Dollar amounts mentioned
- DATES: Dates mentioned
- NAMES: Person names mentioned
- LOCATIONS: Addresses or locations mentioned

Respond in this format:
ACCOUNT_NUMBERS: value1, value2
AMOUNTS: value1, value2
DATES: value1, value2
NAMES: value1, value2
LOCATIONS: value1, value2

If no entities found for a type, write "None".
"""

        response = self.generate_completion(prompt, temperature=0.2, max_tokens=400)

        if not response:
            return {}

        # Parse entities
        entities = {}
        for line in response.strip().split('\n'):
            if ':' in line:
                entity_type, values = line.split(':', 1)
                entity_type = entity_type.strip().lower()
                values = values.strip()

                if values.lower() != 'none':
                    entities[entity_type] = [v.strip() for v in values.split(',') if v.strip()]
                else:
                    entities[entity_type] = []

        return entities


def test_llm_agent():
    """Test LLM agent functionality"""
    print("\n=== Testing LLM Agent ===\n")

    agent = LLMAgent()

    if not agent.client:
        print("⚠ OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
        print("Some tests will be skipped.\n")
        return

    # Test classification
    print("1. Testing intent classification...")
    sample_email = {
        'subject': 'Home Loan Application',
        'sender': 'john@example.com',
        'sender_name': 'John Doe',
        'body': 'I would like to apply for a home loan of $300,000 for property purchase.'
    }

    classification = agent.classify_intent(sample_email)
    print(f"   Intent: {classification['intent']}")
    print(f"   Confidence: {classification['confidence']}")
    print(f"   Reasoning: {classification['reasoning']}\n")

    # Test response generation
    print("2. Testing response generation...")
    response = agent.generate_response(sample_email, classification['intent'])
    print(f"   Generated response:\n{response[:200]}...\n")

    # Test action determination
    print("3. Testing action determination...")
    action = agent.determine_action(sample_email, classification['intent'], classification['confidence'])
    print(f"   Action: {action['action_type']}")
    print(f"   Assigned to: {action['assigned_to']}")
    print(f"   Reason: {action['reason']}\n")


if __name__ == "__main__":
    test_llm_agent()

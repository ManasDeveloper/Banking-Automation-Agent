"""
Database layer for banking automation system.
Handles all data persistence using SQLAlchemy with SQLite.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Email(Base):
    """Email records from mock email data"""
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String(50), unique=True, nullable=False, index=True)
    sender = Column(String(255), nullable=False)
    sender_name = Column(String(255))
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    priority = Column(String(20))
    requires_response = Column(Boolean, default=True)
    processed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    extracted_data = relationship("ExtractedData", back_populates="email", cascade="all, delete-orphan")
    classifications = relationship("Classification", back_populates="email", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="email", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="email", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert email to dictionary"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'sender': self.sender,
            'sender_name': self.sender_name,
            'subject': self.subject,
            'body': self.body,
            'date': self.date.isoformat() if self.date else None,
            'priority': self.priority,
            'requires_response': self.requires_response,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
        }


class ExtractedData(Base):
    """Structured data extracted from email attachments via OCR"""
    __tablename__ = 'extracted_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    attachment_name = Column(String(255))
    raw_text = Column(Text)
    account_number = Column(String(50))
    amount = Column(Float)
    date_mentioned = Column(String(100))
    names = Column(Text)  # JSON string of names found
    addresses = Column(Text)  # JSON string of addresses
    other_data = Column(Text)  # JSON string for other extracted fields
    extracted_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    email = relationship("Email", back_populates="extracted_data")

    def to_dict(self) -> Dict[str, Any]:
        """Convert extracted data to dictionary"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'attachment_name': self.attachment_name,
            'raw_text': self.raw_text,
            'account_number': self.account_number,
            'amount': self.amount,
            'date_mentioned': self.date_mentioned,
            'names': self.names,
            'addresses': self.addresses,
            'other_data': self.other_data,
            'extracted_at': self.extracted_at.isoformat() if self.extracted_at else None,
        }


class Classification(Base):
    """Intent classification results from LLM"""
    __tablename__ = 'classifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    intent = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    sub_category = Column(String(100))
    reasoning = Column(Text)  # LLM's reasoning for classification
    classified_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    email = relationship("Email", back_populates="classifications")

    def to_dict(self) -> Dict[str, Any]:
        """Convert classification to dictionary"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'intent': self.intent,
            'confidence': self.confidence,
            'sub_category': self.sub_category,
            'reasoning': self.reasoning,
            'classified_at': self.classified_at.isoformat() if self.classified_at else None,
        }


class Response(Base):
    """Generated responses from LLM"""
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    response_text = Column(Text, nullable=False)
    template_used = Column(String(100))
    personalization_data = Column(Text)  # JSON string of personalization fields
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_approved = Column(Boolean, default=False)
    approved_at = Column(DateTime)

    # Relationship
    email = relationship("Email", back_populates="responses")

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'response_text': self.response_text,
            'template_used': self.template_used,
            'personalization_data': self.personalization_data,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'is_approved': self.is_approved,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
        }


class Action(Base):
    """Recommended actions for each email"""
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    action_type = Column(String(50), nullable=False)  # reply, escalate, log, etc.
    priority = Column(String(20))
    reason = Column(Text)
    assigned_to = Column(String(100))  # department or person
    status = Column(String(20), default='pending')  # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationship
    email = relationship("Email", back_populates="actions")

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'action_type': self.action_type,
            'priority': self.priority,
            'reason': self.reason,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class DatabaseManager:
    """Manager class for database operations"""

    def __init__(self, database_url: str = "sqlite:///./banking_automation.db"):
        """Initialize database connection"""
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"Database initialized: {database_url}")

    def init_db(self) -> None:
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def get_session(self):
        """Get a new database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def drop_all_tables(self) -> None:
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")

    # Email CRUD operations
    def create_email(self, session, email_data: Dict[str, Any]) -> Email:
        """Create a new email record"""
        email = Email(**email_data)
        session.add(email)
        session.commit()
        session.refresh(email)
        logger.info(f"Email created: {email.email_id}")
        return email

    def get_email_by_id(self, session, email_id: str) -> Optional[Email]:
        """Get email by email_id"""
        return session.query(Email).filter(Email.email_id == email_id).first()

    def get_all_emails(self, session) -> List[Email]:
        """Get all emails"""
        return session.query(Email).order_by(Email.date.desc()).all()

    # ExtractedData CRUD operations
    def create_extracted_data(self, session, data: Dict[str, Any]) -> ExtractedData:
        """Create extracted data record"""
        extracted = ExtractedData(**data)
        session.add(extracted)
        session.commit()
        session.refresh(extracted)
        logger.info(f"Extracted data created for email_id: {extracted.email_id}")
        return extracted

    def get_extracted_data_by_email(self, session, email_id: int) -> List[ExtractedData]:
        """Get all extracted data for an email"""
        return session.query(ExtractedData).filter(ExtractedData.email_id == email_id).all()

    # Classification CRUD operations
    def create_classification(self, session, classification_data: Dict[str, Any]) -> Classification:
        """Create classification record"""
        classification = Classification(**classification_data)
        session.add(classification)
        session.commit()
        session.refresh(classification)
        logger.info(f"Classification created for email_id: {classification.email_id} - Intent: {classification.intent}")
        return classification

    def get_classification_by_email(self, session, email_id: int) -> Optional[Classification]:
        """Get classification for an email"""
        return session.query(Classification).filter(Classification.email_id == email_id).first()

    # Response CRUD operations
    def create_response(self, session, response_data: Dict[str, Any]) -> Response:
        """Create response record"""
        response = Response(**response_data)
        session.add(response)
        session.commit()
        session.refresh(response)
        logger.info(f"Response created for email_id: {response.email_id}")
        return response

    def get_response_by_email(self, session, email_id: int) -> Optional[Response]:
        """Get response for an email"""
        return session.query(Response).filter(Response.email_id == email_id).first()

    def approve_response(self, session, response_id: int) -> Optional[Response]:
        """Approve a response"""
        response = session.query(Response).filter(Response.id == response_id).first()
        if response:
            response.is_approved = True
            response.approved_at = datetime.utcnow()
            session.commit()
            session.refresh(response)
            logger.info(f"Response approved: {response_id}")
        return response

    # Action CRUD operations
    def create_action(self, session, action_data: Dict[str, Any]) -> Action:
        """Create action record"""
        action = Action(**action_data)
        session.add(action)
        session.commit()
        session.refresh(action)
        logger.info(f"Action created for email_id: {action.email_id} - Type: {action.action_type}")
        return action

    def get_actions_by_email(self, session, email_id: int) -> List[Action]:
        """Get all actions for an email"""
        return session.query(Action).filter(Action.email_id == email_id).all()

    def complete_action(self, session, action_id: int) -> Optional[Action]:
        """Mark action as completed"""
        action = session.query(Action).filter(Action.id == action_id).first()
        if action:
            action.status = 'completed'
            action.completed_at = datetime.utcnow()
            session.commit()
            session.refresh(action)
            logger.info(f"Action completed: {action_id}")
        return action

    # Analytics and reporting
    def get_classification_stats(self, session) -> Dict[str, int]:
        """Get classification statistics"""
        classifications = session.query(Classification).all()
        stats = {}
        for classification in classifications:
            intent = classification.intent
            stats[intent] = stats.get(intent, 0) + 1
        return stats

    def get_action_stats(self, session) -> Dict[str, int]:
        """Get action statistics"""
        actions = session.query(Action).all()
        stats = {}
        for action in actions:
            action_type = action.action_type
            stats[action_type] = stats.get(action_type, 0) + 1
        return stats


# Singleton instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(database_url: str = "sqlite:///./banking_automation.db") -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


if __name__ == "__main__":
    # Test database creation
    db = get_db_manager()
    db.init_db()
    print("✓ Database initialized successfully!")

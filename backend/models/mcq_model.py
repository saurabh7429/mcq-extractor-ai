"""
MCQ Model - Database model for MCQ questions.
"""
import logging
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.models.database import Base

# Create logger
logger = logging.getLogger(__name__)


class MCQ(Base):
    """Model for storing MCQ questions."""
    
    __tablename__ = 'mcqs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_id = Column(Integer, ForeignKey('pdf_files.id', ondelete='CASCADE'), nullable=False, index=True)
    question = Column(String(2000), nullable=False)
    options = Column(JSON, nullable=False)  # Stores list of 4 options as JSON
    answer = Column(String(500), nullable=False)  # The correct answer string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to PDF
    pdf = relationship('PDFFile', back_populates='mcqs')
    
    def __repr__(self):
        return f"<MCQ(id={self.id}, question={self.question[:50]}...)>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'pdf_id': self.pdf_id,
            'question': self.question,
            'options': self.options if isinstance(self.options, list) else json.loads(self.options),
            'answer': self.answer,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def options_list(self):
        """Get options as a list (handles both JSON string and list)."""
        if isinstance(self.options, str):
            return json.loads(self.options)
        return self.options

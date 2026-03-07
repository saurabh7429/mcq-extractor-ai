"""
PDF Model - Database model for PDF file metadata.
"""
import logging
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger
from sqlalchemy.orm import relationship
from backend.models.database import Base

# Create logger
logger = logging.getLogger(__name__)


class PDFFile(Base):
    """Model for storing PDF file metadata."""
    
    __tablename__ = 'pdf_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False, default='application/pdf')
    status = Column(String(50), nullable=False, default='uploaded')  # uploaded, processed, error
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to MCQ
    mcqs = relationship('MCQ', back_populates='pdf', cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f"<PDFFile(id={self.id}, file_id={self.file_id}, original_filename={self.original_filename})>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'file_id': self.file_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'status': self.status,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'mcq_count': self.mcqs.count()
        }

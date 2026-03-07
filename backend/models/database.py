"""
Database configuration and models.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.config import Config

# Create logger
logger = logging.getLogger(__name__)

# Create Base for declarative models
Base = declarative_base()

# Create engine
engine = None
SessionLocal = None


def init_db(app=None):
    """
    Initialize database connection.
    
    Args:
        app: Flask application instance (optional)
    """
    global engine, SessionLocal
    
    try:
        # Get database URI from config
        if app:
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', Config.SQLALCHEMY_DATABASE_URI)
        else:
            db_uri = Config.SQLALCHEMY_DATABASE_URI
        
        logger.info(f"Initializing database: {db_uri}")
        
        # Create engine
        engine = create_engine(
            db_uri,
            echo=Config.FLASK_DEBUG,
            pool_pre_ping=True
        )
        
        # Create session factory
        SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )
        
        logger.info("Database initialized successfully")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_session():
    """
    Get a database session.
    
    Returns:
        Database session
    """
    if SessionLocal is None:
        init_db()
    return SessionLocal()


def close_session(exception=None):
    """
    Close database session after request.
    
    Args:
        exception: Any exception that occurred (optional)
    """
    if SessionLocal:
        SessionLocal.remove()
        logger.debug("Database session closed")


# ============== PDF Metadata Functions ==============

def save_pdf_metadata(file_id: str, original_filename: str, stored_filename: str, 
                       file_path: str, file_size: int, mime_type: str) -> 'PDFFile':
    """
    Save PDF file metadata to database.
    
    Args:
        file_id: Unique identifier for the file (UUID)
        original_filename: Original name of the uploaded file
        stored_filename: Unique filename used for storage
        file_path: Path where file is stored
        file_size: Size of file in bytes
        mime_type: MIME type of the file
    
    Returns:
        PDFFile: The created PDF file record
    """
    from backend.models.pdf_model import PDFFile
    
    session = get_session()
    try:
        pdf_file = PDFFile(
            file_id=file_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            status='uploaded'
        )
        session.add(pdf_file)
        session.commit()
        session.refresh(pdf_file)
        logger.info(f"PDF metadata saved: file_id={file_id}")
        return pdf_file
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save PDF metadata: {e}")
        raise
    finally:
        session.close()


def get_pdf_by_file_id(file_id: str) -> 'PDFFile':
    """
    Get PDF file metadata by file_id.
    
    Args:
        file_id: Unique identifier for the file (UUID)
    
    Returns:
        PDFFile: The PDF file record or None
    """
    from backend.models.pdf_model import PDFFile
    
    session = get_session()
    try:
        pdf_file = session.query(PDFFile).filter(PDFFile.file_id == file_id).first()
        return pdf_file
    except Exception as e:
        logger.error(f"Failed to get PDF metadata: {e}")
        raise
    finally:
        session.close()


def create_tables():
    """Create all database tables."""
    if engine is None:
        init_db()
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("All database tables created")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


# ============== PDF Model Functions ==============

def create_pdf(filename: str):
    """
    Create a new PDF record.
    
    Args:
        filename: Name of the PDF file
    
    Returns:
        PDFFile: The created PDF record
    """
    from backend.models.pdf_model import PDFFile
    
    session = get_session()
    try:
        pdf = PDFFile(filename=filename)
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        logger.info(f"PDF created: id={pdf.id}, filename={filename}")
        return pdf
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create PDF: {e}")
        raise
    finally:
        session.close()


def get_pdf_by_id(pdf_id: int):
    """
    Get PDF by ID.
    
    Args:
        pdf_id: PDF ID
    
    Returns:
        PDFFile: The PDF record or None
    """
    from backend.models.pdf_model import PDFFile
    
    session = get_session()
    try:
        return session.query(PDFFile).filter(PDFFile.id == pdf_id).first()
    except Exception as e:
        logger.error(f"Failed to get PDF: {e}")
        raise
    finally:
        session.close()


def get_all_pdfs() -> list:
    """
    Get all PDF records.
    
    Returns:
        List of PDFFile records
    """
    from backend.models.pdf_model import PDFFile
    
    session = get_session()
    try:
        return session.query(PDFFile).order_by(PDFFile.upload_date.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get PDFs: {e}")
        raise
    finally:
        session.close()


def delete_pdf(pdf_id: int) -> bool:
    """
    Delete a PDF and its MCQs.
    
    Args:
        pdf_id: PDF ID
    
    Returns:
        True if successful
    """
    from backend.models.pdf_model import PDFFile
    
    session = get_session()
    try:
        pdf = session.query(PDFFile).filter(PDFFile.id == pdf_id).first()
        if pdf:
            session.delete(pdf)
            session.commit()
            logger.info(f"PDF deleted: id={pdf_id}")
            return True
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete PDF: {e}")
        raise
    finally:
        session.close()


# ============== MCQ Model Functions ==============

def create_mcq(pdf_id: int, question: str, options: list, answer: str):
    """
    Create a new MCQ record.
    
    Args:
        pdf_id: ID of the parent PDF
        question: The question text
        options: List of 4 options
        answer: The correct answer
    
    Returns:
        MCQ: The created MCQ record
    """
    from backend.models.mcq_model import MCQ
    
    session = get_session()
    try:
        mcq = MCQ(
            pdf_id=pdf_id,
            question=question,
            options=options,
            answer=answer
        )
        session.add(mcq)
        session.commit()
        session.refresh(mcq)
        logger.info(f"MCQ created: id={mcq.id}, pdf_id={pdf_id}")
        return mcq
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create MCQ: {e}")
        raise
    finally:
        session.close()


def create_mcqs_bulk(pdf_id: int, mcqs: list) -> list:
    """
    Create multiple MCQ records.
    
    Args:
        pdf_id: ID of the parent PDF
        mcqs: List of MCQ dictionaries with question, options, answer
    
    Returns:
        List of created MCQ records
    """
    from backend.models.mcq_model import MCQ
    
    session = get_session()
    created = []
    try:
        for mcq_data in mcqs:
            mcq = MCQ(
                pdf_id=pdf_id,
                question=mcq_data.get('question', ''),
                options=mcq_data.get('options', []),
                answer=mcq_data.get('answer', '')
            )
            session.add(mcq)
            created.append(mcq)
        
        session.commit()
        for mcq in created:
            session.refresh(mcq)
        
        logger.info(f"Created {len(created)} MCQs for pdf_id={pdf_id}")
        return created
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create MCQs: {e}")
        raise
    finally:
        session.close()


def get_mcqs_by_pdf_id(pdf_id: int) -> list:
    """
    Get all MCQs for a PDF.
    
    Args:
        pdf_id: PDF ID
    
    Returns:
        List of MCQ records
    """
    from backend.models.mcq_model import MCQ
    
    session = get_session()
    try:
        return session.query(MCQ).filter(MCQ.pdf_id == pdf_id).all()
    except Exception as e:
        logger.error(f"Failed to get MCQs: {e}")
        raise
    finally:
        session.close()


def get_mcq_by_id(mcq_id: int):
    """
    Get MCQ by ID.
    
    Args:
        mcq_id: MCQ ID
    
    Returns:
        MCQ record or None
    """
    from backend.models.mcq_model import MCQ
    
    session = get_session()
    try:
        return session.query(MCQ).filter(MCQ.id == mcq_id).first()
    except Exception as e:
        logger.error(f"Failed to get MCQ: {e}")
        raise
    finally:
        session.close()


def delete_mcq(mcq_id: int) -> bool:
    """
    Delete an MCQ.
    
    Args:
        mcq_id: MCQ ID
    
    Returns:
        True if successful
    """
    from backend.models.mcq_model import MCQ
    
    session = get_session()
    try:
        mcq = session.query(MCQ).filter(MCQ.id == mcq_id).first()
        if mcq:
            session.delete(mcq)
            session.commit()
            logger.info(f"MCQ deleted: id={mcq_id}")
            return True
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete MCQ: {e}")
        raise
    finally:
        session.close()

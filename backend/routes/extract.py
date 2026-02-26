"""
Extract API route - handles MCQ extraction from PDFs.
"""
import logging
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from backend.utils.error_handler import ValidationError, NotFoundError
from backend.config import Config
from backend.services.ai_processor import AIProcessor
from backend.services.pdf_reader import PDFReader, PDFReadError, PDFNoTextError
from backend.services.json_formatter import JSONFormatter
from backend.services.storage_service import StorageService

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('extract', __name__)


@bp.route('/mcq', methods=['POST'])
def extract_mcq():
    """
    Extract MCQs from uploaded PDF file.
    
    Request body:
        file: PDF file (multipart/form-data)
    
    Returns:
        JSON response with extracted MCQs
    """
    logger.info("Starting MCQ extraction process")
    
    # Check if file is in request
    if 'file' not in request.files:
        logger.warning("No file provided in request")
        raise ValidationError("No file provided. Please upload a PDF file.")
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        logger.warning("Empty filename provided")
        raise ValidationError("No file selected. Please select a PDF file.")
    
    # Validate file extension
    if not file.filename.lower().endswith('.pdf'):
        logger.warning(f"Invalid file type: {file.filename}")
        raise ValidationError("Invalid file type. Only PDF files are allowed.")
    
    try:
        # Read PDF content
        pdf_reader = PDFReader()
        text_content = pdf_reader.read_pdf(file)
        logger.info(f"PDF read successfully, extracted {len(text_content)} characters")
        
        # Process with AI
        ai_processor = AIProcessor()
        raw_mcqs = ai_processor.extract_mcq(text_content)
        logger.info(f"Extracted {len(raw_mcqs)} MCQs from AI")
        
        # Format to JSON
        formatter = JSONFormatter()
        formatted_mcqs = formatter.format_mcq(raw_mcqs)
        logger.info("MCQs formatted successfully")
        
        return jsonify({
            'success': True,
            'message': 'MCQs extracted successfully',
            'mcqs': formatted_mcqs,
            'count': len(formatted_mcqs)
        }), 200
        
    except PDFNoTextError as e:
        logger.warning(f"PDF has no text (possibly scanned): {str(e)}")
        raise ValidationError(str(e))
    except PDFReadError as e:
        logger.error(f"PDF read error: {str(e)}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.exception(f"Error during MCQ extraction: {str(e)}")
        raise ValidationError(f"Failed to extract MCQs: {str(e)}")


@bp.route('/status/<task_id>', methods=['GET'])
def get_extraction_status(task_id: str):
    """
    Get the status of an extraction task.
    
    Args:
        task_id: ID of the extraction task
    
    Returns:
        JSON response with task status
    """
    logger.info(f"Checking status for task: {task_id}")
    
    # TODO: Implement task status checking with database
    return jsonify({
        'success': True,
        'task_id': task_id,
        'status': 'completed',
        'progress': 100
    }), 200


@bp.route('/<file_id>', methods=['GET', 'POST'])
def extract_text_from_file(file_id: str):
    """
    Extract text and MCQs from an uploaded PDF file by file_id.
    
    Args:
        file_id: Unique identifier of the uploaded file
    
    Returns:
        JSON response with extracted MCQs
    """
    logger.info(f"Starting MCQ extraction for file_id: {file_id}")
    
    # Validate file_id format
    if not file_id:
        logger.warning("No file_id provided")
        raise ValidationError("File ID is required.")
    
    try:
        # Initialize PDF reader
        pdf_reader = PDFReader()
        
        # Show processing status - reading PDF
        logger.info("Reading PDF file from storage...")
        
        # Read PDF from storage using file_id
        text_content, page_count = pdf_reader.read_pdf_from_storage(file_id)
        
        logger.info(f"PDF read successfully: {page_count} pages, {len(text_content)} characters")
        
        # Process with AI to extract MCQs
        logger.info("Extracting MCQs using AI...")
        ai_processor = AIProcessor()
        raw_mcqs = ai_processor.extract_mcq(text_content)
        logger.info(f"Extracted {len(raw_mcqs)} MCQs from AI")
        
        # Format to JSON
        formatter = JSONFormatter()
        formatted_mcqs = formatter.format_mcq(raw_mcqs)
        logger.info("MCQs formatted successfully")
        
        # Save JSON to storage
        try:
            storage = StorageService()
            json_content = json.dumps(formatted_mcqs, indent=2, ensure_ascii=False)
            storage.save_json_by_uuid(json_content, file_id)
            logger.info(f"JSON saved to storage for file_id: {file_id}")
        except Exception as save_error:
            logger.warning(f"Failed to save JSON to storage: {save_error}")
        
        return jsonify({
            'success': True,
            'message': 'MCQs extracted successfully',
            'file_id': file_id,
            'mcqs': formatted_mcqs,
            'count': len(formatted_mcqs)
        }), 200
        
    except PDFNoTextError as e:
        logger.warning(f"PDF has no text (possibly scanned): {str(e)}")
        raise ValidationError(str(e))
    except PDFReadError as e:
        logger.error(f"PDF read error: {str(e)}")
        raise ValidationError(str(e))
    except ValueError as e:
        logger.warning(f"Validation error during MCQ extraction: {str(e)}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.exception(f"Error during MCQ extraction: {str(e)}")
        raise ValidationError(f"Failed to extract MCQs: {str(e)}")

"""
Extract API route - handles MCQ extraction from PDFs.
"""
import logging
import json
import threading
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from backend.utils.error_handler import ValidationError, NotFoundError
from backend.config import Config
from backend.services.ai_processor import AIProcessor
from backend.services.pdf_reader import PDFReader, PDFReadError, PDFNoTextError
from backend.services.json_formatter import JSONFormatter
from backend.services.storage_service import StorageService
from backend.services.job_manager import (
    get_job_manager,
    STAGE_READING_PDF,
    STAGE_EXTRACTING_TEXT,
    STAGE_AI_PROCESSING,
    STAGE_FORMATTING,
    STAGE_SAVING,
    STAGE_COMPLETED,
    JOB_STATUS_PROCESSING
)

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('extract', __name__)


def process_extraction_background(job_id: str, file_id: str):
    """
    Background task to process MCQ extraction.
    This runs in a separate thread to avoid blocking the request.
    
    Args:
        job_id: The job identifier
        file_id: The file_id to process
    """
    job_manager = get_job_manager()
    
    try:
        # Mark as processing
        job_manager.set_processing(job_id)
        logger.info(f"Starting background extraction for job {job_id}, file {file_id}")
        
        # Stage 1: Read PDF from storage
        job_manager.set_progress(
            job_id,
            stage=STAGE_READING_PDF,
            progress=10,
            message='Reading PDF file from storage...',
            pages_processed=0
        )
        
        pdf_reader = PDFReader()
        text_content, page_count = pdf_reader.read_pdf_from_storage(file_id)
        
        job_manager.set_progress(
            job_id,
            stage=STAGE_EXTRACTING_TEXT,
            progress=25,
            message=f'Extracted {len(text_content)} characters from {page_count} pages',
            pages_processed=page_count,
            total_pages=page_count
        )
        
        # Stage 2: AI Processing
        job_manager.set_progress(
            job_id,
            stage=STAGE_AI_PROCESSING,
            progress=30,
            message='Processing with AI to extract MCQs...',
            pages_processed=page_count,
            total_pages=page_count,
            mcqs_found=0
        )
        
        ai_processor = AIProcessor()
        raw_mcqs = ai_processor.extract_mcq(text_content)
        
        job_manager.set_progress(
            job_id,
            stage=STAGE_FORMATTING,
            progress=70,
            message=f'Extracted {len(raw_mcqs)} MCQs, formatting...',
            pages_processed=page_count,
            total_pages=page_count,
            mcqs_found=len(raw_mcqs)
        )
        
        # Stage 3: Format MCQs
        formatter = JSONFormatter()
        formatted_mcqs = formatter.format_mcq(raw_mcqs)
        
        job_manager.set_progress(
            job_id,
            stage=STAGE_SAVING,
            progress=85,
            message='Saving MCQs to storage...',
            pages_processed=page_count,
            total_pages=page_count,
            mcqs_found=len(formatted_mcqs)
        )
        
        # Stage 4: Save to storage
        storage = StorageService()
        json_content = json.dumps(formatted_mcqs, indent=2, ensure_ascii=False)
        storage.save_json_by_uuid(json_content, file_id)
        
        # Mark as completed
        result = {
            'mcqs': formatted_mcqs,
            'count': len(formatted_mcqs),
            'file_id': file_id
        }
        
        job_manager.set_completed(job_id, result)
        logger.info(f"Job {job_id} completed successfully with {len(formatted_mcqs)} MCQs")
        
    except PDFNoTextError as e:
        logger.warning(f"PDF has no text (possibly scanned): {str(e)}")
        job_manager.set_failed(job_id, f"PDF has no text: {str(e)}")
        
    except PDFReadError as e:
        logger.error(f"PDF read error: {str(e)}")
        job_manager.set_failed(job_id, f"Failed to read PDF: {str(e)}")
        
    except Exception as e:
        logger.exception(f"Error during background extraction: {str(e)}")
        job_manager.set_failed(job_id, f"Extraction failed: {str(e)}")


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
    
    # Increment view count
    try:
        from backend.routes.stats import increment_view
        increment_view()
    except Exception as e:
        logger.warning(f"Could not increment view count: {e}")
    
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
    Get or start extraction for a PDF file by file_id.
    - GET: Returns cached MCQs if available
    - POST: Starts background extraction, returns job_id
    
    Args:
        file_id: Unique identifier of the uploaded file
    
    Returns:
        JSON response with MCQs or job_id
    """
    logger.info(f"Handling extraction request for file_id: {file_id}")
    
    # Validate file_id format
    if not file_id:
        logger.warning("No file_id provided")
        raise ValidationError("File ID is required.")
    
    try:
        # FIRST: Check if JSON already exists (cache) - avoid duplicate API calls
        storage = StorageService()
        existing_json = storage.get_json_by_uuid(file_id)
        
        if existing_json:
            # Return cached results - no need to start background job
            logger.info(f"Returning cached MCQs for file_id: {file_id}")
            try:
                cached_mcqs = json.loads(existing_json)
                return jsonify({
                    'success': True,
                    'message': 'MCQs loaded from cache',
                    'file_id': file_id,
                    'mcqs': cached_mcqs,
                    'count': len(cached_mcqs),
                    'cached': True
                }), 200
            except json.JSONDecodeError:
                logger.warning("Failed to parse cached JSON, will re-extract")
        
        # For GET requests without cache, return error
        if request.method == 'GET':
            raise ValidationError("No cached MCQs found. Please upload the file first.")
        
        # For POST requests without cache, start background extraction
        # Create a new background job
        job_manager = get_job_manager()
        job_id = job_manager.create_job(
            file_id=file_id,
            metadata={'source': 'api_extract'}
        )
        
        logger.info(f"Created job {job_id} for file {file_id}, starting background thread")
        
        # Start background processing in a separate thread
        thread = threading.Thread(
            target=process_extraction_background,
            args=(job_id, file_id),
            daemon=True  # Thread will be terminated when main program exits
        )
        thread.start()
        
        # Return immediately with job_id
        return jsonify({
            'success': True,
            'message': 'Extraction started in background',
            'job_id': job_id,
            'status': 'processing',
            'file_id': file_id
        }), 202  # 202 Accepted - request accepted for processing
        
    except ValidationError:
        raise
    except Exception as e:
        logger.exception(f"Error starting background extraction: {str(e)}")
        raise ValidationError(f"Failed to start extraction: {str(e)}")

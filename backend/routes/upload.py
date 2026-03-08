"""
Upload API route - handles file uploads.
"""
import logging
import uuid
import time
from collections import defaultdict
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from backend.utils.file_validator import FileValidator
from backend.config import Config
from backend.services.storage_service import StorageService
from backend.models.database import save_pdf_metadata

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('upload', __name__)

# Maximum file size (20MB from config)
MAX_FILE_SIZE = Config.MAX_CONTENT_LENGTH

# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = 15  # 15 uploads per minute per IP
rate_limit_store = defaultdict(list)  # IP -> list of timestamps


def check_rate_limit(ip: str) -> bool:
    """
    Check if IP has exceeded rate limit.
    
    Args:
        ip: Client IP address
    
    Returns:
        True if within limit, False if exceeded
    """
    current_time = time.time()
    # Remove timestamps older than 1 minute
    rate_limit_store[ip] = [
        ts for ts in rate_limit_store[ip] 
        if current_time - ts < 60
    ]
    
    if len(rate_limit_store[ip]) >= RATE_LIMIT_PER_MINUTE:
        return False
    
    # Add current timestamp
    rate_limit_store[ip].append(current_time)
    return True


def cleanup_old_files():
    """
    Clean up PDF files older than 1 hour.
    This prevents disk storage overflow on Render.
    """
    try:
        from pathlib import Path
        import time as time_module
        
        upload_folder = Config.UPLOAD_FOLDER
        if not upload_folder.exists():
            return
        
        current_time = time_module.time()
        cutoff_time = current_time - 3600  # 1 hour ago
        
        deleted_count = 0
        for file_path in upload_folder.glob("*.pdf"):
            try:
                # Check file modification time
                file_mtime = file_path.stat().st_mtime
                if file_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Cleaned up old file: {file_path.name}")
            except Exception as e:
                logger.warning(f"Failed to delete old file {file_path.name}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old PDF files")
            
    except Exception as e:
        logger.error(f"Error during file cleanup: {e}")


def create_error_response(message: str, status_code: int = 400):
    """
    Create standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
    
    Returns:
        Tuple of (response, status_code)
    """
    return jsonify({
        'success': False,
        'message': message
    }), status_code


# Run cleanup on module load
cleanup_old_files()


@bp.route('/file', methods=['POST'])
def upload_file():
    """
    Upload a PDF file to the server.
    
    Request body:
        file: PDF file (multipart/form-data)
    
    Returns:
        JSON response with file upload confirmation
    """
    logger.info("[DIAG] Entered upload_file route")
    
    try:
        # Check rate limit
        client_ip = request.remote_addr or 'unknown'
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return create_error_response(
                "Rate limit exceeded. Maximum 15 uploads per minute allowed.",
                429
            )
        
        # Initialize validator
        validator = FileValidator()

        # Check if file is in request
        if 'file' not in request.files:
            logger.warning("No file provided in request")
            return create_error_response(
                "No file provided. Please upload a PDF file.",
                400
            )

        file = request.files['file']

        # Check if file was selected
        if file.filename == '':
            logger.warning("Empty filename provided")
            return create_error_response(
                "No file selected. Please select a PDF file.",
                400
            )

        # Validate file extension using file_validator
        ext_result = validator.validate_extension(file.filename)
        if not ext_result['valid']:
            logger.warning(f"Invalid file extension: {file.filename}")
            return create_error_response("Only PDF files are allowed.", 400)

        # Validate MIME type using file_validator
        mime_result = validator.validate_mime_type(file)
        if not mime_result['valid']:
            logger.warning(f"Invalid MIME type: {file.content_type}")
            return create_error_response("Only PDF files are allowed.", 400)

        # Validate file size using file_validator
        size_result = validator.validate_file_size(file)
        if not size_result['valid']:
            logger.warning(f"File size validation failed: {size_result['message']}")
            return create_error_response(
                f"File too large. Maximum size is 20MB.",
                400
            )

        try:
            # Generate unique filename using UUID
            original_filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            unique_filename = f"{file_id}_{original_filename}"

            # Save file using storage service
            storage = StorageService()
            file_path = storage.save_upload(file, unique_filename)
            logger.info(f"File saved successfully: {file_path}")

            # Validate page count after saving
            page_result = validator.validate_page_count(str(file_path))
            if not page_result['valid']:
                # Delete the file since it exceeds page limit
                storage.delete_file(file_path)
                logger.warning(f"Page count validation failed: {page_result['message']}")
                return create_error_response(
                    f"PDF exceeds maximum page limit (50 pages).",
                    400
                )

            # Save file metadata to database
            try:
                save_pdf_metadata(
                    file_id=file_id,
                    original_filename=original_filename,
                    stored_filename=unique_filename,
                    file_path=str(file_path),
                    file_size=size_result['details']['file_size'],
                    mime_type='application/pdf'
                )
                logger.info(f"File metadata saved to database: file_id={file_id}")
            except Exception as db_error:
                logger.error(f"Failed to save file metadata: {db_error}")

            # EXTRACT MCQs IMMEDIATELY - in same request
            extracted_mcqs = []
            extraction_success = True
            extraction_error = None
            
            try:
                from backend.services.pdf_reader import PDFReader
                from backend.services.ai_processor import AIProcessor
                from backend.services.json_formatter import JSONFormatter
                import json

                # Read PDF
                pdf_reader = PDFReader()
                text_content = pdf_reader.read_pdf_from_storage(file_id)
                logger.info(f"PDF read for extraction: {len(text_content[0])} characters")

                # Extract MCQs using AI
                ai_processor = AIProcessor()
                raw_mcqs = ai_processor.extract_mcq(text_content[0])
                logger.info(f"Extracted {len(raw_mcqs)} MCQs from AI")

                # Format MCQs
                formatter = JSONFormatter()
                formatted_mcqs = formatter.format_mcq(raw_mcqs)
                
                # Save JSON to storage
                json_content = json.dumps(formatted_mcqs, indent=2, ensure_ascii=False)
                storage.save_json_by_uuid(json_content, file_id)
                logger.info(f"MCQs saved to storage for file_id: {file_id}")
                
                extracted_mcqs = formatted_mcqs

            except Exception as extract_error:
                logger.error(f"Error during extraction: {extract_error}")
                extraction_success = False
                extraction_error = str(extract_error)
            
            # Cleanup: Delete temporary PDF file after processing
            try:
                storage.delete_file(file_path)
                logger.info(f"Temporary PDF file deleted: {file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temporary file: {cleanup_error}")

            # Run cleanup of old files periodically
            cleanup_old_files()

            if extraction_success:
                return jsonify({
                    'success': True,
                    'message': 'File uploaded and MCQs extracted successfully',
                    'file_id': file_id,
                    'mcqs': extracted_mcqs,
                    'count': len(extracted_mcqs)
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': 'File uploaded successfully. MCQ extraction failed.',
                    'file_id': file_id,
                    'mcqs': [],
                    'count': 0,
                    'extraction_error': extraction_error
                }), 200

        except Exception as e:
            logger.exception(f"Error during file upload: {str(e)}")
            return create_error_response(
                f"Failed to upload file: {str(e)}",
                500
            )

    except Exception as outer_e:
        logger.exception(f"[DIAG] Unhandled exception in upload_file: {str(outer_e)}")
        return create_error_response(
            "An unexpected error occurred. Please try again.",
            500
        )


@bp.route('/validate', methods=['POST'])
def validate_upload():
    """
    Validate an uploaded PDF file.
    
    Request body:
        file: PDF file (multipart/form-data)
    
    Returns:
        JSON response with validation result
    """
    logger.info("Starting file validation")
    
    # Check rate limit
    client_ip = request.remote_addr or 'unknown'
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return create_error_response(
            "Rate limit exceeded. Maximum 15 uploads per minute allowed.",
            429
        )
    
    # Initialize validator
    validator = FileValidator()
    
    # Check if file is in request
    if 'file' not in request.files:
        logger.warning("No file provided in request")
        return create_error_response(
            "No file provided. Please upload a PDF file.",
            400
        )
    
    file = request.files['file']
    
    # Validate using file_validator
    ext_result = validator.validate_extension(file.filename)
    mime_result = validator.validate_mime_type(file)
    size_result = validator.validate_file_size(file)
    
    is_valid = ext_result['valid'] and mime_result['valid'] and size_result['valid']
    
    if is_valid:
        return jsonify({
            'success': True,
            'message': 'File is valid'
        }), 200
    else:
        # Return the first error message
        if not ext_result['valid']:
            message = ext_result['message']
        elif not mime_result['valid']:
            message = mime_result['message']
        else:
            message = size_result['message']
            
        return create_error_response(message, 400)


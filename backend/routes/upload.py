"""
Upload API route - handles file uploads.
"""
import logging
import uuid
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

# Maximum file size (10MB from config)
MAX_FILE_SIZE = Config.MAX_CONTENT_LENGTH


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
        # Initialize validator
        validator = FileValidator()

        # Check if file is in request
        if 'file' not in request.files:
            logger.warning("No file provided in request")
            return jsonify({
                'status': 'error',
                'message': 'No file provided. Please upload a PDF file.',
                'file_id': ''
            }), 400

        file = request.files['file']

        # Check if file was selected
        if file.filename == '':
            logger.warning("Empty filename provided")
            return jsonify({
                'status': 'error',
                'message': 'No file selected. Please select a PDF file.',
                'file_id': ''
            }), 400

        # Validate file extension using file_validator
        ext_result = validator.validate_extension(file.filename)
        if not ext_result['valid']:
            logger.warning(f"Invalid file extension: {file.filename}")
            return jsonify({
                'status': 'error',
                'message': ext_result['message'],
                'file_id': ''
            }), 400

        # Validate MIME type using file_validator
        mime_result = validator.validate_mime_type(file)
        if not mime_result['valid']:
            logger.warning(f"Invalid MIME type: {file.content_type}")
            return jsonify({
                'status': 'error',
                'message': mime_result['message'],
                'file_id': ''
            }), 400

        # Validate file size using file_validator
        size_result = validator.validate_file_size(file)
        if not size_result['valid']:
            logger.warning(f"File size validation failed: {size_result['message']}")
            return jsonify({
                'status': 'error',
                'message': size_result['message'],
                'file_id': ''
            }), 400

        try:
            # Generate unique filename using UUID
            original_filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            unique_filename = f"{file_id}_{original_filename}"

            # Save file using storage service
            storage = StorageService()
            file_path = storage.save_upload(file, unique_filename)
            logger.info(f"File saved successfully: {file_path}")

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
                # Still return success since file was saved, but log the error

            return jsonify({
                'status': 'success',
                'message': 'File uploaded successfully',
                'file_id': file_id
            }), 200

        except Exception as e:
            logger.exception(f"Error during file upload: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to upload file: {str(e)}',
                'file_id': ''
            }), 500

    except Exception as outer_e:
        logger.exception(f"[DIAG] Unhandled exception in upload_file: {str(outer_e)}")
        return jsonify({
            'status': 'error',
            'message': f'Critical error in upload_file: {str(outer_e)}',
            'file_id': ''
        }), 500


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
    
    # Initialize validator
    validator = FileValidator()
    
    # Check if file is in request
    if 'file' not in request.files:
        logger.warning("No file provided in request")
        return jsonify({
            'status': 'error',
            'message': 'No file provided. Please upload a PDF file.',
            'valid': False
        }), 400
    
    file = request.files['file']
    
    # Validate using file_validator
    ext_result = validator.validate_extension(file.filename)
    mime_result = validator.validate_mime_type(file)
    size_result = validator.validate_file_size(file)
    
    is_valid = ext_result['valid'] and mime_result['valid'] and size_result['valid']
    
    if is_valid:
        return jsonify({
            'status': 'success',
            'valid': True,
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
            
        return jsonify({
            'status': 'error',
            'valid': False,
            'message': message
        }), 400

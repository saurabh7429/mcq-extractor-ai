"""
Download API route - handles file downloads.
"""
import logging
from flask import Blueprint, jsonify, request, send_file
from backend.utils.error_handler import ValidationError, NotFoundError
from backend.config import Config
from backend.services.storage_service import StorageService

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('download', __name__)


@bp.route('/json/<file_id>', methods=['GET'])
def download_json(file_id: str):
    """
    Download a generated JSON file by file_id (UUID).
    
    Args:
        file_id: The UUID of the file to download
    
    Returns:
        JSON file as attachment
    """
    logger.info(f"Download request for JSON: {file_id}")
    
    try:
        storage = StorageService()
        
        # Check if it's a UUID (no .json extension)
        if '.' not in file_id:
            # Try as UUID first
            file_path = storage.get_json_by_uuid(file_id)
            if file_path and file_path.exists():
                return send_file(
                    file_path,
                    mimetype='application/json',
                    as_attachment=True,
                    download_name=f"{file_id}.json"
                )
            # If not found as UUID, try with .json extension
            file_id = f"{file_id}.json"
        
        # Look for file by name
        file_path = storage.get_json_path(file_id)
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_id}")
            raise NotFoundError(f"File not found: {file_id}")
        
        return send_file(
            file_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=file_id
        )
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"Error during download: {str(e)}")
        raise ValidationError(f"Failed to download file: {str(e)}")


@bp.route('/pdf/<filename>', methods=['GET'])
def download_pdf(filename: str):
    """
    Download an uploaded PDF file.
    
    Args:
        filename: Name of the PDF file to download
    
    Returns:
        PDF file as attachment
    """
    logger.info(f"Download request for PDF: {filename}")
    
    try:
        storage = StorageService()
        file_path = storage.get_pdf_path(filename)
        
        if not file_path.exists():
            logger.warning(f"File not found: {filename}")
            raise NotFoundError(f"File not found: {filename}")
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"Error during download: {str(e)}")
        raise ValidationError(f"Failed to download file: {str(e)}")


@bp.route('/list', methods=['GET'])
def list_files():
    """
    List all available files for download.
    
    Returns:
        JSON response with list of files
    """
    logger.info("Listing available files")
    
    try:
        storage = StorageService()
        json_files = storage.list_json_files()
        pdf_files = storage.list_pdf_files()
        
        return jsonify({
            'success': True,
            'data': {
                'json_files': json_files,
                'pdf_files': pdf_files
            }
        }), 200
        
    except Exception as e:
        logger.exception(f"Error listing files: {str(e)}")
        raise ValidationError(f"Failed to list files: {str(e)}")

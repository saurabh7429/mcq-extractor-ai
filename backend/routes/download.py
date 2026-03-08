"""
Download API route - handles file downloads and exports.
"""
import logging
import io
from flask import Blueprint, jsonify, request, send_file
from backend.utils.error_handler import ValidationError, NotFoundError
from backend.config import Config
from backend.services.storage_service import StorageService
from backend.services.export_service import ExportService

logger = logging.getLogger(__name__)
bp = Blueprint('download', __name__)

@bp.route('/<file_id>', methods=['GET'])
def download_json_by_id(file_id: str):
    logger.info(f"Download request for file_id: {file_id}")
    try:
        storage = StorageService()
        file_path = storage.get_json_by_uuid(file_id)
        if not file_path:
            return jsonify({'success': False, 'message': 'File not found', 'file_id': file_id}), 404
        filename = file_path.name
        return send_file(file_path, mimetype='application/json', as_attachment=True, download_name=filename)
    except Exception as e:
        logger.exception(f"Error during download: {str(e)}")
        return jsonify({'success': False, 'message': f'Failed to download file: {str(e)}', 'file_id': file_id}), 500

@bp.route('/json/<filename>', methods=['GET'])
def download_json(filename: str):
    logger.info(f"Download request for JSON: {filename}")
    try:
        storage = StorageService()
        file_path = storage.get_json_path(filename)
        if not file_path.exists():
            raise NotFoundError(f"File not found: {filename}")
        return send_file(file_path, mimetype='application/json', as_attachment=True, download_name=filename)
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"Error during download: {str(e)}")
        raise ValidationError(f"Failed to download file: {str(e)}")

@bp.route('/pdf/<filename>', methods=['GET'])
def download_pdf(filename: str):
    logger.info(f"Download request for PDF: {filename}")
    try:
        storage = StorageService()
        file_path = storage.get_pdf_path(filename)
        if not file_path.exists():
            raise NotFoundError(f"File not found: {filename}")
        return send_file(file_path, mimetype='application/pdf', as_attachment=True, download_name=filename)
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(f"Error during download: {str(e)}")
        raise ValidationError(f"Failed to download file: {str(e)}")

@bp.route('/list', methods=['GET'])
def list_files():
    logger.info("Listing available files")
    try:
        storage = StorageService()
        json_files = storage.list_json_files()
        pdf_files = storage.list_pdf_files()
        return jsonify({'success': True, 'data': {'json_files': json_files, 'pdf_files': pdf_files}}), 200
    except Exception as e:
        logger.exception(f"Error listing files: {str(e)}")
        raise ValidationError(f"Failed to list files: {str(e)}")

@bp.route('/export/<format>/<file_id>', methods=['GET'])
def export_format(format: str, file_id: str):
    """Export MCQs to specified format."""
    logger.info(f"Export request: format={format}, file_id={file_id}")
    try:
        export_service = ExportService()
        content = export_service.export(file_id, format)
        
        format_info = {
            'json': ('application/json', 'json'),
            'csv': ('text/csv', 'csv'),
            'txt': ('text/plain', 'txt'),
            'markdown': ('text/markdown', 'md'),
            'html': ('text/html', 'html'),
            'xml': ('application/xml', 'xml'),
            'yaml': ('text/yaml', 'yaml'),
            'sql': ('application/sql', 'sql'),
            'aiken': ('text/plain', 'txt'),
            'gift': ('text/plain', 'txt'),
            'excel': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'),
            # New print-ready formats
            'question_pdf': ('application/pdf', 'pdf'),
            'answer_key_pdf': ('application/pdf', 'pdf'),
            'omr_pdf': ('application/pdf', 'pdf'),
            'tabular_pdf': ('application/pdf', 'pdf'),
            'docx': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx')
        }
        
        mimetype, ext = format_info.get(format.lower(), ('application/json', 'json'))
        filename = f"{file_id}.{ext}"
        
        if isinstance(content, bytes):
            file_stream = io.BytesIO(content)
        else:
            file_stream = io.BytesIO(content.encode('utf-8'))
        
        return send_file(file_stream, mimetype=mimetype, as_attachment=True, download_name=filename)
    except ValueError as e:
        logger.warning(f"Export validation error: {str(e)}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.exception(f"Error during export: {str(e)}")
        raise ValidationError(f"Failed to export: {str(e)}")

@bp.route('/export/formats', methods=['GET'])
def get_export_formats():
    """Get list of supported export formats."""
    try:
        export_service = ExportService()
        formats = export_service.get_supported_formats()
        return jsonify({'success': True, 'formats': formats}), 200
    except Exception as e:
        logger.exception(f"Error getting formats: {str(e)}")
        raise ValidationError(f"Failed to get formats: {str(e)}")

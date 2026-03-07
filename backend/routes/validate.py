"""
Validate API route - handles validation of files and MCQs.
"""
import logging
from flask import Blueprint, jsonify, request
from backend.utils.error_handler import ValidationError
from backend.utils.file_validator import FileValidator
from backend.services.json_formatter import JSONFormatter

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('validate', __name__)


@bp.route('/file', methods=['POST'])
def validate_file():
    """Validate an uploaded PDF file."""
    logger.info("Starting file validation")
    
    if 'file' not in request.files:
        logger.warning("No file provided in request")
        raise ValidationError("No file provided. Please upload a PDF file.")
    
    file = request.files['file']
    validator = FileValidator()
    result = validator.validate_pdf(file)
    
    return jsonify({
        'success': True,
        'valid': result['valid'],
        'message': result['message'],
        'details': result.get('details', {})
    }), 200


@bp.route('/mcq', methods=['POST'])
def validate_mcq():
    """Validate MCQ JSON data with new schema."""
    logger.info("Starting MCQ validation")
    
    if not request.is_json:
        logger.warning("Request is not JSON")
        raise ValidationError("Request must be JSON.")
    
    data = request.get_json()
    
    # Handle both old format (mcqs array) and new format (direct array)
    if isinstance(data, list):
        mcqs = data
    elif 'mcqs' in data:
        mcqs = data.get('mcqs', [])
    elif 'questions' in data:
        mcqs = data.get('questions', [])
    else:
        raise ValidationError("Invalid format. Provide MCQ array or object with 'mcqs' key.")
    
    # Validate using JSONFormatter which enforces the schema
    formatter = JSONFormatter()
    formatted_mcqs = formatter.format_mcq(mcqs)
    
    invalid_count = len(mcqs) - len(formatted_mcqs)
    
    return jsonify({
        'success': True,
        'valid': len(formatted_mcqs) > 0,
        'message': f'Validated {len(formatted_mcqs)} MCQs, {invalid_count} discarded',
        'count': len(formatted_mcqs),
        'invalid_count': invalid_count,
        'mcqs': formatted_mcqs
    }), 200


@bp.route('/schema', methods=['GET'])
def get_schema():
    """Get the expected MCQ JSON schema."""
    logger.info("Providing MCQ schema")
    
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "Auto-assigned incremental ID"},
            "question": {"type": "string", "description": "The MCQ question text"},
            "options": {
                "type": "array", 
                "items": {"type": "string"},
                "minItems": 4,
                "maxItems": 4,
                "description": "Exactly 4 options"
            },
            "answer": {"type": "string", "description": "The correct answer (must match one option)"}
        },
        "required": ["id", "question", "options", "answer"]
    }
    
    example = {
        "mcqs": [
            {
                "id": 1,
                "question": "What is the capital of France?",
                "options": ["London", "Paris", "Berlin", "Madrid"],
                "answer": "Paris"
            }
        ]
    }
    
    return jsonify({
        'success': True,
        'schema': schema,
        'example': example
    }), 200

"""
File Validator - validates files and MCQ data.
"""
import logging
from typing import Dict, Any, List

# Create logger
logger = logging.getLogger(__name__)


class FileValidator:
    """Handles validation of files and MCQ data."""
    
    ALLOWED_EXTENSIONS = {'pdf'}
    ALLOWED_MIME_TYPES = {'application/pdf'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        """Initialize file validator."""
        logger.info("File Validator initialized")
    
    def validate_extension(self, filename: str) -> Dict[str, Any]:
        """
        Validate file extension.
        
        Args:
            filename: Name of the file to validate
        
        Returns:
            Dictionary with validation result
        """
        result = {
            'valid': False,
            'message': '',
            'details': {}
        }
        
        if not filename:
            result['message'] = 'No filename provided'
            return result
        
        # Get file extension
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if extension not in self.ALLOWED_EXTENSIONS:
            result['message'] = f'Invalid file extension: .{extension}. Only PDF files are allowed.'
            return result
        
        result['valid'] = True
        result['message'] = 'Valid file extension'
        result['details'] = {
            'extension': extension,
            'allowed_extensions': list(self.ALLOWED_EXTENSIONS)
        }
        
        return result
    
    def validate_mime_type(self, file) -> Dict[str, Any]:
        """
        Validate file MIME type.
        
        Args:
            file: File object to validate
        
        Returns:
            Dictionary with validation result
        """
        result = {
            'valid': False,
            'message': '',
            'details': {}
        }
        
        if not file:
            result['message'] = 'No file provided'
            return result
        
        # Get content type from file
        content_type = file.content_type
        
        if not content_type:
            result['message'] = 'No content type provided'
            return result
        
        if content_type not in self.ALLOWED_MIME_TYPES:
            result['message'] = f'Invalid MIME type: {content_type}. Only PDF files are allowed.'
            return result
        
        result['valid'] = True
        result['message'] = 'Valid MIME type'
        result['details'] = {
            'mime_type': content_type,
            'allowed_mime_types': list(self.ALLOWED_MIME_TYPES)
        }
        
        return result
    
    def validate_file_size(self, file) -> Dict[str, Any]:
        """
        Validate file size.
        
        Args:
            file: File object to validate
        
        Returns:
            Dictionary with validation result
        """
        result = {
            'valid': False,
            'message': '',
            'details': {}
        }
        
        if not file:
            result['message'] = 'No file provided'
            return result
        
        # Seek to end to get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size == 0:
            result['message'] = 'Empty file. Please upload a valid PDF file.'
            return result
        
        if file_size > self.MAX_FILE_SIZE:
            max_size_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            result['message'] = f'File too large. Maximum size is {max_size_mb:.0f}MB.'
            result['details'] = {
                'file_size': file_size,
                'max_size': self.MAX_FILE_SIZE,
                'max_size_mb': max_size_mb
            }
            return result
        
        result['valid'] = True
        result['message'] = 'Valid file size'
        result['details'] = {
            'file_size': file_size,
            'max_size': self.MAX_FILE_SIZE
        }
        
        return result
    
    def validate_pdf(self, file) -> Dict[str, Any]:
        """
        Validate a PDF file.
        
        Args:
            file: File to validate
        
        Returns:
            Dictionary with validation result
        """
        result = {
            'valid': False,
            'message': '',
            'details': {}
        }
        
        # Check if file exists
        if not file:
            result['message'] = 'No file provided'
            return result
        
        # Check filename
        filename = file.filename
        if not filename:
            result['message'] = 'No filename provided'
            return result
        
        # Check extension
        if not filename.lower().endswith('.pdf'):
            result['message'] = 'Invalid file type. Only PDF files are allowed.'
            return result
        
        # Check content type if available
        content_type = file.content_type
        if content_type and content_type not in self.ALLOWED_MIME_TYPES:
            result['message'] = f'Invalid content type: {content_type}'
            return result
        
        result['valid'] = True
        result['message'] = 'File is valid'
        result['details'] = {
            'filename': filename,
            'size': file.content_length
        }
        
        return result
    
    def validate_mcq_list(self, mcqs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a list of MCQs.
        
        Args:
            mcqs: List of MCQ dictionaries
        
        Returns:
            Dictionary with validation result
        """
        result = {
            'valid': False,
            'message': '',
            'errors': []
        }
        
        if not mcqs:
            result['message'] = 'No MCQs provided'
            result['errors'].append('Empty MCQ list')
            return result
        
        errors = []
        
        for idx, mcq in enumerate(mcqs):
            mcq_errors = self._validate_single_mcq(mcq, idx)
            errors.extend(mcq_errors)
        
        if errors:
            result['message'] = f'Found {len(errors)} validation errors'
            result['errors'] = errors
        else:
            result['valid'] = True
            result['message'] = f'All {len(mcqs)} MCQs are valid'
        
        return result
    
    def _validate_single_mcq(self, mcq: Dict[str, Any], index: int) -> List[str]:
        """
        Validate a single MCQ.
        
        Args:
            mcq: MCQ dictionary
            index: Index of MCQ in list
        
        Returns:
            List of error messages
        """
        errors = []
        prefix = f"MCQ {index + 1}:"
        
        # Check required fields
        if 'question' not in mcq or not mcq['question']:
            errors.append(f"{prefix} Missing or empty 'question' field")
        
        if 'options' not in mcq or not mcq['options']:
            errors.append(f"{prefix} Missing or empty 'options' field")
        elif len(mcq['options']) < 2:
            errors.append(f"{prefix} At least 2 options required, found {len(mcq['options'])}")
        
        if 'correct_answer' not in mcq:
            errors.append(f"{prefix} Missing 'correct_answer' field")
        elif mcq.get('options') and mcq['correct_answer'] >= len(mcq['options']):
            errors.append(f"{prefix} correct_answer index out of range")
        
        return errors
    
    def validate_json_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON data against expected schema.
        
        Args:
            data: Data to validate
        
        Returns:
            Dictionary with validation result
        """
        result = {
            'valid': False,
            'message': ''
        }
        
        if not isinstance(data, dict):
            result['message'] = 'Data must be a JSON object'
            return result
        
        if 'mcqs' not in data:
            result['message'] = "Missing 'mcqs' key"
            return result
        
        if not isinstance(data['mcqs'], list):
            result['message'] = "'mcqs' must be an array"
            return result
        
        result['valid'] = True
        result['message'] = 'Valid JSON schema'
        
        return result

"""
Global error handler for the Flask application.
Provides structured error responses and logging.
"""
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
from typing import Tuple, Dict, Any

# Create logger
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base custom exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 500, payload: Dict[str, Any] = None):
        """
        Initialize API error.
        
        Args:
            message: Error message (user-friendly)
            status_code: HTTP status code
            payload: Additional error data
        """
        super().__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        error_dict = dict(self.payload)
        error_dict['error'] = self.message
        error_dict['status_code'] = self.status_code
        # Add helpful suggestions based on error type
        error_dict['suggestion'] = self._get_suggestion()
        return error_dict
    
    def _get_suggestion(self) -> str:
        """Get helpful suggestion based on error message."""
        msg_lower = self.message.lower()
        
        if 'no text found' in msg_lower or 'scanned' in msg_lower:
            return "Try using a text-based PDF or install OCR dependencies: pip install pytesseract pdf2image"
        elif 'pdf' in msg_lower and ('not found' in msg_lower or 'invalid' in msg_lower):
            return "Please upload a valid PDF file. The file may be corrupted or password protected."
        elif 'api' in msg_lower and 'key' in msg_lower:
            return "Please check your GEMINI_API_KEY in the .env file."
        elif 'database' in msg_lower or 'db' in msg_lower:
            return "Please restart the server to initialize the database."
        elif 'connection' in msg_lower or 'network' in msg_lower:
            return "Please check your internet connection and try again."
        else:
            return "Please try again or contact support if the problem persists."


class ValidationError(APIError):
    """Exception for validation errors (400)."""
    
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(APIError):
    """Exception for not found errors (404)."""
    
    def __init__(self, message: str = "Resource not found", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=404, payload=payload)


class UnauthorizedError(APIError):
    """Exception for unauthorized errors (401)."""
    
    def __init__(self, message: str = "Unauthorized", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=401, payload=payload)


class ForbiddenError(APIError):
    """Exception for forbidden errors (403)."""
    
    def __init__(self, message: str = "Forbidden", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=403, payload=payload)


class InternalServerError(APIError):
    """Exception for internal server errors (500)."""
    
    def __init__(self, message: str = "Internal server error", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=500, payload=payload)


def handle_api_error(error: APIError) -> Tuple[Dict[str, Any], int]:
    """
    Handle custom API errors.
    
    Args:
        error: The API error instance
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    logger.error(f"API Error: {error.message} (Status: {error.status_code})")
    response = jsonify(error.to_dict())
    return response, error.status_code


def handle_http_exception(error: HTTPException) -> Tuple[Dict[str, Any], int]:
    """
    Handle HTTP exceptions from Werkzeug.
    
    Args:
        error: The HTTP exception instance
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    logger.warning(f"HTTP Exception: {error.description} (Status: {error.code})")
    response = jsonify({
        'error': error.description,
        'status_code': error.code,
        'suggestion': _get_http_suggestion(error.code)
    })
    return response, error.code


def _get_http_suggestion(status_code: int) -> str:
    """Get suggestion based on HTTP status code."""
    suggestions = {
        400: "Please check your request and try again.",
        401: "Please provide valid authentication credentials.",
        403: "You don't have permission to access this resource.",
        404: "The requested resource was not found. Please check the URL.",
        405: "The request method is not allowed for this endpoint.",
        413: "The file is too large. Maximum size is 10MB.",
        500: "Server error. Please try again later or contact support.",
        502: "Server is temporarily unavailable. Please try again later.",
        503: "Server is under maintenance. Please try again later.",
        504: "Server took too long to respond. Please try again."
    }
    return suggestions.get(status_code, "An error occurred. Please try again.")


def handle_generic_exception(error: Exception) -> Tuple[Dict[str, Any], int]:
    """
    Handle generic unhandled exceptions.
    
    Args:
        error: The exception instance
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    logger.exception(f"Unhandled exception: {str(error)}")
    
    # Check for specific common errors
    error_msg = str(error).lower()
    suggestion = "Please try again or contact support if the problem persists."
    
    if 'pdf' in error_msg:
        suggestion = "The PDF file may be corrupted or in an unsupported format."
    elif 'ocr' in error_msg or 'tesseract' in error_msg:
        suggestion = "OCR is not available. Install dependencies: pip install pytesseract pdf2image"
    elif 'api' in error_msg and ('key' in error_msg or 'quota' in error_msg):
        suggestion = "Check your API key in .env file or try again later."
    elif 'database' in error_msg or 'sqlite' in error_msg:
        suggestion = "Database error. Please restart the server."
    elif 'memory' in error_msg or 'memoryerror' in error_msg:
        suggestion = "File is too large or system memory is low. Try with a smaller PDF."
    
    response = jsonify({
        'error': 'An unexpected error occurred. Please try again.',
        'status_code': 500,
        'details': str(error),  # Include error details for debugging
        'suggestion': suggestion
    })
    return response, 500


def register_error_handlers(app):
    """
    Register all error handlers with the Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(APIError)
    def handle_custom_api_error(error):
        return handle_api_error(error)
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return handle_http_exception(error)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        return handle_generic_exception(error)
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 Not Found: {error}")
        return jsonify({
            'error': 'The requested resource was not found.',
            'status_code': 404,
            'suggestion': 'Please check the URL or go to the homepage.'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error: {error}")
        return jsonify({
            'error': 'Internal server error.',
            'status_code': 500,
            'suggestion': 'Please try again later or contact support.'
        }), 500

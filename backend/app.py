"""
Main Flask application factory.
Creates and configures the Flask app with all necessary extensions and blueprints.
""" 
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.config import get_config
from backend.utils.error_handler import register_error_handlers


def setup_logging(app):
    """
    Configure structured logging for the application.
    
    Args:
        app: Flask application instance
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    log_format = app.config['LOG_FORMAT']
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format
    )
    
    # Add file handler for persistent logs
    try:
        log_dir = Path(__file__).resolve().parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    except Exception as e:
        app.logger.warning(f"Could not create log file: {e}")
    
    app.logger.setLevel(log_level)
    app.logger.info(f"Logging configured. Level: {app.config['LOG_LEVEL']}")


def create_app(config_name: str = None):
    """
    Application factory function.
    Creates and configures the Flask application.
    
    Args:
        config_name: Name of configuration to use (defaults to environment variable)
    
    Returns:
        Flask application instance
    """
    # Get configuration
    if config_name:
        os.environ['FLASK_ENV'] = config_name
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    # Setup logging
    setup_logging(app)
    
    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register error handlers
    register_error_handlers(app)
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        app.logger.debug('Headers: %s', dict(request.headers))
        app.logger.debug('Body: %s', request.get_data())
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'MCQ Extractor AI',
            'version': '1.0.0'
        }), 200
    
    # Serve frontend - root route
    @app.route('/', methods=['GET'])
    def serve_index():
        """Serve the main index.html page."""
        from flask import send_from_directory
        frontend_path = Path(__file__).resolve().parent.parent / 'frontend'
        return send_from_directory(frontend_path, 'index.html')
    
    # Serve static files from frontend
    @app.route('/<path:filename>', methods=['GET'])
    def serve_static(filename):
        """Serve static files from frontend directory."""
        from flask import send_from_directory
        frontend_path = Path(__file__).resolve().parent.parent / 'frontend'
        # Check if it's a file in frontend directory
        file_path = frontend_path / filename
        if file_path.exists() and file_path.is_file():
            return send_from_directory(frontend_path, filename)
        # Otherwise serve index.html for SPA routing
        return send_from_directory(frontend_path, 'index.html')
    
    # Register blueprints
    register_blueprints(app)
    
    # Ensure upload directories exist
    ensure_directories(app)
    
    # Initialize database and create tables
    init_database(app)
    
    app.logger.info("Application started successfully")
    
    return app


def register_blueprints(app):
    """
    Register all blueprints with the application.
    
    Args:
        app: Flask application instance
    """
    from backend.routes import extract, upload, download, validate
    
    # Register blueprints with url_prefix
    app.register_blueprint(extract.bp, url_prefix='/api/extract')
    app.register_blueprint(upload.bp, url_prefix='/api/upload')
    app.register_blueprint(download.bp, url_prefix='/api/download')
    app.register_blueprint(validate.bp, url_prefix='/api/validate')
    
    app.logger.info("All blueprints registered successfully")


def ensure_directories(app):
    """
    Ensure required directories exist.
    
    Args:
        app: Flask application instance
    """
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['JSON_OUTPUT_FOLDER']
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    app.logger.debug("All required directories created")


def init_database(app):
    """
    Initialize database and create tables.
    
    Args:
        app: Flask application instance
    """
    try:
        from backend.models.database import init_db, create_tables
        init_db(app)
        create_tables()
        app.logger.info("Database initialized and tables created")
    except Exception as e:
        app.logger.warning(f"Could not initialize database: {e}")


# Export app for gunicorn
app = create_app()

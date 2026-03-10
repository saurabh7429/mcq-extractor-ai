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
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    log_format = app.config['LOG_FORMAT']
    
    logging.basicConfig(
        level=log_level,
        format=log_format
    )
    
    try:
        log_dir = Path(__file__).resolve().parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,
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
    if config_name:
        os.environ['FLASK_ENV'] = config_name
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    setup_logging(app)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    register_error_handlers(app)
    
    @app.before_request
    def log_request_info():
        app.logger.debug('Headers: %s', dict(request.headers))
        app.logger.debug('Body: %s', request.get_data())
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'MCQ Extractor AI',
            'version': '1.0.0'
        }), 200
    
    # Serve frontend - root route
    @app.route('/', methods=['GET'])
    def serve_index():
        from flask import send_from_directory
        root_path = Path(__file__).resolve().parent.parent
        return send_from_directory(root_path, 'index.html')
    
    # Serve preview page
    @app.route('/preview', methods=['GET'])
    @app.route('/preview.html', methods=['GET'])
    def serve_preview():
        from flask import send_from_directory
        root_path = Path(__file__).resolve().parent.parent
        return send_from_directory(root_path, 'preview.html')
    
    # Serve quiz page
    @app.route('/quiz', methods=['GET'])
    @app.route('/quiz.html', methods=['GET'])
    def serve_quiz():
        from flask import send_from_directory
        root_path = Path(__file__).resolve().parent.parent
        return send_from_directory(root_path, 'quiz.html')
    
    # Serve static files from root
    @app.route('/<path:filename>', methods=['GET'])
    def serve_static(filename):
        from flask import send_from_directory
        root_path = Path(__file__).resolve().parent.parent
        
        valid_dirs = ['js', 'css', 'images', 'assets', 'logo.png']
        
        for dir_name in valid_dirs:
            if filename.startswith(dir_name + '/') or filename == dir_name:
                file_path = root_path / filename
                if file_path.exists() and file_path.is_file():
                    return send_from_directory(root_path, filename)
        
        return send_from_directory(root_path, 'index.html')
    
    # Register blueprints
    register_blueprints(app)
    
    # Ensure upload directories exist
    ensure_directories(app)
    
    # Initialize database and create tables
    init_database(app)
    
    app.logger.info("Application started successfully")
    
    return app


def register_blueprints(app):
    from backend.routes import extract, upload, download, validate, stats, status
    
    app.register_blueprint(extract.bp, url_prefix='/api/extract')
    app.register_blueprint(upload.bp, url_prefix='/api/upload')
    app.register_blueprint(download.bp, url_prefix='/api/download')
    app.register_blueprint(validate.bp, url_prefix='/api/validate')
    app.register_blueprint(stats.bp, url_prefix='/api/stats')
    app.register_blueprint(status.bp, url_prefix='/api/status')
    
    app.logger.info("All blueprints registered successfully")


def ensure_directories(app):
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['JSON_OUTPUT_FOLDER']
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    app.logger.debug("All required directories created")


def init_database(app):
    try:
        from backend.models.database import init_db, create_tables
        init_db(app)
        create_tables()
        app.logger.info("Database initialized and tables created")
    except Exception as e:
        app.logger.warning(f"Could not initialize database: {e}")


# Export app for gunicorn
app = create_app()

"""
Centralized configuration for the Flask application.
Loads environment variables using python-dotenv.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def get_database_path():
    """
    Get the database path based on the environment.
    On Render.com, use /tmp for writable storage.
    """
    # Check if running on Render.com
    if os.getenv('RENDER') or os.path.exists('/opt/render'):
        # Use /tmp on Render.com for writable storage
        return Path('/tmp') / 'mcq.db'
    else:
        # Use local database path
        return BASE_DIR / 'database' / 'mcq.db'


class Config:
    """Base configuration class."""
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    # Base directory
    BASE_DIR = BASE_DIR
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_PDF_PAGES = 50  # Maximum allowed pages in PDF
    UPLOAD_FOLDER = BASE_DIR / 'storage' / 'uploaded_pdfs'
    JSON_OUTPUT_FOLDER = BASE_DIR / 'storage' / 'generated_json'
    
    # Database settings - Use environment-specific path
    DATABASE_PATH = get_database_path()
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development configuration."""
    FLASK_ENV = 'development'
    FLASK_DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    FLASK_ENV = 'production'
    FLASK_DEBUG = False
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """Testing configuration."""
    FLASK_ENV = 'testing'
    FLASK_DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}


def get_config():
    """
    Get the configuration object based on FLASK_ENV.
    
    Returns:
        Config: The configuration object
    """
    env = os.getenv('FLASK_ENV', 'production')
    return config_by_name.get(env, ProductionConfig)

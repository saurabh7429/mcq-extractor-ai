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


class Config:
    """Base configuration class."""
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File upload settings - use /tmp for production (Render's ephemeral filesystem)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    if os.getenv('RENDER'):
        UPLOAD_FOLDER = Path('/tmp/storage/uploaded_pdfs')
        JSON_OUTPUT_FOLDER = Path('/tmp/storage/generated_json')
    else:
        UPLOAD_FOLDER = BASE_DIR / 'storage' / 'uploaded_pdfs'
        JSON_OUTPUT_FOLDER = BASE_DIR / 'storage' / 'generated_json'
    
    # Database settings - use /tmp for production (Render's ephemeral filesystem)
    if os.getenv('RENDER'):
        DATABASE_PATH = '/tmp/mcq.db'
    else:
        DATABASE_PATH = BASE_DIR / 'database' / 'mcq.db'
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

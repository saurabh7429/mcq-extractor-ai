"""
Application entry point.
Run this file to start the Flask development server.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app

# Get environment from FLASK_ENV or use production as default
env = os.getenv('FLASK_ENV', 'production')

# Create the application
app = create_app(env)

if __name__ == '__main__':
    # Get host and port from environment or use defaults
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = app.config.get('FLASK_DEBUG', False)
    
    print(f"Starting MCQ Extractor AI on {host}:{port}")
    print(f"Environment: {env}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)

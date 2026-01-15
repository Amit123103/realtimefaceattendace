"""
Production WSGI configuration for deployment
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
path = Path(__file__).parent
sys.path.insert(0, str(path))

# Import Flask app
from app import app as application

# For PythonAnywhere, Heroku, Render, etc.
if __name__ == "__main__":
    application.run()

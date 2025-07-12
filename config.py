import os
from dotenv import load_dotenv

# Load environment variables from .env file (only in development)
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///blog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'change-this-password'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # In production, these MUST be set as environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Will fail if not set
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')  # Will fail if not set

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

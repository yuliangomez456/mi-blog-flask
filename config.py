import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Configuración para Railway - usa DATABASE_URL si existe
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Railway usa postgres:// pero SQLAlchemy necesita postgresql://
        SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://')
    else:
        # Fallback para desarrollo
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

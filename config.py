import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto-para-desarrollo'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CONFIGURACIÓN CRÍTICA PARA SQLALCHEMY
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
    }
    
    # Configuración de carga de archivos
    if os.environ.get('RENDER'):
        # En Render, avisar que no se soportan uploads
        UPLOAD_FOLDER = None
        UPLOADS_ENABLED = False
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
        UPLOADS_ENABLED = True
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    
    # Configuración de correo (para producción)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['admin@comisionesmarinas.es']
    
    # Configuraciones específicas para Render
    if 'RENDER' in os.environ:
        # Arreglar URL de PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
        PREFERRED_URL_SCHEME = 'https'
        
        # Configuración adicional para producción
        PROPAGATE_EXCEPTIONS = True
        
        # Para Render, usar una configuración más robusta de SQLAlchemy
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'max_overflow': 10,
            'pool_timeout': 30,
        }

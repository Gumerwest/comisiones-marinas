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
    
    # CLOUDINARY - Para almacenar archivos e imágenes
    CLOUDINARY_ENABLED = bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # Configuración de carga de archivos
    if os.environ.get('RENDER'):
        # En Render, usar Cloudinary
        UPLOAD_FOLDER = None
        UPLOADS_ENABLED = bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
        USE_CLOUDINARY = True
    else:
        # En desarrollo local, usar filesystem local
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
        UPLOADS_ENABLED = True
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
        USE_CLOUDINARY = bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))
    
    # RESEND - Para envío de emails
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'Comisiones Marinas <noreply@tudominio.com>')
    
    # Configuración de correo (fallback)
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

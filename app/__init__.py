from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_socketio import SocketIO
from config import Config
import os

db = SQLAlchemy()
login = LoginManager()
csrf = CSRFProtect()
mail = Mail()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Crear directorio de uploads si no existe
    upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
    
    # Configuración especial para SQLAlchemy en producción
    if os.environ.get('RENDER'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'max_overflow': 20,
        }
    
    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    
    # Inicializar SocketIO con configuración mejorada
    if os.environ.get('RENDER'):
        # Configuración para producción
        socketio.init_app(app, 
                         cors_allowed_origins="*",
                         async_mode='threading',
                         logger=True,
                         engineio_logger=True)
    else:
        # Configuración para desarrollo
        socketio.init_app(app, cors_allowed_origins="*")
    
    login.login_view = 'auth.login'
    login.login_message = 'Por favor, inicie sesión para acceder a esta página.'
    
    # Registrar blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.routes.comisiones import bp as comisiones_bp
    app.register_blueprint(comisiones_bp, url_prefix='/comisiones')
    
    from app.routes.temas import bp as temas_bp
    app.register_blueprint(temas_bp, url_prefix='/temas')
    
    # Registrar página de inicio
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Gestor de errores
    from app.routes.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    # Registrar eventos de Socket.IO
    from app.routes import socketio_handlers
    
    # Configurar comandos CLI
    from app.utils.cli import init_cli_commands
    init_cli_commands(app)
    
    # Configuración adicional para evitar problemas de threading
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    
    return app

from app import models

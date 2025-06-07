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

    # Crear directorio de uploads si no existe y no estamos en Render
    if not os.environ.get('RENDER'):
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)
            print(f"📁 Upload folder asegurado: {upload_folder}")

    # Configuración especial para SQLAlchemy en producción
    if os.environ.get('RENDER'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'max_overflow': 10,
        }

    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Configuración de SocketIO usando valores de config.py
    if os.environ.get('RENDER'):
        socketio.init_app(
            app,
            cors_allowed_origins="*",
            async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading'),
            logger=False,
            engineio_logger=False,
            transports=app.config.get('SOCKETIO_TRANSPORTS', ['polling'])
        )
        print("🔌 SocketIO configurado para Render")
    else:
        socketio.init_app(
            app,
            cors_allowed_origins="*",
            async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading'),
            logger=True,
            engineio_logger=True,
            transports=app.config.get('SOCKETIO_TRANSPORTS', ['polling', 'websocket'])
        )
        print("🔌 SocketIO configurado para desarrollo")

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

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Registrar eventos de Socket.IO
    from app.routes import socketio_handlers

    # Configurar comandos CLI
    from app.utils.cli import init_cli_commands
    init_cli_commands(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Mostrar estado de configuración
    print(f"🌐 Aplicación inicializada")
    print(f"📊 Base de datos: {'PostgreSQL' if 'postgresql' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'SQLite'}")
    print(f"📁 Uploads habilitados: {app.config.get('UPLOADS_ENABLED', False)}")

    return app

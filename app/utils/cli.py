import click
from app import db
from app.models import Usuario
import os

def init_cli_commands(app):
    @app.cli.command()
    @click.argument('email')
    @click.argument('password')
    def create_admin(email, password):
        """Crear un usuario administrador"""
        # Verificar si ya existe
        if Usuario.query.filter_by(email=email).first():
            click.echo('Error: Ya existe un usuario con ese email')
            return
        
        # Crear el administrador
        admin = Usuario(
            email=email,
            nombre='Admin',
            apellidos='Sistema',
            telefono='000000000',
            razon_social='Administración',
            nombre_comercial='Admin',
            cargo='Administrador',
            rol='admin',
            activo=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f'Administrador creado exitosamente: {email}')
    
    @app.cli.command()
    def init_db():
        """Inicializar la base de datos"""
        db.create_all()
        click.echo('Base de datos inicializada')
    
    @app.cli.command()
    def create_default_admin():
        """Crear administrador por defecto desde variables de entorno"""
        email = os.environ.get('ADMIN_EMAIL', 'admin@comisionesmarinas.es')
        password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        # Verificar si ya existe
        if Usuario.query.filter_by(email=email).first():
            click.echo('El administrador por defecto ya existe')
            return
        
        # Crear el administrador
        admin = Usuario(
            email=email,
            nombre='Administrador',
            apellidos='Principal',
            telefono='900000000',
            razon_social='Administración del Sistema',
            nombre_comercial='Admin',
            cargo='Administrador Principal',
            rol='admin',
            activo=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f'Administrador por defecto creado: {email}')

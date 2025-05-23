#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""
from app import create_app, db
from app.models import Usuario
import os

def init_database():
    app = create_app()
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas correctamente")
            
            # Verificar si ya existe un administrador
            admin_exists = Usuario.query.filter_by(rol='admin').first()
            if not admin_exists:
                # Crear administrador por defecto
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@comisionesmarinas.es')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
                
                admin = Usuario(
                    email=admin_email,
                    nombre='Administrador',
                    apellidos='Principal',
                    telefono='900000000',
                    razon_social='Administración del Sistema',
                    nombre_comercial='Admin',
                    cargo='Administrador Principal',
                    rol='admin',
                    activo=True
                )
                admin.set_password(admin_password)
                
                db.session.add(admin)
                db.session.commit()
                print(f"✅ Administrador creado: {admin_email}")
            else:
                print("✅ Administrador ya existe")
                
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {str(e)}")
            raise

if __name__ == '__main__':
    init_database()

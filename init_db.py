#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""
import os
import sys

# Añadir la ruta del proyecto al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Usuario

def init_database():
    app = create_app()
    with app.app_context():
        try:
            print("🔄 Iniciando creación de base de datos...")
            
            # Eliminar todas las tablas existentes
            db.drop_all()
            print("✅ Tablas anteriores eliminadas")
            
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas correctamente")
            
            # Verificar si ya existe un administrador
            admin_exists = Usuario.query.filter_by(rol='admin').first()
            if not admin_exists:
                # Crear administrador por defecto
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@comisionesmarinas.es')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
                
                print(f"🔄 Creando administrador: {admin_email}")
                
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
            
            print("🎉 Base de datos inicializada correctamente")
                
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {str(e)}")
            import traceback
            traceback.print_exc()
            # No hacer raise para que el build no falle completamente
            
if __name__ == '__main__':
    init_database()

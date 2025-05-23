#!/usr/bin/env python3
"""
Script para inicializar la base de datos
"""
import os
import sys
import time

# Añadir la ruta del proyecto al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    from app import create_app, db
    from app.models import Usuario
    
    print("🔄 Iniciando configuración de base de datos...")
    
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        print("📊 Creando tablas...")
        db.create_all()
        print("✅ Tablas creadas")
        
        # Verificar si existe un administrador
        admin = Usuario.query.filter_by(rol='admin').first()
        if not admin:
            # Crear administrador por defecto
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@comisionesmarinas.es')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            print(f"👤 Creando administrador: {admin_email}")
            
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
            print(f"✅ Administrador creado exitosamente")
        else:
            print("✅ Administrador ya existe")
        
        print("🎉 Base de datos configurada correctamente")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        # Continuar de todos modos para no bloquear el deploy
        pass

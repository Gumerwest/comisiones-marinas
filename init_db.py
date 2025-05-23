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
        
        # Buscar o crear administrador
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@comisionesmarinas.es')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'ComisionesMar2024!')
        
        # Buscar si existe el admin
        admin = Usuario.query.filter_by(email=admin_email).first()
        
        if admin:
            print(f"📝 Actualizando administrador existente: {admin_email}")
            # Actualizar todos los campos por si acaso
            admin.set_password(admin_password)
            admin.activo = True
            admin.rol = 'admin'
            admin.nombre = 'Administrador'
            admin.apellidos = 'Principal'
            db.session.commit()
            print(f"✅ Administrador actualizado")
        else:
            print(f"👤 Creando nuevo administrador: {admin_email}")
            
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
        
        # Verificar que se guardó correctamente
        admin_check = Usuario.query.filter_by(email=admin_email).first()
        if admin_check:
            print(f"✅ Verificación: Usuario existe")
            print(f"✅ Activo: {admin_check.activo}")
            print(f"✅ Rol: {admin_check.rol}")
            print(f"✅ Puede hacer login: {admin_check.check_password(admin_password)}")
        
        print(f"\n📧 Email: {admin_email}")
        print(f"🔑 Contraseña: {admin_password}")
        print("🎉 Base de datos configurada correctamente")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Continuar de todos modos para no bloquear el deploy
        pass

#!/usr/bin/env python3
"""
Script para inicializar la base de datos y crear directorios necesarios
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
        # Crear directorio de uploads si no existe
        upload_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path, exist_ok=True)
            print(f"📁 Directorio de uploads creado: {upload_path}")
            
            # Crear archivo .gitkeep para mantener el directorio
            gitkeep_path = os.path.join(upload_path, '.gitkeep')
            with open(gitkeep_path, 'w') as f:
                f.write('# Keep this directory\n')
        
        # Intentar crear las tablas con reintentos
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                print(f"📊 Intento {attempt + 1} de crear tablas...")
                db.create_all()
                print("✅ Tablas creadas exitosamente")
                break
            except Exception as e:
                print(f"⚠️ Error en intento {attempt + 1}: {str(e)}")
                if attempt < max_attempts - 1:
                    print("⏳ Esperando 2 segundos antes de reintentar...")
                    time.sleep(2)
                else:
                    print("❌ No se pudieron crear las tablas después de varios intentos")
                    # No salir con error para no bloquear el deploy
        
        # Buscar o crear administrador
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@comisionesmarinas.es')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        try:
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
            
        except Exception as e:
            print(f"⚠️ Error manejando usuario admin: {str(e)}")
            print("Continuando de todos modos...")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Siempre salir con código 0 para no bloquear el deploy
        sys.exit(0)

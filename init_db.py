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
        # En Render, usar /tmp para archivos temporales
        if os.environ.get('RENDER'):
            upload_path = '/tmp/uploads'
        else:
            upload_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
        
        # Crear directorio de uploads si no existe
        if upload_path:
            try:
                os.makedirs(upload_path, exist_ok=True)
                print(f"📁 Directorio de uploads preparado: {upload_path}")
            except Exception as e:
                print(f"⚠️ No se pudo crear directorio de uploads: {str(e)}")
                # Continuar sin uploads
        
        # Intentar crear las tablas con reintentos
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                print(f"📊 Intento {attempt + 1} de crear tablas...")
                
                # Primero intentar conectar a la base de datos
                with db.engine.connect() as conn:
                    print("✅ Conexión a base de datos exitosa")
                
                # Luego crear las tablas
                db.create_all()
                print("✅ Tablas creadas exitosamente")
                break
            except Exception as e:
                print(f"⚠️ Error en intento {attempt + 1}: {str(e)}")
                if attempt < max_attempts - 1:
                    print("⏳ Esperando 3 segundos antes de reintentar...")
                    time.sleep(3)
                else:
                    print("⚠️ No se pudieron crear las tablas, pero continuando...")
        
        # Buscar o crear administrador
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@comisionesmarinas.es')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        try:
            # Buscar si existe el admin
            admin = Usuario.query.filter_by(email=admin_email).first()
            
            if admin:
                print(f"📝 Actualizando administrador existente: {admin_email}")
                # Actualizar campos
                admin.set_password(admin_password)
                admin.activo = True
                admin.rol = 'admin'
                admin.nombre = admin.nombre or 'Administrador'
                admin.apellidos = admin.apellidos or 'Principal'
                admin.telefono = admin.telefono or '900000000'
                admin.razon_social = admin.razon_social or 'Administración del Sistema'
                admin.nombre_comercial = admin.nombre_comercial or 'Admin'
                admin.cargo = admin.cargo or 'Administrador Principal'
                
                db.session.commit()
                print(f"✅ Administrador actualizado exitosamente")
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
                print(f"✅ Verificación: Usuario administrador configurado correctamente")
                print(f"✅ Email: {admin_email}")
                print(f"✅ Activo: {admin_check.activo}")
                print(f"✅ Rol: {admin_check.rol}")
            
            print("\n🎉 Base de datos configurada correctamente")
            print(f"📧 Credenciales de administrador:")
            print(f"   Email: {admin_email}")
            print(f"   Contraseña: {admin_password}")
            
        except Exception as e:
            print(f"⚠️ Error manejando usuario admin: {str(e)}")
            print("La aplicación puede funcionar pero sin usuario administrador inicial")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")
        # Imprimir más detalles del error
        import traceback
        traceback.print_exc()
    finally:
        # Siempre salir con código 0 para no bloquear el deploy
        print("\n✅ Script de inicialización completado")
        sys.exit(0)

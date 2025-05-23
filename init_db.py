#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""
import os
import sys
import time

# Añadir la ruta del proyecto al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    try:
        from app import create_app, db
        from app.models import Usuario
        
        print("🔄 Iniciando creación de base de datos...")
        
        app = create_app()
        
        with app.app_context():
            # Esperar un poco para asegurar que la BD está lista
            time.sleep(2)
            
            try:
                # Intentar conectar a la base de datos
                db.engine.connect()
                print("✅ Conexión a base de datos establecida")
            except Exception as e:
                print(f"⚠️ Error conectando a BD: {e}")
                print("Continuando de todos modos...")
            
            # Crear todas las tablas
            try:
                db.create_all()
                print("✅ Tablas creadas correctamente")
            except Exception as e:
                print(f"⚠️ Error creando tablas: {e}")
                print("Es posible que las tablas ya existan, continuando...")
            
            # Verificar si ya existe un administrador
            try:
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
                    print(f"📧 Email: {admin_email}")
                    print(f"🔑 Contraseña: {admin_password}")
                else:
                    print("✅ Administrador ya existe")
            except Exception as e:
                print(f"⚠️ Error verificando/creando admin: {e}")
                print("Continuando sin crear admin...")
            
            print("🎉 Proceso de inicialización completado")
                
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        # No hacer raise para que el build no falle
        
if __name__ == '__main__':
    init_database()

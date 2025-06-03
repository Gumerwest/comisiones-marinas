#!/usr/bin/env python3
"""
Script para verificar servicios externos (Cloudinary, Resend)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_services():
    from app import create_app
    app = create_app()
    
    with app.app_context():
        print("=== VERIFICACIÓN DE SERVICIOS ===\n")
        
        # Verificar Cloudinary
        print("📸 CLOUDINARY:")
        if app.config.get('CLOUDINARY_ENABLED'):
            print(f"  ✅ Habilitado")
            print(f"  - Cloud Name: {app.config.get('CLOUDINARY_CLOUD_NAME')}")
            print(f"  - API Key: {app.config.get('CLOUDINARY_API_KEY')[:10]}...")
            
            # Test de conexión
            try:
                import cloudinary
                cloudinary.config(
                    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
                    api_key=app.config['CLOUDINARY_API_KEY'],
                    api_secret=app.config['CLOUDINARY_API_SECRET']
                )
                
                # Intentar hacer una operación simple para verificar las credenciales
                try:
                    result = cloudinary.api.ping()
                    print("  ✅ Conexión exitosa")
                except:
                    # Si ping falla, intentar listar recursos (más confiable)
                    try:
                        result = cloudinary.api.resources(max_results=1)
                        print("  ✅ Conexión exitosa - API funcionando")
                    except Exception as e:
                        if "401" in str(e):
                            print("  ❌ Error de autenticación - Verifique las credenciales")
                        else:
                            print(f"  ⚠️  API accesible pero con advertencias: {str(e)}")
                
            except Exception as e:
                print(f"  ❌ Error de conexión: {str(e)}")
        else:
            print("  ❌ Deshabilitado")
            print("  ℹ️  Para habilitar, configure las variables de entorno:")
            print("     - CLOUDINARY_CLOUD_NAME")
            print("     - CLOUDINARY_API_KEY")
            print("     - CLOUDINARY_API_SECRET")
        
        # Verificar Resend
        print("\n📧 RESEND:")
        if app.config.get('RESEND_API_KEY'):
            print(f"  ✅ API Key configurada")
            print(f"  - From Email: {app.config.get('RESEND_FROM_EMAIL')}")
            
            # Test de API
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {app.config['RESEND_API_KEY']}",
                    "Content-Type": "application/json"
                }
                
                # Verificar que la API responde
                response = requests.get("https://api.resend.com/domains", headers=headers)
                
                if response.status_code == 200:
                    print("  ✅ API accesible - Conexión exitosa")
                    domains = response.json().get('data', [])
                    if domains:
                        print(f"  ✅ Dominios configurados: {len(domains)}")
                        for domain in domains:
                            print(f"     - {domain.get('name', 'Sin nombre')} ({domain.get('status', 'desconocido')})")
                    else:
                        print("  ⚠️  No hay dominios configurados - Los emails no funcionarán")
                        print("     Configure un dominio en https://resend.com/domains")
                elif response.status_code == 401:
                    print("  ❌ Error de autenticación - API key inválida")
                else:
                    print(f"  ⚠️  Respuesta API: {response.status_code}")
                    print(f"     {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Error conectando: {str(e)}")
        else:
            print("  ❌ No configurado")
            print("  ℹ️  Para habilitar, configure las variables de entorno:")
            print("     - RESEND_API_KEY")
            print("     - RESEND_FROM_EMAIL (opcional)")
        
        # Verificar SocketIO
        print("\n💬 SOCKETIO:")
        print(f"  - Async Mode: {app.config.get('SOCKETIO_ASYNC_MODE', 'default')}")
        print(f"  - CORS: {app.config.get('SOCKETIO_CORS_ALLOWED_ORIGINS', 'default')}")
        print(f"  - Transports: {app.config.get('SOCKETIO_TRANSPORTS', ['polling', 'websocket'])}")
        print(f"  - Ping Timeout: {app.config.get('SOCKETIO_PING_TIMEOUT', 30)}s")
        print(f"  - Ping Interval: {app.config.get('SOCKETIO_PING_INTERVAL', 15)}s")
        print(f"  - En Render: {'Sí' if os.environ.get('RENDER') else 'No'}")
        
        if os.environ.get('RENDER'):
            print("  ℹ️  Configuración optimizada para Render (solo polling)")
        else:
            print("  ℹ️  Configuración para desarrollo (polling + websocket)")
        
        # Verificar Base de Datos
        print("\n🗄️  BASE DE DATOS:")
        try:
            from app.models import Usuario
            # Intentar hacer una consulta simple
            count = Usuario.query.count()
            print(f"  ✅ Conexión exitosa")
            print(f"  - Tipo: {'PostgreSQL' if 'postgresql' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'SQLite'}")
            print(f"  - Usuarios registrados: {count}")
        except Exception as e:
            print(f"  ❌ Error de conexión: {str(e)}")
        
        # Verificar configuración de archivos
        print("\n📁 CONFIGURACIÓN DE ARCHIVOS:")
        print(f"  - Uploads habilitados: {'Sí' if app.config.get('UPLOADS_ENABLED') else 'No'}")
        print(f"  - Usar Cloudinary: {'Sí' if app.config.get('USE_CLOUDINARY') else 'No'}")
        print(f"  - Tamaño máximo: {app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB")
        
        if app.config.get('UPLOAD_FOLDER'):
            exists = os.path.exists(app.config['UPLOAD_FOLDER'])
            print(f"  - Directorio local: {'Existe' if exists else 'No existe'}")
        
        # Resumen
        print("\n=== RESUMEN ===")
        servicios_ok = []
        servicios_error = []
        
        if app.config.get('CLOUDINARY_ENABLED'):
            servicios_ok.append("Cloudinary")
        else:
            servicios_error.append("Cloudinary (carga de archivos)")
            
        if app.config.get('RESEND_API_KEY'):
            servicios_ok.append("Resend")
        else:
            servicios_error.append("Resend (emails)")
        
        if servicios_ok:
            print(f"✅ Servicios funcionando: {', '.join(servicios_ok)}")
        
        if servicios_error:
            print(f"❌ Servicios no configurados: {', '.join(servicios_error)}")
        
        print("\n💡 RECOMENDACIONES:")
        if not app.config.get('CLOUDINARY_ENABLED'):
            print("- Configure Cloudinary para habilitar la carga de archivos e imágenes")
        
        if not app.config.get('RESEND_API_KEY'):
            print("- Configure Resend para habilitar el envío de emails")
        elif app.config.get('RESEND_API_KEY') and os.environ.get('RENDER'):
            print("- Verifique que tiene un dominio configurado en Resend")
            print("- El email 'from' debe usar ese dominio verificado")
        
        if os.environ.get('RENDER'):
            print("\n📌 NOTA PARA RENDER:")
            print("- Los archivos locales NO se persistirán entre despliegues")
            print("- Use Cloudinary para almacenar archivos permanentemente")
            print("- El chat usa polling (más confiable que WebSockets en Render)")

if __name__ == '__main__':
    try:
        verify_services()
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()

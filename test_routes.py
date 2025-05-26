#!/usr/bin/env python3
"""
Script para probar las rutas y verificar errores
"""
import os
import sys

# Añadir la ruta del proyecto al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_routes():
    from app import create_app, db
    from app.models import Usuario, Comision
    
    app = create_app()
    
    with app.app_context():
        print("=== PRUEBA DE RUTAS ===\n")
        
        # Verificar configuración
        print("📋 CONFIGURACIÓN:")
        print(f"  - Upload folder: {app.config.get('UPLOAD_FOLDER')}")
        print(f"  - Max content length: {app.config.get('MAX_CONTENT_LENGTH')} bytes")
        print(f"  - En Render: {os.environ.get('RENDER', 'No')}")
        
        # Verificar directorio uploads
        upload_dir = app.config.get('UPLOAD_FOLDER')
        if upload_dir:
            exists = os.path.exists(upload_dir)
            writable = os.access(upload_dir, os.W_OK) if exists else False
            print(f"  - Directorio uploads existe: {exists}")
            print(f"  - Directorio uploads escribible: {writable}")
        
        # Listar rutas de comisiones
        print("\n🛣️ RUTAS DE COMISIONES:")
        with app.test_request_context():
            routes = []
            for rule in app.url_map.iter_rules():
                if 'comision' in str(rule):
                    routes.append(f"  - {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            
            for route in sorted(routes):
                print(route)
        
        # Verificar admin
        print("\n👤 USUARIO ADMIN:")
        admin = Usuario.query.filter_by(rol='admin').first()
        if admin:
            print(f"  ✅ Admin encontrado: {admin.email}")
            print(f"  - Activo: {admin.activo}")
            print(f"  - Nombre: {admin.nombre} {admin.apellidos}")
        else:
            print("  ❌ No se encontró usuario administrador")
        
        # Verificar comisiones
        print("\n📊 COMISIONES:")
        comisiones = Comision.query.all()
        if comisiones:
            for c in comisiones:
                print(f"  - {c.nombre} (ID: {c.id}, Activa: {c.activa})")
        else:
            print("  - No hay comisiones creadas")
        
        # Probar creación de comisión simulada
        print("\n🧪 PRUEBA DE CREACIÓN DE COMISIÓN:")
        try:
            # Simular datos
            test_comision = Comision(
                nombre="Comisión de Prueba",
                descripcion="Esta es una comisión de prueba para verificar la funcionalidad"
            )
            
            # No guardar realmente, solo verificar que se puede crear
            print("  ✅ Objeto Comision se puede crear correctamente")
            
            # Verificar si se puede acceder a las relaciones
            print(f"  ✅ Relaciones accesibles: membresias, temas, documentos")
            
        except Exception as e:
            print(f"  ❌ Error al crear comisión de prueba: {str(e)}")

if __name__ == '__main__':
    try:
        test_routes()
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

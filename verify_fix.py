#!/usr/bin/env python3
"""
Script para verificar que la corrección del error de Jinja2 está aplicada
"""
import os
import sys

# Añadir la ruta del proyecto al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_correccion():
    print("🔍 VERIFICACIÓN DE CORRECCIÓN DE ERROR JINJA2\n")
    
    # Verificar que el archivo del template existe
    template_path = os.path.join('app', 'templates', 'comisiones', 'ver.html')
    
    if not os.path.exists(template_path):
        print(f"❌ ERROR: No se encuentra el archivo {template_path}")
        return False
    
    print(f"✅ Archivo de template encontrado: {template_path}")
    
    # Leer el contenido del template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que NO contiene el código problemático
    problematic_code = "reuniones_proximas|sort(attribute='fecha')[:6]"
    
    if problematic_code in content:
        print(f"❌ ERROR: El template todavía contiene el código problemático:")
        print(f"   '{problematic_code}'")
        print("\n⚠️  Necesitas actualizar el archivo app/templates/comisiones/ver.html")
        print("   con el contenido corregido que te proporcioné.")
        return False
    else:
        print("✅ El código problemático ha sido eliminado")
    
    # Verificar que contiene la solución correcta
    if "{% if loop.index <= 6 %}" in content:
        print("✅ La solución correcta (loop.index) está implementada")
    else:
        print("⚠️  ADVERTENCIA: No se encontró la implementación con loop.index")
        print("   Asegúrate de que el template tenga la lógica correcta para limitar reuniones")
    
    # Verificar la aplicación Flask
    try:
        from app import create_app, db
        from app.models import Comision
        
        app = create_app()
        with app.app_context():
            print("\n✅ La aplicación Flask se puede crear correctamente")
            
            # Verificar que las rutas están registradas
            comision_routes = [rule for rule in app.url_map.iter_rules() if 'comision' in str(rule)]
            print(f"✅ Se encontraron {len(comision_routes)} rutas de comisiones")
            
            # Verificar la base de datos
            try:
                comisiones_count = Comision.query.count()
                print(f"✅ Base de datos accesible - {comisiones_count} comisiones encontradas")
            except Exception as e:
                print(f"⚠️  Error al acceder a la base de datos: {str(e)}")
                print("   Esto es normal si no has inicializado la BD aún")
            
    except Exception as e:
        print(f"\n❌ Error al verificar la aplicación: {str(e)}")
        return False
    
    # Verificar configuración para Render
    print("\n📋 CONFIGURACIÓN PARA RENDER:")
    if os.environ.get('RENDER'):
        print("✅ Ejecutándose en Render")
        print("   - Los archivos NO se guardarán localmente")
        print("   - Las imágenes NO se persistirán")
    else:
        print("ℹ️  Ejecutándose en modo desarrollo local")
        print("   - Los archivos se guardarán normalmente")
    
    print("\n✨ RESUMEN:")
    print("=" * 50)
    print("La corrección del error de Jinja2 está aplicada.")
    print("La aplicación debería funcionar correctamente ahora.")
    print("\nSi aún tienes problemas:")
    print("1. Asegúrate de haber guardado todos los archivos")
    print("2. Reinicia el servidor de Render")
    print("3. Limpia la caché del navegador")
    
    return True

if __name__ == '__main__':
    try:
        success = verificar_correccion()
        if success:
            print("\n✅ ¡TODO CORRECTO! La aplicación debería funcionar ahora.")
        else:
            print("\n❌ Hay problemas que necesitan ser corregidos.")
            print("\n📝 INSTRUCCIONES:")
            print("1. Copia el contenido del template corregido que te proporcioné")
            print("2. Pégalo en app/templates/comisiones/ver.html")
            print("3. Guarda el archivo")
            print("4. Haz commit y push a tu repositorio")
            print("5. Render debería redesplegar automáticamente")
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Script para verificar el estado de la aplicación
"""
import os
import sys

# Añadir la ruta del proyecto al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_app():
    from app import create_app, db
    from app.models import Usuario, Comision, Tema, MembresiaComision
    
    app = create_app()
    
    with app.app_context():
        print("=== VERIFICACIÓN DE LA APLICACIÓN ===\n")
        
        # Verificar usuarios
        print("📊 USUARIOS:")
        usuarios = Usuario.query.all()
        print(f"Total de usuarios: {len(usuarios)}")
        for u in usuarios:
            print(f"  - {u.email} | Rol: {u.rol} | Activo: {u.activo}")
        
        # Verificar comisiones
        print("\n🚢 COMISIONES:")
        comisiones = Comision.query.all()
        print(f"Total de comisiones: {len(comisiones)}")
        for c in comisiones:
            miembros_count = MembresiaComision.query.filter_by(
                comision_id=c.id, 
                estado='aprobado'
            ).count()
            print(f"  - {c.nombre} | Activa: {c.activa} | Miembros aprobados: {miembros_count}")
        
        # Verificar temas
        print("\n💡 TEMAS:")
        temas = Tema.query.all()
        print(f"Total de temas: {len(temas)}")
        for t in temas:
            print(f"  - {t.titulo} | Estado: {t.estado} | Comisión: {t.comision.nombre if t.comision else 'N/A'}")
        
        # Verificar membresías
        print("\n👥 MEMBRESÍAS:")
        membresias = MembresiaComision.query.all()
        print(f"Total de membresías: {len(membresias)}")
        aprobadas = MembresiaComision.query.filter_by(estado='aprobado').count()
        pendientes = MembresiaComision.query.filter_by(estado='pendiente_aprobacion').count()
        print(f"  - Aprobadas: {aprobadas}")
        print(f"  - Pendientes: {pendientes}")
        
        # Verificar rutas
        print("\n🛣️ RUTAS DE COMISIONES REGISTRADAS:")
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
            if 'comision' in str(rule) or str(rule).startswith('/comisiones'):
                print(f"  - {rule}")
        
        # Verificar configuración
        print("\n⚙️ CONFIGURACIÓN:")
        print(f"  - Base de datos: {'PostgreSQL' if 'postgresql' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'SQLite'}")
        print(f"  - Upload folder existe: {os.path.exists(app.config.get('UPLOAD_FOLDER', ''))}")
        
        print("\n✅ Verificación completada")

if __name__ == '__main__':
    try:
        verificar_app()
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Script para crear datos de ejemplo
"""
import os
import sys

# Añadir la ruta del proyecto al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def crear_datos_ejemplo():
    from app import create_app, db
    from app.models import Usuario, Comision, MembresiaComision, Tema
    
    app = create_app()
    
    with app.app_context():
        print("🔄 Creando datos de ejemplo...")
        
        # Buscar el admin
        admin = Usuario.query.filter_by(rol='admin').first()
        if not admin:
            print("❌ No se encontró un usuario administrador")
            return
        
        # Crear comisión de ejemplo si no existe
        comision = Comision.query.filter_by(nombre='Sostenibilidad y Medio Ambiente').first()
        if not comision:
            comision = Comision(
                nombre='Sostenibilidad y Medio Ambiente',
                descripcion='Comisión dedicada a abordar los desafíos ambientales en el sector marítimo, incluyendo la reducción de emisiones, gestión de residuos y protección de ecosistemas marinos.',
                activa=True
            )
            db.session.add(comision)
            db.session.commit()
            print("✅ Comisión 'Sostenibilidad y Medio Ambiente' creada")
            
            # Hacer al admin coordinador de la comisión
            membresia = MembresiaComision(
                usuario_id=admin.id,
                comision_id=comision.id,
                estado='aprobado',
                rol='coordinador'
            )
            db.session.add(membresia)
            db.session.commit()
            print("✅ Admin asignado como coordinador")
            
            # Crear un tema de ejemplo
            tema = Tema(
                titulo='Reducción de Emisiones en Puertos',
                resumen='Estrategias para reducir las emisiones de CO2 y otros contaminantes en las operaciones portuarias.',
                situacion_actual='Los puertos españoles están implementando diversas medidas para cumplir con las normativas europeas de reducción de emisiones.',
                estado='aprobado',
                comision_id=comision.id,
                creador_id=admin.id
            )
            db.session.add(tema)
            db.session.commit()
            print("✅ Tema de ejemplo creado")
        else:
            print("ℹ️ La comisión 'Sostenibilidad y Medio Ambiente' ya existe")
        
        # Crear segunda comisión si no existe
        comision2 = Comision.query.filter_by(nombre='Innovación y Tecnología Naval').first()
        if not comision2:
            comision2 = Comision(
                nombre='Innovación y Tecnología Naval',
                descripcion='Comisión enfocada en promover la innovación tecnológica en el sector naval, incluyendo digitalización, automatización y nuevas tecnologías de propulsión.',
                activa=True
            )
            db.session.add(comision2)
            db.session.commit()
            print("✅ Comisión 'Innovación y Tecnología Naval' creada")
            
            # Hacer al admin miembro de esta comisión
            membresia2 = MembresiaComision(
                usuario_id=admin.id,
                comision_id=comision2.id,
                estado='aprobado',
                rol='miembro'
            )
            db.session.add(membresia2)
            db.session.commit()
            print("✅ Admin agregado como miembro")
        
        # Crear usuario de prueba si no existe
        usuario_prueba = Usuario.query.filter_by(email='usuario@ejemplo.com').first()
        if not usuario_prueba:
            usuario_prueba = Usuario(
                email='usuario@ejemplo.com',
                nombre='Usuario',
                apellidos='De Prueba',
                telefono='600123456',
                razon_social='Empresa Naval S.L.',
                nombre_comercial='NavalTech',
                cargo='Ingeniero Naval',
                rol='usuario',
                activo=True
            )
            usuario_prueba.set_password('usuario123')
            db.session.add(usuario_prueba)
            db.session.commit()
            print("✅ Usuario de prueba creado (usuario@ejemplo.com / usuario123)")
        
        print("\n📊 Estado actual:")
        print(f"- Comisiones: {Comision.query.count()}")
        print(f"- Usuarios: {Usuario.query.count()}")
        print(f"- Membresías: {MembresiaComision.query.count()}")
        print(f"- Temas: {Tema.query.count()}")
        
        print("\n✨ Datos de ejemplo creados exitosamente")
        print("\n📝 Credenciales de acceso:")
        print(f"  Admin: {admin.email} / {os.environ.get('ADMIN_PASSWORD', 'admin123')}")
        if usuario_prueba:
            print("  Usuario: usuario@ejemplo.com / usuario123")

if __name__ == '__main__':
    try:
        crear_datos_ejemplo()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

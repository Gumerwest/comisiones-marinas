#!/usr/bin/env python3
"""
Script para verificar la configuración de Socket.IO
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_socketio():
    from app import create_app, socketio
    
    print("=== VERIFICACIÓN DE SOCKET.IO ===\n")
    
    # Verificar dependencias
    print("📦 DEPENDENCIAS:")
    try:
        import eventlet
        print("  ✅ eventlet instalado")
        print(f"     Versión: {eventlet.__version__}")
    except ImportError:
        print("  ❌ eventlet NO instalado - El chat no funcionará en producción")
    
    try:
        import socketio as sio
        print("  ✅ python-socketio instalado")
        print(f"     Versión: {sio.__version__}")
    except ImportError:
        print("  ❌ python-socketio NO instalado")
    
    try:
        import flask_socketio
        print("  ✅ Flask-SocketIO instalado")
        print(f"     Versión: {flask_socketio.__version__}")
    except ImportError:
        print("  ❌ Flask-SocketIO NO instalado")
    
    # Crear aplicación
    app = create_app()
    
    with app.app_context():
        print("\n🔧 CONFIGURACIÓN:")
        print(f"  - En Render: {'Sí' if os.environ.get('RENDER') else 'No'}")
        print(f"  - Async Mode: {app.config.get('SOCKETIO_ASYNC_MODE', 'default')}")
        print(f"  - Transports: {app.config.get('SOCKETIO_TRANSPORTS', 'default')}")
        print(f"  - CORS: {app.config.get('SOCKETIO_CORS_ALLOWED_ORIGINS', 'default')}")
        print(f"  - Logger: {app.config.get('SOCKETIO_LOGGER', True)}")
        print(f"  - Ping Timeout: {app.config.get('SOCKETIO_PING_TIMEOUT', 60)}s")
        print(f"  - Ping Interval: {app.config.get('SOCKETIO_PING_INTERVAL', 25)}s")
        
        # Verificar handlers registrados
        print("\n📡 HANDLERS REGISTRADOS:")
        if hasattr(socketio, 'handlers'):
            for namespace in socketio.handlers:
                print(f"  Namespace: {namespace}")
                for event in socketio.handlers[namespace]:
                    print(f"    - {event}")
        else:
            print("  ⚠️  No se puede verificar handlers (normal en producción)")
        
        # Verificar rutas Socket.IO
        print("\n🛣️  RUTAS SOCKET.IO:")
        socket_routes = []
        for rule in app.url_map.iter_rules():
            if 'socket.io' in str(rule):
                socket_routes.append(str(rule))
        
        if socket_routes:
            for route in socket_routes:
                print(f"  ✅ {route}")
        else:
            print("  ⚠️  No se encontraron rutas de Socket.IO explícitas")
            print("     (Esto es normal, Socket.IO las maneja internamente)")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        if os.environ.get('RENDER'):
            print("  Para Render:")
            print("  - Use solo 'polling' como transporte (más estable)")
            print("  - Use 'eventlet' como async_mode")
            print("  - Mantenga workers=1 en gunicorn")
            print("  - El comando debe ser: gunicorn run:app (no --factory)")
        else:
            print("  Para desarrollo local:")
            print("  - Puede usar 'polling' y 'websocket'")
            print("  - Use 'threading' como async_mode")
            print("  - No necesita eventlet en desarrollo")
        
        # Verificar problemas comunes
        print("\n⚠️  PROBLEMAS COMUNES:")
        if os.environ.get('RENDER'):
            if app.config.get('SOCKETIO_ASYNC_MODE') != 'eventlet':
                print("  ❌ Async mode debe ser 'eventlet' en Render")
            
            if 'websocket' in app.config.get('SOCKETIO_TRANSPORTS', []):
                print("  ⚠️  WebSocket puede no funcionar bien en Render")
                print("     Recomendado: usar solo ['polling']")
        
        print("\n✅ Verificación completada")
        
        # Test de conexión simple
        print("\n🧪 TEST DE CONEXIÓN:")
        print("  Para probar manualmente:")
        print("  1. Abra la aplicación en el navegador")
        print("  2. Vaya a una comisión o tema")
        print("  3. Abra la consola del navegador (F12)")
        print("  4. Debe ver mensajes de conexión del chat")
        print("  5. Si ve 'Conectado al servidor de chat', está funcionando")

if __name__ == '__main__':
    try:
        verify_socketio()
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()

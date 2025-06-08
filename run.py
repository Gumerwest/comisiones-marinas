import eventlet
eventlet.monkey_patch()
from app import create_app, socketio
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # En producción (Render), usar eventlet
    if os.environ.get('RENDER'):
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        # En desarrollo, usar el modo por defecto
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)

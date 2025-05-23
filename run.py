from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # En entorno de producción, Gunicorn maneja el servidor
    if os.environ.get('RENDER') is None:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # En Render, Gunicorn se encarga de ejecutar la app
        pass

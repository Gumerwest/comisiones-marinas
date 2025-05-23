from flask import Flask
from app import create_app, db
from flask_migrate import init, migrate, upgrade
import os

app = create_app()

@app.cli.command()
def init_db():
    """Initialize the database."""
    init()
    migrate(message='Initial migration')
    upgrade()
    print('Initialized the database.')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # En entorno de producción, Gunicorn maneja el servidor
    if os.environ.get('RENDER') is None:
        app.run(host='0.0.0.0', port=port, debug=False)

# Comisiones Marinas

Este proyecto es una aplicación web basada en Flask para gestionar comisiones marinas.

## Instalación

1. Clona este repositorio.
2. Instala las dependencias con `pip install -r requirements.txt`.
3. Asegúrate de tener un archivo `.env` con la configuración necesaria.

## Archivo `.env`

Dentro del repositorio se incluye un archivo `.env` de ejemplo. En él se definen las variables esenciales para que la aplicación funcione:

- `SECRET_KEY`: una cadena única que usa Flask para mantener la seguridad.
- `DATABASE_URL`: la ruta de la base de datos. Por defecto utiliza `sqlite:///app.db` para desarrollo local.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`: datos de tu servidor de correo si decides usar esta función.
- `ADMIN_EMAIL` y `ADMIN_PASSWORD`: credenciales del usuario administrador inicial.

Puedes copiar este `.env` y modificarlo según tus necesidades para realizar pruebas en tu propio entorno de desarrollo.

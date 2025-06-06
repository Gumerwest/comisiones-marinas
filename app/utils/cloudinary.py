import os
from flask import current_app
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
from datetime import datetime

def init_cloudinary():
    """Inicializar configuración de Cloudinary"""
    if not current_app.config.get('CLOUDINARY_ENABLED'):
        return False

    try:
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET']
        )
        return True
    except Exception as e:
        print(f"Error configurando Cloudinary: {str(e)}")
        return False

def upload_file_to_cloudinary(file, folder="documentos", resource_type="auto"):
    """
    Subir archivo a Cloudinary

    Args:
        file: Archivo de Flask/Werkzeug
        folder: Carpeta en Cloudinary
        resource_type: "auto", "image", "video", "raw"

    Returns:
        dict: Información del archivo subido o None si hay error
    """
    if not init_cloudinary():
        return None

    try:
        # Generar nombre único
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename_without_ext = os.path.splitext(original_filename)[0]
        extension = os.path.splitext(original_filename)[1]

        unique_filename = f"{timestamp}_{filename_without_ext}{extension}"

        # Subir a Cloudinary
        # `folder` ya agrupa las cargas, por lo que no debemos incluirlo de
        # nuevo en ``public_id``. Hacerlo duplicaba la ruta final generando
        # URLs con ``folder/folder``.
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            public_id=unique_filename,
            resource_type=resource_type,
            overwrite=False,
            unique_filename=False
        )

        return {
            'public_id': result['public_id'],
            'secure_url': result['secure_url'],
            'original_filename': original_filename,
            'format': result.get('format'),
            'bytes': result.get('bytes'),
            'created_at': result.get('created_at')
        }

    except Exception as e:
        print(f"Error subiendo archivo a Cloudinary: {str(e)}")
        return None

def upload_image_to_cloudinary(file, folder="imagenes"):
    """Subir imagen específicamente a Cloudinary"""
    return upload_file_to_cloudinary(file, folder=folder, resource_type="image")

def delete_file_from_cloudinary(public_id, resource_type="auto"):
    """
    Eliminar archivo de Cloudinary

    Args:
        public_id: ID público del archivo en Cloudinary
        resource_type: Tipo de recurso

    Returns:
        bool: True si se eliminó correctamente
    """
    if not init_cloudinary():
        return False

    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Error eliminando archivo de Cloudinary: {str(e)}")
        return False

def get_cloudinary_url(public_id, **options):
    """
    Generar URL de Cloudinary con transformaciones

    Args:
        public_id: ID público del archivo
        **options: Opciones de transformación (width, height, crop, etc.)

    Returns:
        str: URL del archivo
    """
    if not init_cloudinary():
        return None

    try:
        return cloudinary.CloudinaryImage(public_id).build_url(**options)
    except Exception as e:
        print(f"Error generando URL de Cloudinary: {str(e)}")
        return None

def validate_file_type(file, allowed_types=None):
    """
    Validar tipo de archivo

    Args:
        file: Archivo de Flask
        allowed_types: Lista de extensiones permitidas

    Returns:
        bool: True si el archivo es válido
    """
    if allowed_types is None:
        allowed_types = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                        'txt', 'jpg', 'jpeg', 'png', 'gif'}

    if not file or not file.filename:
        return False

    extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    return extension in allowed_types

def get_file_category(filename):
    """
    Determinar categoría del archivo basado en extensión

    Returns:
        str: 'image', 'document', 'spreadsheet', 'presentation', 'other'
    """
    if not filename or '.' not in filename:
        return 'other'

    extension = filename.rsplit('.', 1)[1].lower()

    categories = {
        'image': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'},
        'document': {'pdf', 'doc', 'docx', 'txt', 'rtf'},
        'spreadsheet': {'xls', 'xlsx', 'csv'},
        'presentation': {'ppt', 'pptx'},
        'other': set()
    }

    for category, extensions in categories.items():
        if extension in extensions:
            return category

    return 'other'

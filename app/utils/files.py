import os
from werkzeug.utils import secure_filename

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    """Verifica si el archivo es una imagen permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def get_file_extension(filename):
    """Obtiene la extensión del archivo"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def generate_unique_filename(filename, prefix=''):
    """Genera un nombre único para el archivo"""
    from datetime import datetime
    
    # Obtener nombre seguro
    safe_filename = secure_filename(filename)
    
    # Si no hay nombre válido, usar uno genérico
    if not safe_filename or safe_filename == '':
        extension = get_file_extension(filename)
        safe_filename = f'archivo.{extension}' if extension else 'archivo'
    
    # Generar timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # Crear nombre único
    if prefix:
        return f"{prefix}_{timestamp}_{safe_filename}"
    else:
        return f"{timestamp}_{safe_filename}"

def validate_file_size(file, max_size_mb=16):
    """Valida que el archivo no exceda el tamaño máximo"""
    # Obtener el tamaño del archivo
    file.seek(0, 2)  # Mover al final
    file_size = file.tell()
    file.seek(0)  # Volver al inicio
    
    # Convertir MB a bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    
    return file_size <= max_size_bytes

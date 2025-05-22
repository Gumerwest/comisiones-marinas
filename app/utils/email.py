from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error enviando email: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_notification_email(user, notification_type, data):
    """
    Envía notificaciones por email según el tipo de evento
    
    notification_type puede ser:
    - 'nuevo_tema': cuando se aprueba un nuevo tema
    - 'nuevo_comentario': cuando hay un nuevo comentario
    - 'nueva_reunion': cuando se programa una nueva reunión
    - 'nuevo_documento': cuando se sube un nuevo documento
    - 'membresia_aprobada': cuando se aprueba la membresía a una comisión
    """
    
    if not current_app.config.get('MAIL_SERVER'):
        print(f"Email no configurado. Notificación: {notification_type} para {user.email}")
        return
    
    sender = current_app.config['ADMINS'][0] if current_app.config.get('ADMINS') else 'noreply@comisionesmarinas.es'
    
    if notification_type == 'nuevo_tema':
        subject = f"Nuevo tema en la comisión {data['comision_nombre']}"
        text_body = f"""
        Hola {user.nombre},
        
        Se ha aprobado un nuevo tema en la comisión {data['comision_nombre']}:
        
        Título: {data['tema_titulo']}
        Resumen: {data['tema_resumen']}
        
        Puede ver más detalles en la plataforma.
        
        Saludos,
        Equipo de Comisiones Marinas de España
        """
        
    elif notification_type == 'nuevo_comentario':
        subject = f"Nuevo comentario en el tema {data['tema_titulo']}"
        text_body = f"""
        Hola {user.nombre},
        
        {data['comentario_autor']} ha añadido un nuevo comentario en el tema "{data['tema_titulo']}":
        
        {data['comentario_texto'][:200]}{'...' if len(data['comentario_texto']) > 200 else ''}
        
        Puede ver el comentario completo en la plataforma.
        
        Saludos,
        Equipo de Comisiones Marinas de España
        """
        
    elif notification_type == 'nueva_reunion':
        subject = f"Nueva reunión programada para el tema {data['tema_titulo']}"
        text_body = f"""
        Hola {user.nombre},
        
        Se ha programado una nueva reunión para el tema "{data['tema_titulo']}":
        
        Título: {data['reunion_titulo']}
        Fecha: {data['reunion_fecha']}
        Lugar: {data.get('reunion_lugar', 'Por definir')}
        
        Puede ver más detalles en la plataforma.
        
        Saludos,
        Equipo de Comisiones Marinas de España
        """
        
    elif notification_type == 'nuevo_documento':
        subject = f"Nuevo documento en el tema {data['tema_titulo']}"
        text_body = f"""
        Hola {user.nombre},
        
        Se ha subido un nuevo documento al tema "{data['tema_titulo']}":
        
        Nombre: {data['documento_nombre']}
        Descripción: {data.get('documento_descripcion', 'Sin descripción')}
        Subido por: {data['documento_autor']}
        
        Puede descargar el documento desde la plataforma.
        
        Saludos,
        Equipo de Comisiones Marinas de España
        """
        
    elif notification_type == 'membresia_aprobada':
        subject = f"Su membresía a la comisión {data['comision_nombre']} ha sido aprobada"
        text_body = f"""
        Hola {user.nombre},
        
        ¡Buenas noticias! Su solicitud de membresía a la comisión "{data['comision_nombre']}" ha sido aprobada.
        
        Ahora puede:
        - Ver todos los temas de la comisión
        - Proponer nuevos temas
        - Participar en las discusiones
        - Subir documentos
        - Proponer reuniones
        
        Acceda a la plataforma para comenzar a participar.
        
        Saludos,
        Equipo de Comisiones Marinas de España
        """
    else:
        return
    
    html_body = f"<html><body><pre>{text_body}</pre></body></html>"
    
    try:
        send_email(subject, sender, [user.email], text_body, html_body)
    except Exception as e:
        print(f"Error enviando notificación: {str(e)}")

def notify_members_of_commission(comision_id, notification_type, data):
    """
    Notifica a todos los miembros activos de una comisión
    """
    from app.models import Usuario, MembresiaComision
    
    miembros = Usuario.query.join(MembresiaComision).filter(
        MembresiaComision.comision_id == comision_id,
        MembresiaComision.estado == 'aprobado',
        Usuario.activo == True
    ).all()
    
    for miembro in miembros:
        send_notification_email(miembro, notification_type, data)

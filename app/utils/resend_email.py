import requests
from flask import current_app
from threading import Thread

def send_email_with_resend(to_email, subject, html_content, text_content=None):
    """
    Enviar email usando Resend API
    
    Args:
        to_email: Email del destinatario
        subject: Asunto del email
        html_content: Contenido HTML
        text_content: Contenido de texto plano (opcional)
    
    Returns:
        bool: True si se envió correctamente
    """
    resend_api_key = current_app.config.get('RESEND_API_KEY')
    
    if not resend_api_key:
        print("❌ Resend API key no configurada")
        return False
    
    from_email = current_app.config.get('RESEND_FROM_EMAIL', 'noreply@tudominio.com')
    
    url = "https://api.resend.com/emails"
    
    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    if text_content:
        payload["text"] = text_content
    
    headers = {
        "Authorization": f"Bearer {resend_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Email enviado a {to_email}")
            return True
        else:
            print(f"❌ Error enviando email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")
        return False

def send_async_email_resend(app, to_email, subject, html_content, text_content=None):
    """Enviar email de forma asíncrona"""
    with app.app_context():
        send_email_with_resend(to_email, subject, html_content, text_content)

def send_notification_email_resend(user, notification_type, data):
    """
    Envía notificaciones por email usando Resend según el tipo de evento
    """
    
    if not current_app.config.get('RESEND_API_KEY'):
        print(f"Email no configurado. Notificación: {notification_type} para {user.email}")
        return False
    
    # Generar contenido según tipo de notificación
    if notification_type == 'nuevo_tema':
        subject = f"🚢 Nuevo tema en {data['comision_nombre']}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 1.8rem;">🚢 Comisiones Marinas</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Nuevo tema disponible</p>
            </div>
            
            <div style="padding: 2rem; background: white;">
                <h2 style="color: #333; margin-bottom: 1rem;">Hola {user.nombre},</h2>
                
                <p>Se ha aprobado un nuevo tema en la comisión <strong>{data['comision_nombre']}</strong>:</p>
                
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                    <h3 style="color: #007bff; margin: 0 0 0.5rem 0;">{data['tema_titulo']}</h3>
                    <p style="margin: 0; color: #666; line-height: 1.5;">{data['tema_resumen']}</p>
                </div>
                
                <p>Puede ver más detalles y participar en la discusión accediendo a la plataforma.</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 1rem; text-align: center; color: #666; font-size: 0.9rem;">
                <p style="margin: 0;">Comisiones de Trabajo Marinas de España</p>
            </div>
        </div>
        """
        
    elif notification_type == 'membresia_aprobada':
        subject = f"🎉 Membresía aprobada en {data['comision_nombre']}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #28a745, #20c997); padding: 2rem; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 1.8rem;">🎉 ¡Bienvenido!</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Su membresía ha sido aprobada</p>
            </div>
            
            <div style="padding: 2rem; background: white;">
                <h2 style="color: #333;">¡Excelentes noticias, {user.nombre}!</h2>
                
                <p>Su solicitud de membresía a la comisión <strong>"{data['comision_nombre']}"</strong> ha sido aprobada.</p>
                
                <div style="background: #d4edda; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                    <h3 style="color: #155724; margin: 0 0 1rem 0;">Ahora puede:</h3>
                    <ul style="color: #155724; margin: 0; padding-left: 1.5rem;">
                        <li>Ver todos los temas de la comisión</li>
                        <li>Proponer nuevos temas</li>
                        <li>Participar en discusiones</li>
                        <li>Subir documentos</li>
                        <li>Proponer reuniones</li>
                    </ul>
                </div>
            </div>
        </div>
        """
    else:
        return False
    
    # Enviar email de forma asíncrona
    Thread(target=send_async_email_resend, 
           args=(current_app._get_current_object(), user.email, subject, html_content)).start()
    
    return True

def notify_members_of_commission_resend(comision_id, notification_type, data):
    """
    Notifica a todos los miembros activos de una comisión usando Resend
    """
    from app.models import Usuario, MembresiaComision
    
    miembros = Usuario.query.join(MembresiaComision).filter(
        MembresiaComision.comision_id == comision_id,
        MembresiaComision.estado == 'aprobado',
        Usuario.activo == True
    ).all()
    
    for miembro in miembros:
        send_notification_email_resend(miembro, notification_type, data)

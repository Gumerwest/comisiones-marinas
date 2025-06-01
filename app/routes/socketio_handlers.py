from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user
from app import socketio, db
from app.models import MensajeChat, Tema, Comision
from datetime import datetime
import traceback
import os

# Configuración específica para diferentes entornos
IS_RENDER = os.environ.get('RENDER')

@socketio.on('connect')
def handle_connect():
    try:
        if current_user.is_authenticated:
            print(f"✅ Usuario conectado: {current_user.email}")
            emit('connected', {
                'user_id': current_user.id,
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            print("❌ Usuario no autenticado intentó conectarse")
            emit('error', {'message': 'No autenticado'})
            disconnect()
    except Exception as e:
        print(f"❌ Error en connect: {str(e)}")
        if not IS_RENDER:  # Solo imprimir traceback en desarrollo
            traceback.print_exc()
        emit('error', {'message': 'Error de conexión'})

@socketio.on('disconnect')
def handle_disconnect():
    try:
        if current_user.is_authenticated:
            print(f"👋 Usuario desconectado: {current_user.email}")
    except Exception as e:
        print(f"⚠️ Error en disconnect: {str(e)}")

@socketio.on('join_comision')
def handle_join_comision(data):
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'No autenticado'})
            return
            
        comision_id = data.get('comision_id')
        if not comision_id:
            emit('error', {'message': 'ID de comisión requerido'})
            return
            
        # Verificar permisos
        if current_user.es_miembro_de(comision_id) or current_user.rol == 'admin':
            room = f'comision_{comision_id}'
            join_room(room)
            print(f"🏠 Usuario {current_user.email} se unió a {room}")
            emit('joined_room', {
                'room': room,
                'type': 'comision',
                'id': comision_id
            })
        else:
            emit('error', {'message': 'No es miembro de esta comisión'})
            
    except Exception as e:
        print(f"❌ Error en join_comision: {str(e)}")
        if not IS_RENDER:
            traceback.print_exc()
        emit('error', {'message': 'Error al unirse a la comisión'})

@socketio.on('leave_comision')
def handle_leave_comision(data):
    try:
        comision_id = data.get('comision_id')
        if comision_id:
            room = f'comision_{comision_id}'
            leave_room(room)
            emit('left_room', {'room': room})
            print(f"🚪 Usuario salió de {room}")
    except Exception as e:
        print(f"⚠️ Error en leave_comision: {str(e)}")

@socketio.on('join_tema')
def handle_join_tema(data):
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'No autenticado'})
            return
            
        tema_id = data.get('tema_id')
        if not tema_id:
            emit('error', {'message': 'ID de tema requerido'})
            return
            
        tema = Tema.query.get(tema_id)
        if not tema:
            emit('error', {'message': 'Tema no encontrado'})
            return
            
        # Verificar permisos
        if current_user.es_miembro_de(tema.comision_id) or current_user.rol == 'admin':
            room = f'tema_{tema_id}'
            join_room(room)
            print(f"💡 Usuario {current_user.email} se unió a {room}")
            emit('joined_room', {
                'room': room,
                'type': 'tema',
                'id': tema_id
            })
        else:
            emit('error', {'message': 'No es miembro de esta comisión'})
            
    except Exception as e:
        print(f"❌ Error en join_tema: {str(e)}")
        if not IS_RENDER:
            traceback.print_exc()
        emit('error', {'message': 'Error al unirse al tema'})

@socketio.on('leave_tema')
def handle_leave_tema(data):
    try:
        tema_id = data.get('tema_id')
        if tema_id:
            room = f'tema_{tema_id}'
            leave_room(room)
            emit('left_room', {'room': room})
            print(f"🚪 Usuario salió de {room}")
    except Exception as e:
        print(f"⚠️ Error en leave_tema: {str(e)}")

@socketio.on('send_message_comision')
def handle_message_comision(data):
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'No autenticado'})
            return
            
        comision_id = data.get('comision_id')
        mensaje_texto = data.get('mensaje', '').strip()
        
        if not comision_id or not mensaje_texto:
            emit('error', {'message': 'Datos incompletos'})
            return
            
        # Verificar permisos
        if not (current_user.es_miembro_de(comision_id) or current_user.rol == 'admin'):
            emit('error', {'message': 'Sin permisos'})
            return
        
        # Limitar longitud del mensaje
        if len(mensaje_texto) > 1000:
            emit('error', {'message': 'Mensaje demasiado largo (máximo 1000 caracteres)'})
            return
        
        # Guardar mensaje en la base de datos
        mensaje = MensajeChat(
            contenido=mensaje_texto,
            usuario_id=current_user.id,
            comision_id=comision_id
        )
        db.session.add(mensaje)
        db.session.commit()
        
        # Emitir mensaje a todos en la sala
        room = f'comision_{comision_id}'
        message_data = {
            'id': mensaje.id,
            'usuario': {
                'id': current_user.id,
                'nombre': current_user.nombre,
                'apellidos': current_user.apellidos,
                'initials': f"{current_user.nombre[0]}{current_user.apellidos[0]}"
            },
            'mensaje': mensaje_texto,
            'fecha': mensaje.fecha.strftime('%d/%m/%Y %H:%M'),
            'timestamp': mensaje.fecha.isoformat()
        }
        
        socketio.emit('new_message_comision', message_data, room=room)
        print(f"📨 Mensaje enviado a {room}: {mensaje_texto[:50]}...")
        
    except Exception as e:
        print(f"❌ Error en send_message_comision: {str(e)}")
        if not IS_RENDER:
            traceback.print_exc()
        db.session.rollback()
        emit('error', {'message': 'Error enviando mensaje'})

@socketio.on('send_message_tema')
def handle_message_tema(data):
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'No autenticado'})
            return
            
        tema_id = data.get('tema_id')
        mensaje_texto = data.get('mensaje', '').strip()
        
        if not tema_id or not mensaje_texto:
            emit('error', {'message': 'Datos incompletos'})
            return
        
        tema = Tema.query.get(tema_id)
        if not tema:
            emit('error', {'message': 'Tema no encontrado'})
            return
            
        # Verificar permisos
        if not (current_user.es_miembro_de(tema.comision_id) or current_user.rol == 'admin'):
            emit('error', {'message': 'Sin permisos'})
            return
        
        # Limitar longitud del mensaje
        if len(mensaje_texto) > 1000:
            emit('error', {'message': 'Mensaje demasiado largo (máximo 1000 caracteres)'})
            return
        
        # Guardar mensaje en la base de datos
        mensaje = MensajeChat(
            contenido=mensaje_texto,
            usuario_id=current_user.id,
            tema_id=tema_id
        )
        db.session.add(mensaje)
        db.session.commit()
        
        # Emitir mensaje a todos en la sala
        room = f'tema_{tema_id}'
        message_data = {
            'id': mensaje.id,
            'usuario': {
                'id': current_user.id,
                'nombre': current_user.nombre,
                'apellidos': current_user.apellidos,
                'initials': f"{current_user.nombre[0]}{current_user.apellidos[0]}"
            },
            'mensaje': mensaje_texto,
            'fecha': mensaje.fecha.strftime('%d/%m/%Y %H:%M'),
            'timestamp': mensaje.fecha.isoformat()
        }
        
        socketio.emit('new_message_tema', message_data, room=room)
        print(f"💬 Mensaje enviado a {room}: {mensaje_texto[:50]}...")
        
    except Exception as e:
        print(f"❌ Error en send_message_tema: {str(e)}")
        if not IS_RENDER:
            traceback.print_exc()
        db.session.rollback()
        emit('error', {'message': 'Error enviando mensaje'})

@socketio.on('get_messages_comision')
def handle_get_messages_comision(data):
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'No autenticado'})
            return
            
        comision_id = data.get('comision_id')
        limit = min(data.get('limit', 50), 100)  # Máximo 100 mensajes
        offset = data.get('offset', 0)
        
        if not comision_id:
            emit('error', {'message': 'ID de comisión requerido'})
            return
            
        # Verificar permisos
        if not (current_user.es_miembro_de(comision_id) or current_user.rol == 'admin'):
            emit('error', {'message': 'Sin permisos'})
            return
        
        # Obtener mensajes
        mensajes = MensajeChat.query.filter_by(comision_id=comision_id)\
            .order_by(MensajeChat.fecha.desc())\
            .limit(limit).offset(offset).all()
        
        mensajes_data = [{
            'id': m.id,
            'usuario': {
                'id': m.usuario.id,
                'nombre': m.usuario.nombre,
                'apellidos': m.usuario.apellidos,
                'initials': f"{m.usuario.nombre[0]}{m.usuario.apellidos[0]}"
            },
            'mensaje': m.contenido,
            'fecha': m.fecha.strftime('%d/%m/%Y %H:%M'),
            'timestamp': m.fecha.isoformat()
        } for m in reversed(mensajes)]
        
        emit('messages_comision', {
            'comision_id': comision_id,
            'mensajes': mensajes_data,
            'total': len(mensajes_data)
        })
        
        print(f"📥 Enviados {len(mensajes_data)} mensajes de comisión {comision_id}")
        
    except Exception as e:
        print(f"❌ Error en get_messages_comision: {str(e)}")
        if not IS_RENDER:
            traceback.print_exc()
        emit('error', {'message': 'Error obteniendo mensajes'})

@socketio.on('get_messages_tema')
def handle_get_messages_tema(data):
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'No autenticado'})
            return
            
        tema_id = data.get('tema_id')
        limit = min(data.get('limit', 50), 100)  # Máximo 100 mensajes
        offset = data.get('offset', 0)
        
        if not tema_id:
            emit('error', {'message': 'ID de tema requerido'})
            return
        
        tema = Tema.query.get(tema_id)
        if not tema:
            emit('error', {'message': 'Tema no encontrado'})
            return
            
        # Verificar permisos
        if not (current_user.es_miembro_de(tema.comision_id) or current_user.rol == 'admin'):
            emit('error', {'message': 'Sin permisos'})
            return
        
        # Obtener mensajes
        mensajes = MensajeChat.query.filter_by(tema_id=tema_id)\
            .order_by(MensajeChat.fecha.desc())\
            .limit(limit).offset(offset).all()
        
        mensajes_data = [{
            'id': m.id,
            'usuario': {
                'id': m.usuario.id,
                'nombre': m.usuario.nombre,
                'apellidos': m.usuario.apellidos,
                'initials': f"{m.usuario.nombre[0]}{m.usuario.apellidos[0]}"
            },
            'mensaje': m.contenido,
            'fecha': m.fecha.strftime('%d/%m/%Y %H:%M'),
            'timestamp': m.fecha.isoformat()
        } for m in reversed(mensajes)]
        
        emit('messages_tema', {
            'tema_id': tema_id,
            'mensajes': mensajes_data,
            'total': len(mensajes_data)
        })
        
        print(f"📥 Enviados {len(mensajes_data)} mensajes de tema {tema_id}")
        
    except Exception as e:
        print(f"❌ Error en get_messages_tema: {str(e)}")
        if not IS_RENDER:
            traceback.print_exc()
        emit('error', {'message': 'Error obteniendo mensajes'})

@socketio.on('ping')
def handle_ping():
    """Responder a ping para mantener conexión activa"""
    try:
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})
    except Exception as e:
        print(f"⚠️ Error en ping: {str(e)}")

@socketio.on_error_default
def default_error_handler(e):
    print(f"❌ Error general de SocketIO: {str(e)}")
    if not IS_RENDER:
        traceback.print_exc()
    emit('error', {'message': 'Error del servidor de chat'})

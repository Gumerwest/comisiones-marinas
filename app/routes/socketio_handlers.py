from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio, db
from app.models import MensajeChat
from datetime import datetime

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        emit('connected', {'user_id': current_user.id})

@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('join_comision')
def handle_join_comision(data):
    try:
        comision_id = data.get('comision_id')
        if comision_id and current_user.is_authenticated and current_user.es_miembro_de(comision_id):
            room = f'comision_{comision_id}'
            join_room(room)
            emit('joined_room', {'room': room}, room=room)
    except Exception as e:
        print(f"Error en join_comision: {str(e)}")

@socketio.on('leave_comision')
def handle_leave_comision(data):
    try:
        comision_id = data.get('comision_id')
        if comision_id:
            room = f'comision_{comision_id}'
            leave_room(room)
            emit('left_room', {'room': room}, room=room)
    except Exception as e:
        print(f"Error en leave_comision: {str(e)}")

@socketio.on('join_tema')
def handle_join_tema(data):
    try:
        tema_id = data.get('tema_id')
        if tema_id and current_user.is_authenticated:
            from app.models import Tema
            tema = Tema.query.get(tema_id)
            if tema and current_user.es_miembro_de(tema.comision_id):
                room = f'tema_{tema_id}'
                join_room(room)
                emit('joined_room', {'room': room}, room=room)
    except Exception as e:
        print(f"Error en join_tema: {str(e)}")

@socketio.on('leave_tema')
def handle_leave_tema(data):
    try:
        tema_id = data.get('tema_id')
        if tema_id:
            room = f'tema_{tema_id}'
            leave_room(room)
            emit('left_room', {'room': room}, room=room)
    except Exception as e:
        print(f"Error en leave_tema: {str(e)}")

@socketio.on('send_message_comision')
def handle_message_comision(data):
    try:
        comision_id = data.get('comision_id')
        mensaje_texto = data.get('mensaje')
        
        if not current_user.is_authenticated or not current_user.es_miembro_de(comision_id):
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
        emit('new_message_comision', {
            'id': mensaje.id,
            'usuario': {
                'id': current_user.id,
                'nombre': current_user.nombre,
                'apellidos': current_user.apellidos
            },
            'mensaje': mensaje_texto,
            'fecha': mensaje.fecha.strftime('%d/%m/%Y %H:%M')
        }, room=room)
    except Exception as e:
        print(f"Error en send_message_comision: {str(e)}")
        db.session.rollback()

@socketio.on('send_message_tema')
def handle_message_tema(data):
    try:
        tema_id = data.get('tema_id')
        mensaje_texto = data.get('mensaje')
        
        if not current_user.is_authenticated:
            return
        
        from app.models import Tema
        tema = Tema.query.get(tema_id)
        if not tema or not current_user.es_miembro_de(tema.comision_id):
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
        emit('new_message_tema', {
            'id': mensaje.id,
            'usuario': {
                'id': current_user.id,
                'nombre': current_user.nombre,
                'apellidos': current_user.apellidos
            },
            'mensaje': mensaje_texto,
            'fecha': mensaje.fecha.strftime('%d/%m/%Y %H:%M')
        }, room=room)
    except Exception as e:
        print(f"Error en send_message_tema: {str(e)}")
        db.session.rollback()

@socketio.on('get_messages_comision')
def handle_get_messages_comision(data):
    try:
        comision_id = data.get('comision_id')
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        
        if not current_user.is_authenticated or not current_user.es_miembro_de(comision_id):
            return
        
        mensajes = MensajeChat.query.filter_by(comision_id=comision_id)\
            .order_by(MensajeChat.fecha.desc())\
            .limit(limit).offset(offset).all()
        
        mensajes_data = [{
            'id': m.id,
            'usuario': {
                'id': m.usuario.id,
                'nombre': m.usuario.nombre,
                'apellidos': m.usuario.apellidos
            },
            'mensaje': m.contenido,
            'fecha': m.fecha.strftime('%d/%m/%Y %H:%M')
        } for m in reversed(mensajes)]
        
        emit('messages_comision', {
            'comision_id': comision_id,
            'mensajes': mensajes_data
        })
    except Exception as e:
        print(f"Error en get_messages_comision: {str(e)}")

@socketio.on('get_messages_tema')
def handle_get_messages_tema(data):
    try:
        tema_id = data.get('tema_id')
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        
        if not current_user.is_authenticated:
            return
        
        from app.models import Tema
        tema = Tema.query.get(tema_id)
        if not tema or not current_user.es_miembro_de(tema.comision_id):
            return
        
        mensajes = MensajeChat.query.filter_by(tema_id=tema_id)\
            .order_by(MensajeChat.fecha.desc())\
            .limit(limit).offset(offset).all()
        
        mensajes_data = [{
            'id': m.id,
            'usuario': {
                'id': m.usuario.id,
                'nombre': m.usuario.nombre,
                'apellidos': m.usuario.apellidos
            },
            'mensaje': m.contenido,
            'fecha': m.fecha.strftime('%d/%m/%Y %H:%M')
        } for m in reversed(mensajes)]
        
        emit('messages_tema', {
            'tema_id': tema_id,
            'mensajes': mensajes_data
        })
    except Exception as e:
        print(f"Error en get_messages_tema: {str(e)}")

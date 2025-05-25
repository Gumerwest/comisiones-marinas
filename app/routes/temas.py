from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Tema, Comision, Comentario, Documento, Reunion, Voto, LecturaComentario, Usuario
from app.forms.temas import TemaForm, PatrocinadorForm, ComentarioForm, DocumentoForm, ReunionForm
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('temas', __name__)

@bp.route('/<int:id>')
@login_required
def ver_tema(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Verificar si el usuario es miembro de la comisión
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para ver este tema', 'warning')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    # Obtener comentarios, documentos y reuniones
    comentarios = Comentario.query.filter_by(tema_id=tema.id).order_by(Comentario.fecha.asc()).all()
    documentos = Documento.query.filter_by(tema_id=tema.id).order_by(Documento.fecha_subida.desc()).all()
    reuniones = Reunion.query.filter_by(tema_id=tema.id).order_by(Reunion.fecha.asc()).all()
    
    # Verificar si el usuario ha votado este tema
    voto_usuario = Voto.query.filter_by(usuario_id=current_user.id, tema_id=tema.id).first()
    
    # Marcar comentarios como leídos
    for comentario in comentarios:
        # Verificar si ya está marcado como leído
        lectura = LecturaComentario.query.filter_by(
            usuario_id=current_user.id,
            comentario_id=comentario.id
        ).first()
        
        if not lectura:
            nueva_lectura = LecturaComentario(
                usuario_id=current_user.id,
                comentario_id=comentario.id
            )
            db.session.add(nueva_lectura)
    
    db.session.commit()
    
    return render_template('temas/ver.html',
                          title=tema.titulo,
                          tema=tema,
                          comentarios=comentarios,
                          documentos=documentos,
                          reuniones=reuniones,
                          voto_usuario=voto_usuario)

@bp.route('/crear/<int:comision_id>', methods=['GET', 'POST'])
@login_required
def crear_tema(comision_id):
    comision = Comision.query.get_or_404(comision_id)
    
    # Verificar si el usuario es miembro de la comisión
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para proponer temas', 'warning')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    form = TemaForm()
    if form.validate_on_submit():
        tema = Tema(
            titulo=form.titulo.data,
            resumen=form.resumen.data,
            situacion_actual=form.situacion_actual.data,
            comision_id=comision.id,
            creador_id=current_user.id
        )
        db.session.add(tema)
        db.session.commit()
        
        flash('Tema propuesto correctamente. Quedará pendiente de aprobación.', 'success')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    return render_template('temas/crear.html',
                          title='Proponer Tema',
                          form=form,
                          comision=comision)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_tema(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Verificar permisos (creador, coordinador o admin)
    if tema.creador_id != current_user.id and not current_user.es_coordinador_de(comision.id) and current_user.rol != 'admin':
        flash('No tiene permisos para editar este tema', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    form = TemaForm()
    if form.validate_on_submit():
        tema.titulo = form.titulo.data
        tema.resumen = form.resumen.data
        tema.situacion_actual = form.situacion_actual.data
        db.session.commit()
        
        flash('Tema actualizado correctamente', 'success')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    elif request.method == 'GET':
        form.titulo.data = tema.titulo
        form.resumen.data = tema.resumen
        form.situacion_actual.data = tema.situacion_actual
    
    return render_template('temas/editar.html',
                          title='Editar Tema',
                          form=form,
                          tema=tema)

@bp.route('/<int:id>/patrocinador', methods=['GET', 'POST'])
@login_required
def gestionar_patrocinador(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Solo coordinadores o admins pueden gestionar patrocinadores
    if not current_user.es_coordinador_de(comision.id) and current_user.rol != 'admin':
        flash('No tiene permisos para gestionar patrocinadores', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    form = PatrocinadorForm()
    if form.validate_on_submit():
        tema.patrocinador = form.patrocinador.data
        tema.enlace_patrocinador = form.enlace.data
        tema.solucion_patrocinador = form.solucion_patrocinador.data
        
        # Guardar logo si se proporciona
        if form.logo.data:
            filename = secure_filename(form.logo.data.filename)
            filename = f"patrocinador_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.logo.data.save(filepath)
            
            # Eliminar logo anterior si existe
            if tema.logo_patrocinador_path:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], tema.logo_patrocinador_path))
                except:
                    pass
            
            tema.logo_patrocinador_path = filename
        
        db.session.commit()
        flash('Información de patrocinador actualizada correctamente', 'success')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    elif request.method == 'GET':
        form.patrocinador.data = tema.patrocinador
        form.enlace.data = tema.enlace_patrocinador
        form.solucion_patrocinador.data = tema.solucion_patrocinador
    
    return render_template('temas/patrocinador.html',
                          title='Gestionar Patrocinador',
                          form=form,
                          tema=tema)

@bp.route('/<int:id>/aprobar', methods=['POST'])
@login_required
def aprobar_tema(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Solo coordinadores o admins pueden aprobar temas
    if not current_user.es_coordinador_de(comision.id) and current_user.rol != 'admin':
        flash('No tiene permisos para aprobar temas', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    tema.estado = 'aprobado'
    db.session.commit()
    
    # Notificar a los miembros
    from app.utils.email import notify_members_of_commission
    notify_members_of_commission(comision.id, 'nuevo_tema', {
        'comision_nombre': comision.nombre,
        'tema_titulo': tema.titulo,
        'tema_resumen': tema.resumen
    })
    
    flash('Tema aprobado correctamente', 'success')
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/<int:id>/rechazar', methods=['POST'])
@login_required
def rechazar_tema(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Solo coordinadores o admins pueden rechazar temas
    if not current_user.es_coordinador_de(comision.id) and current_user.rol != 'admin':
        flash('No tiene permisos para rechazar temas', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    tema.estado = 'rechazado'
    db.session.commit()
    
    flash('Tema rechazado', 'success')
    return redirect(url_for('comisiones.ver_comision', id=comision.id))

@bp.route('/<int:id>/nombrar_lider/<int:usuario_id>', methods=['POST'])
@login_required
def nombrar_lider_tema(id, usuario_id):
    tema = Tema.query.get_or_404(id)
    
    # Solo admins pueden nombrar líderes de tema
    if current_user.rol != 'admin':
        flash('No tiene permisos para nombrar líderes de tema', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    # Verificar que el usuario es miembro de la comisión
    usuario = Usuario.query.get_or_404(usuario_id)
    if not usuario.es_miembro_de(tema.comision_id):
        flash('El usuario debe ser miembro de la comisión para ser líder del tema', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    tema.lider_id = usuario_id
    db.session.commit()
    
    flash(f'{usuario.nombre} {usuario.apellidos} nombrado como líder del tema', 'success')
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/<int:id>/quitar_lider', methods=['POST'])
@login_required
def quitar_lider_tema(id):
    tema = Tema.query.get_or_404(id)
    
    # Solo admins pueden quitar líderes de tema
    if current_user.rol != 'admin':
        flash('No tiene permisos para quitar líderes de tema', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    tema.lider_id = None
    db.session.commit()
    
    flash('Líder del tema removido', 'success')
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/<int:id>/cerrar', methods=['POST'])
@login_required
def cerrar_tema(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Solo coordinadores, creador o admins pueden cerrar temas
    if tema.creador_id != current_user.id and not current_user.es_coordinador_de(comision.id) and current_user.rol != 'admin':
        flash('No tiene permisos para cerrar este tema', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    tema.estado = 'cerrado'
    db.session.commit()
    
    flash('Tema cerrado correctamente', 'success')
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/<int:id>/comentar', methods=['POST'])
@login_required
def comentar(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Verificar si el usuario es miembro de la comisión
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para comentar', 'warning')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    form = ComentarioForm()
    if form.validate_on_submit():
        comentario = Comentario(
            contenido=form.contenido.data,
            tema_id=tema.id,
            usuario_id=current_user.id
        )
        db.session.add(comentario)
        db.session.commit()
        
        # Notificar a los miembros
        from app.utils.email import notify_members_of_commission
        notify_members_of_commission(comision.id, 'nuevo_comentario', {
            'tema_titulo': tema.titulo,
            'comentario_autor': f"{current_user.nombre} {current_user.apellidos}",
            'comentario_texto': form.contenido.data
        })
        
        flash('Comentario añadido correctamente', 'success')
    
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/<int:id>/subir_documento', methods=['POST'])
@login_required
def subir_documento(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Verificar si el usuario es miembro de la comisión
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para subir documentos', 'warning')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    form = DocumentoForm()
    if form.validate_on_submit():
        # Guardar archivo
        file = form.documento.data
        filename = secure_filename(file.filename)
        filename = f"tema_{tema.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Determinar tipo de archivo
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        documento = Documento(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            path=filename,
            tipo=extension,
            tema_id=tema.id,
            usuario_id=current_user.id
        )
        db.session.add(documento)
        db.session.commit()
        
        # Notificar a los miembros
        from app.utils.email import notify_members_of_commission
        notify_members_of_commission(comision.id, 'nuevo_documento', {
            'tema_titulo': tema.titulo,
            'documento_nombre': documento.nombre,
            'documento_descripcion': documento.descripcion,
            'documento_autor': f"{current_user.nombre} {current_user.apellidos}"
        })
        
        flash('Documento subido correctamente', 'success')
    
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/<int:id>/proponer_reunion', methods=['GET', 'POST'])
@login_required
def proponer_reunion(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Verificar si el usuario es miembro de la comisión
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para proponer reuniones', 'warning')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    form = ReunionForm()
    if form.validate_on_submit():
        reunion = Reunion(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            fecha=form.fecha.data,
            duracion=form.duracion.data,
            lugar=form.lugar.data,
            enlace_virtual=form.enlace_virtual.data,
            tema_id=tema.id,
            creador_id=current_user.id
        )
        db.session.add(reunion)
        db.session.commit()
        
        flash('Reunión propuesta correctamente. Quedará pendiente de aprobación.', 'success')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    return render_template('temas/proponer_reunion.html',
                          title='Proponer Reunión',
                          form=form,
                          tema=tema)

@bp.route('/reunion/<int:id>/aprobar', methods=['POST'])
@login_required
def aprobar_reunion(id):
    reunion = Reunion.query.get_or_404(id)
    tema = reunion.tema
    comision = tema.comision
    
    # Solo coordinadores o admins pueden aprobar reuniones
    if not current_user.es_coordinador_de(comision.id) and current_user.rol != 'admin':
        flash('No tiene permisos para aprobar reuniones', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    reunion.estado = 'aprobada'
    db.session.commit()
    
    # Notificar a los miembros
    from app.utils.email import notify_members_of_commission
    notify_members_of_commission(comision.id, 'nueva_reunion', {
        'tema_titulo': tema.titulo,
        'reunion_titulo': reunion.titulo,
        'reunion_fecha': reunion.fecha.strftime('%d/%m/%Y %H:%M'),
        'reunion_lugar': reunion.lugar or 'Virtual'
    })
    
    flash('Reunión aprobada correctamente', 'success')
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/reunion/<int:id>/rechazar', methods=['POST'])
@login_required
def rechazar_reunion(id):
    reunion = Reunion.query.get_or_404(id)
    tema = reunion.tema
    comision = tema.comision
    
    # Solo coordinadores o admins pueden rechazar reuniones
    if not current_user.es_coordinador_de(comision.id) and current_user.rol != 'admin':
        flash('No tiene permisos para rechazar reuniones', 'danger')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    reunion.estado = 'rechazada'
    db.session.commit()
    
    flash('Reunión rechazada', 'success')
    return redirect(url_for('temas.ver_tema', id=tema.id))

@bp.route('/<int:id>/votar', methods=['POST'])
@login_required
def votar(id):
    tema = Tema.query.get_or_404(id)
    comision = tema.comision
    
    # Verificar si el usuario es miembro de la comisión
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para votar', 'warning')
        return redirect(url_for('temas.ver_tema', id=tema.id))
    
    # Verificar si ya ha votado
    voto_existente = Voto.query.filter_by(
        usuario_id=current_user.id,
        tema_id=tema.id
    ).first()
    
    if voto_existente:
        # Si ya votó, eliminar el voto (toggle)
        db.session.delete(voto_existente)
        flash('Voto eliminado', 'info')
    else:
        # Si no ha votado, añadir voto
        voto = Voto(
            usuario_id=current_user.id,
            tema_id=tema.id
        )
        db.session.add(voto)
        flash('Voto registrado correctamente', 'success')
    
    db.session.commit()
    return redirect(url_for('temas.ver_tema', id=tema.id))

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Comision, MembresiaComision, Tema, Usuario, DocumentoComision
from app.forms.comisiones import ComisionForm, SolicitudMembresiaForm
from app.forms.temas import DocumentoComisionForm
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('comisiones', __name__)

@bp.route('/')
@login_required
def listar_comisiones():
    comisiones = Comision.query.filter_by(activa=True).all()
    return render_template('comisiones/listar.html', title='Comisiones', comisiones=comisiones)

@bp.route('/<int:id>')
@login_required
def ver_comision(id):
    comision = Comision.query.get_or_404(id)
    es_miembro = current_user.es_miembro_de(comision.id)
    es_coordinador = current_user.es_coordinador_de(comision.id)
    es_lider = current_user.es_lider_de(comision.id)
    
    # Verificar si ya tiene una solicitud pendiente
    solicitud_pendiente = MembresiaComision.query.filter_by(
        usuario_id=current_user.id,
        comision_id=comision.id,
        estado='pendiente_aprobacion'
    ).first() is not None
    
    # Obtener temas aprobados para esta comisión
    temas = Tema.query.filter_by(
        comision_id=comision.id,
        estado='aprobado'
    ).order_by(Tema.fecha_creacion.desc()).all()
    
    # Obtener miembros de la comisión con sus roles - CORREGIDO
    miembros_query = db.session.query(MembresiaComision, Usuario).join(
        Usuario, MembresiaComision.usuario_id == Usuario.id
    ).filter(
        MembresiaComision.comision_id == comision.id,
        MembresiaComision.estado == 'aprobado'
    ).all()
    
    # Organizar miembros por rol - CORREGIDO
    lideres = [(m.usuario, m) for m, u in miembros_query if m.rol == 'lider']
    coordinadores = [(m.usuario, m) for m, u in miembros_query if m.rol == 'coordinador']
    miembros = [(m.usuario, m) for m, u in miembros_query if m.rol == 'miembro']
    
    return render_template('comisiones/ver.html', 
                          title=comision.nombre,
                          comision=comision,
                          es_miembro=es_miembro,
                          es_coordinador=es_coordinador,
                          es_lider=es_lider,
                          solicitud_pendiente=solicitud_pendiente,
                          temas=temas,
                          lideres=lideres,
                          coordinadores=coordinadores,
                          miembros=miembros,
                          total_miembros=len(miembros_query))

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_comision():
    # Solo administradores pueden crear comisiones
    if current_user.rol != 'admin':
        flash('No tiene permisos para crear comisiones', 'danger')
        return redirect(url_for('comisiones.listar_comisiones'))
    
    form = ComisionForm()
    if form.validate_on_submit():
        comision = Comision(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data
        )
        
        # Guardar imagen si se proporciona
        if form.imagen.data:
            filename = secure_filename(form.imagen.data.filename)
            # Generar nombre único para evitar colisiones
            filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.imagen.data.save(filepath)
            comision.imagen_path = filename
        
        db.session.add(comision)
        db.session.commit()
        
        # Crear membresía automática para el creador como coordinador
        membresia = MembresiaComision(
            usuario_id=current_user.id,
            comision_id=comision.id,
            estado='aprobado',
            rol='coordinador'
        )
        db.session.add(membresia)
        db.session.commit()
        
        flash('Comisión creada correctamente', 'success')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    return render_template('comisiones/crear.html', title='Crear Comisión', form=form)

@bp.route('/<int:id>/solicitar', methods=['GET', 'POST'])
@login_required
def solicitar_membresia(id):
    comision = Comision.query.get_or_404(id)
    
    # Verificar si ya es miembro o tiene solicitud pendiente
    if current_user.es_miembro_de(comision.id):
        flash('Ya es miembro de esta comisión', 'info')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    solicitud_existente = MembresiaComision.query.filter_by(
        usuario_id=current_user.id,
        comision_id=comision.id
    ).first()
    
    if solicitud_existente and solicitud_existente.estado == 'pendiente_aprobacion':
        flash('Ya tiene una solicitud pendiente para esta comisión', 'info')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    form = SolicitudMembresiaForm()
    if form.validate_on_submit():
        membresia = MembresiaComision(
            usuario_id=current_user.id,
            comision_id=comision.id,
            estado='pendiente_aprobacion'
        )
        db.session.add(membresia)
        db.session.commit()
        flash('Solicitud enviada correctamente. Recibirá una notificación cuando sea aprobada.', 'success')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    return render_template('comisiones/solicitar.html', 
                          title='Solicitar Membresía',
                          comision=comision,
                          form=form)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_comision(id):
    comision = Comision.query.get_or_404(id)
    
    # Solo administradores o coordinadores pueden editar
    if current_user.rol != 'admin' and not current_user.es_coordinador_de(comision.id):
        flash('No tiene permisos para editar esta comisión', 'danger')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    form = ComisionForm()
    if form.validate_on_submit():
        comision.nombre = form.nombre.data
        comision.descripcion = form.descripcion.data
        
        # Actualizar imagen si se proporciona una nueva
        if form.imagen.data:
            filename = secure_filename(form.imagen.data.filename)
            filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.imagen.data.save(filepath)
            
            # Eliminar imagen anterior si existe
            if comision.imagen_path:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], comision.imagen_path))
                except:
                    pass
            
            comision.imagen_path = filename
        
        db.session.commit()
        flash('Comisión actualizada correctamente', 'success')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    elif request.method == 'GET':
        form.nombre.data = comision.nombre
        form.descripcion.data = comision.descripcion
    
    return render_template('comisiones/editar.html', 
                          title='Editar Comisión',
                          comision=comision,
                          form=form)

@bp.route('/<int:id>/miembros')
@login_required
def listar_miembros(id):
    comision = Comision.query.get_or_404(id)
    
    # Solo miembros pueden ver la lista completa
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para ver la lista completa de miembros', 'warning')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    # Obtener miembros aprobados con sus roles - CORREGIDO
    miembros_query = db.session.query(MembresiaComision, Usuario).join(
        Usuario, MembresiaComision.usuario_id == Usuario.id
    ).filter(
        MembresiaComision.comision_id == comision.id,
        MembresiaComision.estado == 'aprobado'
    ).all()
    
    # Organizar miembros por rol - CORREGIDO
    lideres = [(m.usuario, m) for m, u in miembros_query if m.rol == 'lider']
    coordinadores = [(m.usuario, m) for m, u in miembros_query if m.rol == 'coordinador']
    miembros = [(m.usuario, m) for m, u in miembros_query if m.rol == 'miembro']
    
    # Si es admin o coordinador, mostrar también solicitudes pendientes
    solicitudes = []
    if current_user.rol == 'admin' or current_user.es_coordinador_de(comision.id):
        solicitudes_query = db.session.query(MembresiaComision, Usuario).join(
            Usuario, MembresiaComision.usuario_id == Usuario.id
        ).filter(
            MembresiaComision.comision_id == comision.id,
            MembresiaComision.estado == 'pendiente_aprobacion'
        ).all()
        solicitudes = [(m.usuario, m) for m, u in solicitudes_query]
    
    return render_template('comisiones/miembros.html',
                          title=f'Miembros de {comision.nombre}',
                          comision=comision,
                          lideres=lideres,
                          coordinadores=coordinadores,
                          miembros=miembros,
                          solicitudes=solicitudes,
                          es_coordinador=current_user.es_coordinador_de(comision.id))

@bp.route('/<int:comision_id>/aprobar_miembro/<int:usuario_id>', methods=['POST'])
@login_required
def aprobar_miembro(comision_id, usuario_id):
    # Solo admins o coordinadores pueden aprobar
    if current_user.rol != 'admin' and not current_user.es_coordinador_de(comision_id):
        flash('No tiene permisos para aprobar miembros', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id,
        estado='pendiente_aprobacion'
    ).first_or_404()
    
    membresia.estado = 'aprobado'
    db.session.commit()
    
    # Notificar al usuario
    from app.utils.email import send_notification_email
    usuario = Usuario.query.get(usuario_id)
    comision = Comision.query.get(comision_id)
    send_notification_email(usuario, 'membresia_aprobada', {
        'comision_nombre': comision.nombre
    })
    
    flash('Miembro aprobado correctamente', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

@bp.route('/<int:comision_id>/rechazar_miembro/<int:usuario_id>', methods=['POST'])
@login_required
def rechazar_miembro(comision_id, usuario_id):
    # Solo admins o coordinadores pueden rechazar
    if current_user.rol != 'admin' and not current_user.es_coordinador_de(comision_id):
        flash('No tiene permisos para rechazar miembros', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id,
        estado='pendiente_aprobacion'
    ).first_or_404()
    
    db.session.delete(membresia)
    db.session.commit()
    
    flash('Solicitud rechazada', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

@bp.route('/<int:comision_id>/nombrar_coordinador/<int:usuario_id>', methods=['POST'])
@login_required
def nombrar_coordinador(comision_id, usuario_id):
    # Solo admins pueden nombrar coordinadores
    if current_user.rol != 'admin':
        flash('No tiene permisos para nombrar coordinadores', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id,
        estado='aprobado'
    ).first_or_404()
    
    membresia.rol = 'coordinador'
    db.session.commit()
    
    flash('Coordinador nombrado correctamente', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

@bp.route('/<int:comision_id>/nombrar_lider/<int:usuario_id>', methods=['POST'])
@login_required
def nombrar_lider(comision_id, usuario_id):
    # Solo admins pueden nombrar líderes
    if current_user.rol != 'admin':
        flash('No tiene permisos para nombrar líderes', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id,
        estado='aprobado'
    ).first_or_404()
    
    membresia.rol = 'lider'
    db.session.commit()
    
    flash('Líder nombrado correctamente', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

@bp.route('/<int:comision_id>/quitar_coordinador/<int:usuario_id>', methods=['POST'])
@login_required
def quitar_coordinador(comision_id, usuario_id):
    # Solo admins pueden quitar coordinadores
    if current_user.rol != 'admin':
        flash('No tiene permisos para quitar coordinadores', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id,
        estado='aprobado',
        rol='coordinador'
    ).first_or_404()
    
    membresia.rol = 'miembro'
    db.session.commit()
    
    flash('Rol de coordinador revocado correctamente', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

@bp.route('/<int:comision_id>/quitar_lider/<int:usuario_id>', methods=['POST'])
@login_required
def quitar_lider(comision_id, usuario_id):
    # Solo admins pueden quitar líderes
    if current_user.rol != 'admin':
        flash('No tiene permisos para quitar líderes', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id,
        estado='aprobado',
        rol='lider'
    ).first_or_404()
    
    membresia.rol = 'miembro'
    db.session.commit()
    
    flash('Rol de líder revocado correctamente', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

@bp.route('/<int:comision_id>/eliminar_miembro/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_miembro(comision_id, usuario_id):
    # Solo admins pueden eliminar miembros
    if current_user.rol != 'admin':
        flash('No tiene permisos para eliminar miembros', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    # No permitir que se elimine a sí mismo
    if usuario_id == current_user.id:
        flash('No puede eliminarse a sí mismo de la comisión', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id
    ).first_or_404()
    
    db.session.delete(membresia)
    db.session.commit()
    
    flash('Miembro eliminado de la comisión correctamente', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

@bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_comision(id):
    # Solo admins pueden eliminar comisiones
    if current_user.rol != 'admin':
        flash('No tiene permisos para eliminar comisiones', 'danger')
        return redirect(url_for('comisiones.ver_comision', id=id))
    
    comision = Comision.query.get_or_404(id)
    comision.activa = False
    db.session.commit()
    
    flash('Comisión eliminada correctamente', 'success')
    return redirect(url_for('comisiones.listar_comisiones'))

@bp.route('/<int:id>/subir_documento', methods=['POST'])
@login_required
def subir_documento(id):
    comision = Comision.query.get_or_404(id)
    
    # Verificar si el usuario es miembro de la comisión
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para subir documentos', 'warning')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    form = DocumentoComisionForm()
    if form.validate_on_submit():
        # Guardar archivo
        file = form.documento.data
        filename = secure_filename(file.filename)
        filename = f"comision_{comision.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Determinar tipo de archivo
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        documento = DocumentoComision(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            path=filename,
            tipo=extension,
            comision_id=comision.id,
            usuario_id=current_user.id
        )
        db.session.add(documento)
        db.session.commit()
        
        # Notificar a los miembros
        from app.utils.email import notify_members_of_commission
        notify_members_of_commission(comision.id, 'nuevo_documento', {
            'comision_nombre': comision.nombre,
            'documento_nombre': documento.nombre,
            'documento_descripcion': documento.descripcion,
            'documento_autor': f"{current_user.nombre} {current_user.apellidos}"
        })
        
        flash('Documento subido correctamente', 'success')
    
    return redirect(url_for('comisiones.ver_comision', id=comision.id) + '#documentacion')

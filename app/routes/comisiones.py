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

# Importar la función upload_file_to_storage de temas.py
def upload_file_to_storage(file, folder="comisiones"):
    """Subir archivo a Cloudinary o almacenamiento local"""
    if not file or not file.filename:
        return None
    
    # Si Cloudinary está configurado, usarlo
    if current_app.config.get('USE_CLOUDINARY'):
        try:
            import cloudinary
            import cloudinary.uploader
            
            # Configurar Cloudinary
            cloudinary.config(
                cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
                api_key=current_app.config.get('CLOUDINARY_API_KEY'),
                api_secret=current_app.config.get('CLOUDINARY_API_SECRET'),
                secure=True
            )
            
            # Generar nombre único
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            original_filename = secure_filename(file.filename)
            
            # Subir a Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                public_id=f"{timestamp}_{original_filename}",
                resource_type="auto",
                overwrite=False
            )
            print(f"✅ Archivo subido a Cloudinary: {result['public_id']}")
            return result['secure_url']  # Devolver URL completa
        except Exception as e:
            print(f"❌ Error subiendo a Cloudinary: {str(e)}")
            return None
    else:
        # Usar filesystem local (solo para desarrollo)
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if not upload_folder:
                return None
                
            os.makedirs(upload_folder, exist_ok=True)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            print(f"✅ Archivo guardado localmente: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error guardando archivo local: {str(e)}")
            return None

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
    
    # Obtener miembros de la comisión con sus roles
    miembros_query = db.session.query(MembresiaComision, Usuario).join(
        Usuario, MembresiaComision.usuario_id == Usuario.id
    ).filter(
        MembresiaComision.comision_id == comision.id,
        MembresiaComision.estado == 'aprobado'
    ).all()
    
    # Organizar miembros por rol
    lideres = [(m.usuario, m) for m, u in miembros_query if m.rol == 'lider']
    coordinadores = [(m.usuario, m) for m, u in miembros_query if m.rol == 'coordinador']
    miembros = [(m.usuario, m) for m, u in miembros_query if m.rol == 'miembro']
    
    # Obtener documentos ordenados
    documentos_ordenados = DocumentoComision.query.filter_by(
        comision_id=comision.id
    ).order_by(DocumentoComision.fecha_subida.desc()).all()
    
    # Función now para las plantillas
    from datetime import datetime as dt
    now = dt.utcnow
    
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
                          total_miembros=len(miembros_query),
                          documentos_ordenados=documentos_ordenados,
                          now=now,
                          config=current_app.config)

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_comision():
    # Solo administradores pueden crear comisiones
    if current_user.rol != 'admin':
        flash('No tiene permisos para crear comisiones', 'danger')
        return redirect(url_for('comisiones.listar_comisiones'))
    
    form = ComisionForm()
    if form.validate_on_submit():
        try:
            comision = Comision(
                nombre=form.nombre.data,
                descripcion=form.descripcion.data
            )
            
            # Manejo de imagen mejorado para Cloudinary
            if form.imagen.data and current_app.config.get('UPLOADS_ENABLED', False):
                try:
                    if current_app.config.get('USE_CLOUDINARY'):
                        # Usar Cloudinary
                        imagen_url = upload_file_to_storage(form.imagen.data, "comisiones")
                        if imagen_url:
                            comision.imagen_path = imagen_url  # Guardar URL completa
                            flash('Imagen subida correctamente a Cloudinary', 'success')
                        else:
                            flash('Error subiendo la imagen', 'warning')
                    else:
                        # Código existente para desarrollo local
                        filename = secure_filename(form.imagen.data.filename)
                        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        upload_folder = current_app.config.get('UPLOAD_FOLDER')
                        if upload_folder and os.path.exists(upload_folder):
                            os.makedirs(upload_folder, exist_ok=True)
                            filepath = os.path.join(upload_folder, filename)
                            form.imagen.data.save(filepath)
                            comision.imagen_path = filename
                except Exception as e:
                    print(f"Error con imagen: {str(e)}")
                    flash('La imagen no pudo ser guardada', 'warning')
            elif form.imagen.data and not current_app.config.get('UPLOADS_ENABLED', False):
                flash('La carga de imágenes no está disponible. Configure Cloudinary para habilitarla.', 'info')
            
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
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando comisión: {str(e)}")
            flash(f'Error al crear la comisión: {str(e)}', 'danger')
            return redirect(url_for('comisiones.crear_comision'))
    
    return render_template('comisiones/crear.html', 
                          title='Crear Comisión', 
                          form=form,
                          config=current_app.config)

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
        try:
            comision.nombre = form.nombre.data
            comision.descripcion = form.descripcion.data
            
            # Actualizar imagen si se proporciona una nueva
            if form.imagen.data and current_app.config.get('UPLOADS_ENABLED', False):
                try:
                    if current_app.config.get('USE_CLOUDINARY'):
                        # Usar Cloudinary
                        imagen_url = upload_file_to_storage(form.imagen.data, "comisiones")
                        if imagen_url:
                            # TODO: Eliminar imagen anterior de Cloudinary si existe
                            comision.imagen_path = imagen_url
                            flash('Imagen actualizada correctamente', 'success')
                        else:
                            flash('Error actualizando la imagen', 'warning')
                    else:
                        # Código existente para desarrollo local
                        filename = secure_filename(form.imagen.data.filename)
                        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        upload_folder = current_app.config.get('UPLOAD_FOLDER')
                        if upload_folder and os.path.exists(upload_folder):
                            os.makedirs(upload_folder, exist_ok=True)
                            filepath = os.path.join(upload_folder, filename)
                            form.imagen.data.save(filepath)
                            
                            # Eliminar imagen anterior si existe
                            if comision.imagen_path and upload_folder:
                                try:
                                    old_path = os.path.join(upload_folder, comision.imagen_path)
                                    if os.path.exists(old_path):
                                        os.remove(old_path)
                                except:
                                    pass
                            
                            comision.imagen_path = filename
                except Exception as e:
                    print(f"Error actualizando imagen: {str(e)}")
                    flash('La imagen no pudo ser actualizada', 'warning')
            elif form.imagen.data and not current_app.config.get('UPLOADS_ENABLED', False):
                flash('La carga de imágenes no está disponible. Configure Cloudinary para habilitarla.', 'info')
            
            db.session.commit()
            flash('Comisión actualizada correctamente', 'success')
            return redirect(url_for('comisiones.ver_comision', id=comision.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error editando comisión: {str(e)}")
            flash('Error al actualizar la comisión', 'danger')
            
    elif request.method == 'GET':
        form.nombre.data = comision.nombre
        form.descripcion.data = comision.descripcion
    
    return render_template('comisiones/editar.html', 
                          title='Editar Comisión',
                          comision=comision,
                          form=form,
                          config=current_app.config)

@bp.route('/<int:id>/miembros')
@login_required
def listar_miembros(id):
    comision = Comision.query.get_or_404(id)
    
    # Solo miembros pueden ver la lista completa
    if not current_user.es_miembro_de(comision.id) and current_user.rol != 'admin':
        flash('Debe ser miembro de la comisión para ver la lista completa de miembros', 'warning')
        return redirect(url_for('comisiones.ver_comision', id=comision.id))
    
    # Obtener miembros aprobados con sus roles
    miembros_query = db.session.query(MembresiaComision, Usuario).join(
        Usuario, MembresiaComision.usuario_id == Usuario.id
    ).filter(
        MembresiaComision.comision_id == comision.id,
        MembresiaComision.estado == 'aprobado'
    ).all()
    
    # Organizar miembros por rol
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
    try:
        # Primero intentar con Resend
        from app.utils.resend_email import send_notification_email_resend
        usuario = Usuario.query.get(usuario_id)
        comision = Comision.query.get(comision_id)
        send_notification_email_resend(usuario, 'membresia_aprobada', {
            'comision_nombre': comision.nombre
        })
        print(f"✅ Email enviado con Resend a {usuario.email}")
    except:
        # Si falla, intentar con el sistema tradicional
        try:
            from app.utils.email import send_notification_email
            usuario = Usuario.query.get(usuario_id)
            comision = Comision.query.get(comision_id)
            send_notification_email(usuario, 'membresia_aprobada', {
                'comision_nombre': comision.nombre
            })
            print(f"✅ Email enviado con Flask-Mail a {usuario.email}")
        except Exception as e:
            print(f"❌ Error enviando email: {str(e)}")
            # No bloquear el proceso si falla el email
            pass
    
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
    
    # Verificar si los uploads están habilitados
    if not current_app.config.get('UPLOADS_ENABLED', False):
        flash('La carga de archivos no está disponible. Configure Cloudinary para habilitarla.', 'warning')
        return redirect(url_for('comisiones.ver_comision', id=comision.id) + '#documentacion')
    
    form = DocumentoComisionForm()
    if form.validate_on_submit():
        try:
            # Subir archivo usando la función mejorada
            file = form.documento.data
            file_url = upload_file_to_storage(file, f"comisiones/{comision.id}/documentos")
            
            if file_url:
                # Determinar tipo de archivo
                extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                
                documento = DocumentoComision(
                    nombre=form.nombre.data,
                    descripcion=form.descripcion.data,
                    path=file_url,
                    tipo=extension,
                    comision_id=comision.id,
                    usuario_id=current_user.id
                )
                db.session.add(documento)
                db.session.commit()
                
                flash('Documento subido correctamente', 'success')
            else:
                flash('Error al subir el documento', 'danger')
        except Exception as e:
            db.session.rollback()
            print(f"Error subiendo documento: {str(e)}")
            flash('Error al subir el documento', 'danger')
    
    return redirect(url_for('comisiones.ver_comision', id=comision.id) + '#documentacion')

@bp.route('/<int:comision_id>/nombrar_lider_comision/<int:usuario_id>', methods=['POST'])
@login_required
def nombrar_lider_comision(comision_id, usuario_id):
    # Solo admins pueden nombrar líderes de comisión
    if current_user.rol != 'admin':
        flash('No tiene permisos para nombrar líderes de comisión', 'danger')
        return redirect(url_for('comisiones.listar_miembros', id=comision_id))
    
    membresia = MembresiaComision.query.filter_by(
        comision_id=comision_id,
        usuario_id=usuario_id,
        estado='aprobado'
    ).first_or_404()
    
    # Quitar el rol de líder a cualquier líder anterior
    MembresiaComision.query.filter_by(
        comision_id=comision_id,
        rol='lider'
    ).update({'rol': 'miembro'})
    
    # Asignar nuevo líder
    membresia.rol = 'lider'
    db.session.commit()
    
    flash('Líder de comisión nombrado correctamente', 'success')
    return redirect(url_for('comisiones.listar_miembros', id=comision_id))

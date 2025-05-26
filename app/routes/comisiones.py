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
    
    # IMPORTANTE: Obtener documentos ordenados aquí en Python
    documentos_ordenados = DocumentoComision.query.filter_by(
        comision_id=comision.id
    ).order_by(DocumentoComision.fecha_subida.desc()).all()
    
    # Añadir función now para las plantillas
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
                          documentos_ordenados=documentos_ordenados,  # Pasar documentos ya ordenados
                          now=now)

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
            
            # Manejo de imagen con soporte para Render
            if form.imagen.data:
                try:
                    filename = secure_filename(form.imagen.data.filename)
                    # Generar nombre único
                    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    
                    if os.environ.get('RENDER'):
                        # En Render, no guardamos imágenes
                        print("En Render: Saltando guardado de imagen")
                        # Opcionalmente, podrías subir a un servicio externo como S3
                        # Por ahora, simplemente no guardamos la imagen
                        pass
                    else:
                        # En desarrollo local
                        upload_folder = current_app.config.get('UPLOAD_FOLDER')
                        if upload_folder:
                            os.makedirs(upload_folder, exist_ok=True)
                            filepath = os.path.join(upload_folder, filename)
                            form.imagen.data.save(filepath)
                            comision.imagen_path = filename
                except Exception as e:
                    print(f"Error con imagen: {str(e)}")
                    flash('La imagen no pudo ser guardada, pero la comisión se creará sin imagen', 'warning')
            
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
        mem

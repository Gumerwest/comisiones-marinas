from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Usuario, Comision, MembresiaComision, Tema
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__)

@bp.route('/')
@login_required
def index():
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para acceder al panel de administración', 'danger')
        return redirect(url_for('main.index'))
    
    # Estadísticas para el dashboard
    usuarios_count = Usuario.query.count()
    usuarios_pendientes = Usuario.query.filter_by(activo=False).count()
    comisiones_count = Comision.query.count()
    temas_count = Tema.query.count()
    temas_pendientes = Tema.query.filter_by(estado='pendiente_aprobacion').count()
    
    return render_template('admin/index.html', 
                          title='Panel de Administración',
                          usuarios_count=usuarios_count,
                          usuarios_pendientes=usuarios_pendientes,
                          comisiones_count=comisiones_count,
                          temas_count=temas_count,
                          temas_pendientes=temas_pendientes)

@bp.route('/usuarios')
@login_required
def listar_usuarios():
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('main.index'))
    
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    return render_template('admin/usuarios.html', 
                          title='Gestión de Usuarios',
                          usuarios=usuarios)

@bp.route('/usuarios/<int:id>/aprobar', methods=['POST'])
@login_required
def aprobar_usuario(id):
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para realizar esta acción', 'danger')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    usuario.activo = True
    db.session.commit()
    
    flash(f'Usuario {usuario.email} aprobado correctamente', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@bp.route('/usuarios/<int:id>/rechazar', methods=['POST'])
@login_required
def rechazar_usuario(id):
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para realizar esta acción', 'danger')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    
    flash('Usuario rechazado y eliminado correctamente', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@bp.route('/usuarios/<int:id>/hacer_admin', methods=['POST'])
@login_required
def hacer_admin(id):
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para realizar esta acción', 'danger')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    usuario.rol = 'admin'
    db.session.commit()
    
    flash(f'Usuario {usuario.email} ahora es administrador', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@bp.route('/usuarios/<int:id>/quitar_admin', methods=['POST'])
@login_required
def quitar_admin(id):
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para realizar esta acción', 'danger')
        return redirect(url_for('main.index'))
    
    # No permitir quitar admin al propio usuario
    if id == current_user.id:
        flash('No puede quitarse a sí mismo los permisos de administrador', 'danger')
        return redirect(url_for('admin.listar_usuarios'))
    
    usuario = Usuario.query.get_or_404(id)
    usuario.rol = 'usuario'
    db.session.commit()
    
    flash(f'Usuario {usuario.email} ya no es administrador', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@bp.route('/usuarios/<int:id>/resetear_password', methods=['POST'])
@login_required
def resetear_password(id):
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para realizar esta acción', 'danger')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    # Resetear a una contraseña temporal
    nueva_password = 'temporal123'
    usuario.password_hash = generate_password_hash(nueva_password)
    db.session.commit()
    
    flash(f'Contraseña de {usuario.email} reseteada a: {nueva_password}', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@bp.route('/comisiones')
@login_required
def listar_comisiones():
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('main.index'))
    
    comisiones = Comision.query.order_by(Comision.fecha_creacion.desc()).all()
    return render_template('admin/comisiones.html', 
                          title='Gestión de Comisiones',
                          comisiones=comisiones)

@bp.route('/temas')
@login_required
def listar_temas():
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('main.index'))
    
    # Obtener temas pendientes de aprobación
    temas_pendientes = Tema.query.filter_by(estado='pendiente_aprobacion').order_by(Tema.fecha_creacion.desc()).all()
    
    # Obtener todos los temas
    temas = Tema.query.order_by(Tema.fecha_creacion.desc()).all()
    
    return render_template('admin/temas.html', 
                          title='Gestión de Temas',
                          temas_pendientes=temas_pendientes,
                          temas=temas)

@bp.route('/membresias')
@login_required
def listar_membresias():
    # Verificar que el usuario es administrador
    if current_user.rol != 'admin':
        flash('No tiene permisos para acceder a esta sección', 'danger')
        return redirect(url_for('main.index'))
    
    # Obtener solicitudes pendientes
    membresias_pendientes = db.session.query(MembresiaComision, Usuario, Comision).join(
        Usuario, MembresiaComision.usuario_id == Usuario.id
    ).join(
        Comision, MembresiaComision.comision_id == Comision.id
    ).filter(
        MembresiaComision.estado == 'pendiente_aprobacion'
    ).all()
    
    return render_template('admin/membresias.html', 
                          title='Gestión de Membresías',
                          membresias_pendientes=membresias_pendientes)

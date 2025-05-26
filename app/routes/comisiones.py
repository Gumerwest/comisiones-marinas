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

from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title='Página no encontrada'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html', title='Error interno'), 500

@bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html', title='Acceso denegado'), 403

from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import current_user
from app.models import Comision, Tema, MembresiaComision
from app import db

bp = Blueprint('main', __name__)

@bp.route('/health')
def health():
    """Health check endpoint para Render"""
    return jsonify({"status": "ok", "message": "Application is running"})

@bp.route('/')
def index():
    # Mostrar página principal con listado de comisiones activas
    comisiones = Comision.query.filter_by(activa=True).all()
    
    # Calcular estadísticas totales
    total_comisiones = len(comisiones)
    total_miembros = 0
    total_temas = 0
    
    # Crear diccionario de estadísticas por comisión
    comision_stats = {}
    
    for comision in comisiones:
        # Contar miembros aprobados
        miembros_count = MembresiaComision.query.filter_by(
            comision_id=comision.id,
            estado='aprobado'
        ).count()
        
        # Contar temas aprobados
        temas_count = Tema.query.filter_by(
            comision_id=comision.id,
            estado='aprobado'
        ).count()
        
        comision_stats[comision.id] = {
            'miembros': miembros_count,
            'temas': temas_count
        }
        
        total_miembros += miembros_count
        total_temas += temas_count
    
    # Obtener temas destacados (los más votados)
    temas_destacados = []
    if current_user.is_authenticated:
        # Solo mostrar temas de comisiones donde el usuario es miembro
        temas_destacados = Tema.query.filter_by(estado='aprobado').limit(5).all()
    
    return render_template('main/index.html', 
                          title='Comisiones de Trabajo Marinas de España',
                          comisiones=comisiones,
                          comision_stats=comision_stats,
                          total_comisiones=total_comisiones,
                          total_miembros=total_miembros,
                          total_temas=total_temas,
                          temas_destacados=temas_destacados)

@bp.route('/acerca')
def acerca():
    return render_template('main/acerca.html', title='Acerca de la Plataforma')

@bp.route('/contacto')
def contacto():
    return render_template('main/contacto.html', title='Contacto')

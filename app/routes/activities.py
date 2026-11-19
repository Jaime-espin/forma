from flask import Blueprint, render_template
from app.database.database import obtener_actividades

# 1. Definimos el Blueprint
# 'activities': nombre interno del blueprint
# __name__: para ubicar el módulo
activities_bp = Blueprint('activities', __name__)

# 2. Asignamos rutas con @activities_bp.route
@activities_bp.route('/')
def index():
    return "¡Hola desde FORMA!"

@activities_bp.route('/activities')
def ver_actividades():
    # Esta función se ejecutará CADA VEZ que alguien visite /activities
    actividades = obtener_actividades()
    return render_template('activities.html', actividades=actividades)
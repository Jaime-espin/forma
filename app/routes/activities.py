from flask import Blueprint, render_template
from app.database.database import obtener_actividades, obtener_actividad_por_id, obtener_streams_actividad
from app.ingesta.stream_importer import importar_stream_actividad
from app.database.database import obtener_actividades_cronologicas
from app.models.training_load import calcular_curvas_entrenamiento

# 1. Definimos el Blueprint
# 'activities': nombre interno del blueprint
# __name__: para ubicar el módulo
activities_bp = Blueprint('activities', __name__)

# 2. Asignamos rutas con @activities_bp.route
@activities_bp.route('/')
def index():
    actividades = obtener_actividades_cronologicas()
    curvas = calcular_curvas_entrenamiento(actividades)

    metrics = curvas[-1] if curvas else {'ctl': 0, 'atl': 0, 'tsb': 0, 'tss': 0, 'date': '-'}

    return render_template('dashboard.html', metrics=metrics, chart_data=curvas, lthr=175)

@activities_bp.route('/activities')
def ver_actividades():
    # Esta función se ejecutará CADA VEZ que alguien visite /activities
    actividades = obtener_actividades()
    return render_template('activities.html', actividades=actividades)

#Usuario hace clic en /activities/20995501852
#                       │
#                       ▼
#Flask ejecuta detalle_actividad(id=20995501852)
#                       │
#  1. ¿Existen ya streams en la tabla `streams` para este activity_id?
#         │
#         ├── NO ──→ ¿Tiene `stream_filename`? (.fit.gz)
#         │               │
#         │               └── Sí ──→ Llamamos a importar_stream_actividad()
#         │                          (Descomprime el FIT, extrae puntos y los guarda en SQLite)
#         │
#         └── SÍ ──→ Ya están cacheados en SQLite, ¡consulta instantánea!
#                       │
#  2. Traer los puntos de pulso, altitud y velocidad de la tabla `streams`.
#                       │
#  3. Renderizar template `templates/activity_detail.html` con las métricas y la gráfica.

@activities_bp.route('/activities/<int:activity_id>')
def detalle_actividad(activity_id):
    actividad = obtener_actividad_por_id(activity_id)
    streams = None
    if not actividad:
        return "Actividad no encontrada", 404
    else:
        streams = obtener_streams_actividad(activity_id)
        stream_file = actividad.get('stream_filename')
        if not streams and stream_file:
            # Solo intentamos con FIT por ahora
            if stream_file.endswith('.fit') or stream_file.endswith('.fit.gz'):
                try:
                    importar_stream_actividad(activity_id, stream_file)
                    streams = obtener_streams_actividad(activity_id)
                except Exception as e:
                    print(f"Error al importar stream {stream_file}: {e}")

    # Preparar datos para la gráfica (con submuestreo para que vuele)
    chart_labels = []
    chart_hr = []
    chart_alt = []

    if streams:
        # Si hay más de 600 puntos, tomamos un salto (step) para quedarnos con ~500 puntos
        paso = max(1, len(streams) // 500)
        puntos_muestreados = streams[::paso]

        for i, p in enumerate(puntos_muestreados):
            # i * paso representa los segundos transcurridos
            segundos = i * paso
            minutos = segundos // 60
            seg_restantes = segundos % 60
            chart_labels.append(f"{minutos}:{seg_restantes:02d}")
            chart_hr.append(p.get('heart_rate'))
            chart_alt.append(round(p['altitude'], 1) if p.get('altitude') is not None else None)

    return render_template(
        'activity_detail.html',
        actividad=actividad,
        streams=streams,
        chart_labels=chart_labels,
        chart_hr=chart_hr,
        chart_alt=chart_alt
    )


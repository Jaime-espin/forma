import os, gzip, fitparse, shutil, glob
from datetime import datetime
from app.ingesta.stream_importer import extraer_puntos_fit
from app.models.training_load import calcular_tss_actividad
from app.database.database import insertar_actividades, insertar_streams
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ACTIVIDAD = {
    'ID de actividad': 'id',
    'Fecha de la actividad': 'start_date', 
    'Nombre de la actividad': 'name',
    'Tipo de actividad': 'activity_type', 
    'Descripción de la actividad': 'description',
    'Tiempo transcurrido': 'elapsed_time', 
    'Distancia': 'total_distance', 
    'Frecuencia cardiaca máxima': 'max_heart_rate', 
    'Esfuerzo Relativo': 'relative_effort',  
    'Nombre del archivo': 'stream_filename',  
    'Tiempo en movimiento': 'moving_time', 
    'Velocidad máxima': 'max_speed', 
    'Velocidad promedio': 'avg_speed', 
    'Desnivel positivo': 'elevation_gain', 
    'Frecuencia cardiaca máxima': 'max_heart_rate', 
    'Frecuencia cardiaca promedio': 'avg_heart_rate', 
    'Calorías': 'calories', 
}

"""{'sport': 'cycling', 'sub_sport': 'road', 'start_time': datetime.datetime(2026, 11, 20, 12, 42, 30), 
'timestamp': datetime.datetime(2026, 11, 20, 14, 3, 38), 'total_elapsed_time': 4868.01, 
'total_timer_time': 4633.92, 'total_distance': 31163.86, 'total_calories': 609, 'max_heart_rate': 163, 
'min_heart_rate': 105, 'avg_heart_rate': 137, 'avg_temperature': 23, 'total_moving_time': 4633.92, 
'total_ascent': 319, 'total_descent': 312, 'max_cadence': 0, 'avg_cadence': 0, 'enhanced_max_speed': 13.042, 
'max_speed': 13.042, 'enhanced_avg_speed': 6.725, 'avg_speed': 6.725, 'max_power': 0, 'avg_power': 0, 
'total_work': 0, 'normalized_power': 0}"""

def deducir_tipo_deporte(sport, sub_sport):
    sub_sport = (sub_sport or '').lower()
    
    if sport == 'running':
        if 'offroad' in sub_sport:
            return 'Trail Running'
        return 'Carrera'
    
    if sport == 'cycling':
        if 'gravel' in sub_sport:
            return 'Gravel'
        elif 'mtb' in sub_sport:
            return 'MTB'
        return 'Ciclismo'
    
    return sport

def parsear_fit(ruta_archivo):
    fitfile = fitparse.FitFile(ruta_archivo)
    session_vals = {}
    for msg in fitfile.get_messages('session'):
        session_vals = msg.get_values()
        break
    start_time = session_vals.get('start_time') or datetime.now()
    activity_id = int(start_time.timestamp())
    start_date_iso = start_time.isoformat()

    sport = session_vals.get('sport')
    sub_sport = session_vals.get('sub_sport')
    nombre_archivo = os.path.basename(ruta_archivo)
    nombre_sin_extension = os.path.splitext(nombre_archivo)[0]

    actividad = {
        'id': activity_id,
        'name': nombre_sin_extension,
        'activity_type': deducir_tipo_deporte(session_vals.get('sport'),session_vals.get('sub_sport')),
        'start_date': start_date_iso,
        'elapsed_time': session_vals.get('total_elapsed_time'),
        'moving_time': session_vals.get('total_timer_time'),
        'distance': (session_vals.get('total_distance')),
        'elevation_gain': (session_vals.get('total_ascent')),
        'avg_speed': (session_vals.get('enhanced_avg_speed') or session_vals.get('avg_speed')),
        'max_speed': (session_vals.get('enhanced_max_speed') or session_vals.get('max_speed')),
        'avg_heart_rate': (session_vals.get('avg_heart_rate')),
        'max_heart_rate': (session_vals.get('max_heart_rate')),
        'calories': (session_vals.get('total_calories')),
        'relative_effort': None,
        'stream_filename': nombre_archivo,
        'description': None,
    }

    tss = calcular_tss_actividad(actividad)
    actividad['tss'] = tss

    with open(ruta_archivo, 'rb') as f:
        contenido_fit = f.read()
    puntos = extraer_puntos_fit(contenido_fit, activity_id)
    return actividad, puntos

def sincronizar_incoming():
    incoming_dir = os.path.join(BASE_DIR, 'data/incoming')
    destino = os.path.join(BASE_DIR, 'data/incoming/procesados')
    contador = 0
    fit = glob.glob(os.path.join(incoming_dir, '*.fit'))
    if not fit:
        return None
    for f in fit:
        actividad, puntos = parsear_fit(f)
        insertar_actividades([actividad], source='incoming', filename=actividad['stream_filename'])
        insertar_streams(puntos)
        shutil.move(f, destino)
        contador += 1
    print("Actividades importadas:", contador)

if __name__ == '__main__':
    #print(parsear_fit('/home/jaime/Escritorio/01Proyecto/forma/data/incoming/Bicicleta_por_la_tarde.fit'))
    sincronizar_incoming()
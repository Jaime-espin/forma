import zipfile
import io
import csv
from app.database.database import insertar_actividades
import os
from app.ingesta.utils import encontrar_zip
ZIP_PATH = encontrar_zip()

COLUMNAS_MAP = {
    'ID de actividad': 'id',
    'Fecha de la actividad': 'start_date', 
    'Nombre de la actividad': 'name',
    'Tipo de actividad': 'activity_type', 
    'Descripción de la actividad': 'description',
    'Tiempo transcurrido': 'elapsed_time', 
    'Distancia': 'distance', 
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

MESES = {
    'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
    'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
    'sept': '09', 'oct': '10', 'nov': '11', 'dic': '12'
}

def parsear_fecha(fecha_str):
    dia, mes, ano, hora = fecha_str.replace(',', '').split()
    mes_num = MESES[mes.lower()]
    return f'{ano}-{mes_num}-{dia.zfill(2)}T{hora.zfill(8)}'

def limpiar_float(valor):
    if valor is None or not valor.strip():
        return None
    return float(valor.strip().replace(',', '.'))

def limpiar_int(valor):
    if valor is None or not valor.strip():
        return None
    return int(float(valor.strip().replace(',', '.')))

def transformar_fila(fila):
    return {
        'id': limpiar_int(fila.get('ID de actividad')),
        'name': fila.get('Nombre de la actividad'),
        'activity_type': fila.get('Tipo de actividad'),
        'start_date': parsear_fecha(fila['Fecha de la actividad']),
        'elapsed_time': limpiar_int(fila.get('Tiempo transcurrido')),
        'moving_time': limpiar_int(fila.get('Tiempo en movimiento')),
        'distance': limpiar_float(fila.get('Distancia')),
        'elevation_gain': limpiar_float(fila.get('Desnivel positivo')),
        'avg_speed': limpiar_float(fila.get('Velocidad promedio')),
        'max_speed': limpiar_float(fila.get('Velocidad máxima')),
        'avg_heart_rate': limpiar_float(fila.get('Frecuencia cardiaca promedio')),
        'max_heart_rate': limpiar_float(fila.get('Frecuencia cardiaca máxima')),
        'calories': limpiar_float(fila.get('Calorías')),
        'relative_effort': limpiar_float(fila.get('Esfuerzo Relativo')),
        'stream_filename': fila.get('Nombre del archivo'),
        'description': fila.get('Descripción de la actividad'),
    }

def leer_zip():
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        # Ver qué archivos contiene
        #print(z.namelist())
        actividades = []
        contador_actividades = 0
        # Abrir un archivo específico dentro del zip directamente en memoria
        with z.open('activities.csv') as f:
            # aquí f se comporta casi como un archivo normal
            texto_f = io.TextIOWrapper(f, encoding='utf-8')
            lector = csv.DictReader(texto_f)
            for fila in lector:
                actividad_limpia = transformar_fila(fila)
                actividades.append(actividad_limpia)
                contador_actividades+=1
    insertar_actividades(actividades, filename=os.path.basename(ZIP_PATH))
    print("actividades procesadas: ", contador_actividades)
                

def get_columnas():
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        with z.open('activities.csv') as f:
            texto_f = io.TextIOWrapper(f, encoding='utf-8')
            lector = csv.DictReader(texto_f)
            print(lector.fieldnames)


if __name__ == '__main__':
    leer_zip()
        
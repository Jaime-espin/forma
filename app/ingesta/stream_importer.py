import zipfile
import gzip
import os
import fitparse
from app.database.database import insertar_streams
from app.ingesta.utils import encontrar_zip
ZIP_PATH = encontrar_zip()

def leer_actividad():
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        #print(z.namelist())
        
        contenido_gz = z.read('activities/22163215648.fit.gz')
        contenido_fit = gzip.decompress(contenido_gz)
        
        fitfile = fitparse.FitFile(contenido_fit)

        contador = 0
        for record in fitfile.get_messages('record'):
            # Cada record tiene valores:
            datos = record.get_values()
            if 'heart_rate' in datos:
                print(datos)
                contador += 1
                if contador >= 3:
                    break

        puntos = []
        puntos = extraer_puntos_fit(contenido_fit, 22163215648)
        print(len(puntos))
        insertar_streams(puntos)
        print("Streams insertados en la base de datos.")

def extraer_puntos_fit(contenido_fit, activity_id):
    fitfile = fitparse.FitFile(contenido_fit)
    puntos = []
    for record in fitfile.get_messages('record'):
        # Cada record tiene valores:
        datos = record.get_values()
        ts = datos.get('timestamp')
        if not ts:
            continue  # Si un punto no tiene fecha/hora, no nos sirve
        ts_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)

        hr = datos.get('heart_rate')
        vel = datos.get('enhanced_speed') or datos.get('speed')

        lat = datos.get('position_lat')
        lon = datos.get('position_long')
        if lat is not None and lon is not None:
            lat = round(lat * (180 / (2**31)), 7)
            lon = round(lon * (180 / (2**31)), 7)

        alt = datos.get('enhanced_altitude') or datos.get('altitude')
        cad = datos.get('cadence')
        power = datos.get('power')

        punto = (activity_id, ts_str, hr, vel, lat, lon, alt, cad, power)
        puntos.append(punto)
    return puntos

def importar_stream_actividad(activity_id, stream_filename):
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
            #print(z.namelist())
            
            contenido_gz = z.read(stream_filename)
            contenido_fit = gzip.decompress(contenido_gz)

            puntos = []
            puntos = extraer_puntos_fit(contenido_fit, activity_id)
            insertar_streams(puntos)



if __name__ == '__main__':
    leer_actividad()
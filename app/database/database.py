import sqlite3
import os
from datetime import datetime
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data', 'database.db')

def crear_tablas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla de activities
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            elapsed_time INTEGER NOT NULL,
            moving_time INTEGER NOT NULL,
            distance REAL,
            elevation_gain REAL,
            avg_speed REAL,
            max_speed REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            calories REAL,
            relative_effort REAL,
            stream_filename TEXT,
            description TEXT,
            imported_at TEXT NOT NULL,
            UNIQUE(id)
        )
    ''')

    # Crear tabla de sesiones de streams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            heart_rate INTEGER,
            velocity REAL,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            cadence INTEGER,
            power INTEGER,
            FOREIGN KEY (activity_id) REFERENCES activities(id)
        )
    ''')

    # Crear tabla de imports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imported_at TEXT NOT NULL,
            source TEXT NOT NULL,
            filename TEXT NOT NULL,
            activities_added INTEGER NOT NULL,
            activities_skipped INTEGER NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        )
    ''')

    conn.commit()
    conn.close()

def insertar_actividades(actividades,  source='zip', filename=''):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    imported_at = datetime.now().isoformat(timespec='seconds')
    for actividad in actividades:
        cursor.execute('''
            INSERT OR IGNORE INTO activities (
                id, name, activity_type, start_date, elapsed_time, moving_time,
                distance, elevation_gain, avg_speed, max_speed, avg_heart_rate,
                max_heart_rate, calories, relative_effort, stream_filename,
                description, imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            actividad.get('id'), actividad.get('name'), actividad.get('activity_type'),
            actividad.get('start_date'), actividad.get('elapsed_time'), actividad.get('moving_time'),
            actividad.get('distance'), actividad.get('elevation_gain'), actividad.get('avg_speed'),
            actividad.get('max_speed'), actividad.get('avg_heart_rate'), actividad.get('max_heart_rate'),
            actividad.get('calories'), actividad.get('relative_effort'), actividad.get('stream_filename'),
            actividad.get('description'), imported_at
        ))

    cambios = conn.total_changes
    cursor.execute('''
        INSERT INTO imports (
            imported_at, source, filename, activities_added,
            activities_skipped, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        imported_at, source, filename, cambios, len(actividades)-cambios, 'success', None
    ))
    conn.commit()
    conn.close()


def insertar_streams(streams_puntos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO streams (
            activity_id, timestamp, heart_rate, velocity,
            latitude, longitude, altitude, cadence, power
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', streams_puntos)
    
    conn.commit()
    conn.close()

def obtener_actividades(limite=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM activities
        ORDER BY start_date DESC
        LIMIT ?
    ''', (limite,))
    actividades = [dict(fila) for fila in cursor.fetchall()]

    conn.close()
    return actividades

def obtener_actividad_por_id(activity_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activities WHERE id = ?', (activity_id,))
    activity = cursor.fetchone()
    conn.close()

    if activity is None:
        return None
    return dict(activity)

def obtener_streams_actividad(activity_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM streams WHERE activity_id = ? ORDER BY timestamp ASC', (activity_id,))
    stream = cursor.fetchall()
    conn.close()

    return [dict(f) for f in stream]

def obtener_actividades_cronologicas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activities ORDER BY start_date ASC')
    actividades = [dict(fila) for fila in cursor.fetchall()]
    conn.close()
    return actividades
    

if __name__ == '__main__':
    crear_tablas()
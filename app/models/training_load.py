import math
from datetime import datetime, timedelta

def calcular_tss_actividad(actividad, lthr = 175):
    """
    Calcula el hrTSS (Heart Rate Training Stress Score) de una actividad.
    
    Fórmula: (tiempo_segundos * (FC_media / LTHR)^2 * 100) / 3600
    - LTHR: Lactate Threshold Heart Rate (pulso en umbral de lactato, ~175 bpm).
    - Una sesión de 1h exactamente a ritmo de umbral equivale a 100 TSS.
    - Si no hay datos de pulso o tiempo, se asigna 0.0 TSS.
    """

    avg_heart_rate = actividad.get('avg_heart_rate')
    if not avg_heart_rate:
        return 0.0
    moving_time = actividad.get('moving_time')
    if not moving_time:
        return 0.0
    
    return round((moving_time * math.pow(avg_heart_rate / lthr, 2)*100)/3600,1)

def calcular_curvas_entrenamiento(actividades, lthr=175):
    """
    Modela las curvas de Banister / Coggan (CTL, ATL, TSB) día a día.
    
    Conceptos clave:
    - CTL (Chronic Training Load / Fitness): media exponencial de ~42 días.
    - ATL (Acute Training Load / Fatiga): media exponencial de ~7 días.
    - TSB (Training Stress Balance / Forma): CTL - ATL.
      * TSB > 0: Estado descansado / frescura (ideal para competir: +5 a +20).
      * TSB < 0: Estado de fatiga / acumulación de carga.
    """

    if not actividades:
        return []

    # 1. Agrupar TSS por fecha (un día puede tener 0, 1 o varias actividades)
    tss_por_dia = {}
    

    for actividad in actividades:
        tss = calcular_tss_actividad(actividad, lthr)
        fecha = actividad.get('start_date')[:10] # 'YYYY-MM-DD'
        tss_por_dia[fecha] = tss_por_dia.get(fecha, 0.0) + tss

    # 2. Definir el rango continuo desde el primer hasta el último día
    dia_actual = datetime.strptime(actividades[0]['start_date'][:10], '%Y-%m-%d').date()
    dia_fin = datetime.strptime(actividades[-1]['start_date'][:10], '%Y-%m-%d').date()

    # 3. Constantes de decaimiento diario (EMA):
    # decay = e^(-1 / constante_dias)
    decay_ctl = math.exp(-1.0 / 42.0) # ~0.976 (el fitness decae despacio)

    decay_atl = math.exp(-1.0 / 7.0) # ~0.867 (la fatiga decae rápido)
    ctl = 0.0
    atl = 0.0
    curvas = []


    # 4. Iterar día a día para que los días de descanso (TSS=0) decaigan la carga
    while dia_actual <= dia_fin:
        dia_str = dia_actual.strftime('%Y-%m-%d')
        tss_hoy = tss_por_dia.get(dia_str, 0.0)
        ctl = ctl*decay_ctl + tss_hoy * (1.0 - decay_ctl)
        atl = atl * decay_atl + tss_hoy * (1.0 - decay_atl)

        tsb = ctl - atl

        curvas.append({
            'date': dia_str, 
            'tss': round(tss_hoy, 1), 
            'ctl': round(ctl, 1), 
            'atl': round(atl, 1), 
            'tsb': round(tsb, 1)
        })
        dia_actual += timedelta(days=1)

    return curvas
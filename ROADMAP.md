# FORMA — Roadmap

> Personal training-data lab. Pulls activity history from Strava, applies fitness and fatigue models to your own data, and grows toward an AI coach. Data layer first.

---

## Stack

| Pieza | Decisión |
|---|---|
| Lenguaje | Python |
| Framework web | Flask |
| Base de datos | SQLite + SQL directo |
| Frontend | Simple y funcional — generado con asistencia de IA, sin protagonismo |
| Ingesta de datos | Export ZIP de Strava (principal) · API de Strava (futuro, requiere suscripción) |

---

## MVP — Dashboard de actividad

La versión mínima: una web que importe el historial de Strava, aplique modelos de carga de entrenamiento y los visualice en un dashboard personal.

### Ingesta de datos
- [x] Leer el export ZIP de Strava directamente en memoria (`zipfile`)
- [x] Parsear `activities.csv` y normalizar datos (fechas ISO 8601, tipos, nulos)
- [x] Importar 714 actividades a SQLite con `INSERT OR IGNORE` (idempotente)
- [x] Log de auditoría automático en tabla `imports`
- [x] Leer archivos `.fit.gz` en memoria (`gzip` + `fitparse`)
- [x] Extraer streams (pulso, GPS, velocidad, altitud) y convertir coordenadas a grados decimales
- [x] Insertar streams en SQLite con `executemany`
- [x] Detección automática del ZIP más reciente en `data/` (`utils.py`)
- [x] Importación de streams bajo demanda (al abrir detalle de actividad)
- [x] Manejo robusto de errores en FIT corruptos o con campos propietarios (`FitParseError`)

### Base de datos
- [x] Esquema: `activities`, `streams`, `imports`
- [ ] Índice en `streams.activity_id` para acelerar consultas de detalle

### Algoritmos de entrenamiento (Fase 2)
- [x] Estudiar el modelo de Banister (TSS, ATL, CTL, TSB) e investigación científica (`RESEARCH.md`)
- [x] Calcular Training Stress Score (TSS) por actividad a partir de FC y esfuerzo relativo
- [x] Implementar curva de fitness (CTL — Chronic Training Load, 42 días)
- [x] Implementar curva de fatiga (ATL — Acute Training Load, 7 días)
- [x] Calcular forma física (TSB = CTL - ATL)

### Interfaz web (Flask)
- [x] Configurar Flask con Application Factory y Blueprints
- [x] Lista de actividades con métricas clave (distancia, tiempo, desnivel, FC, tipo refinado)
- [x] Detalle de actividad: métricas + gráfica de pulso y altitud con Chart.js (carga bajo demanda del stream)
- [ ] Dashboard principal: resumen semanal, volumen por deporte, tendencias
- [x] Visualización de curvas CTL/ATL/TSB en el tiempo (Fase 2) con gráfica interactiva PMC y guía de zonas

---

## Backlog — Features futuras (post-MVP)

### Métricas avanzadas de carga (post-MVP)
- [ ] ACWR (Acute:Chronic Workload Ratio) para estimar picos de carga y riesgo de lesión
- [ ] Soporte para hrTSS zonal por tiempo en zonas o rTSS basado en ritmo

### Heatmap personal
- [ ] Acumular puntos GPS de todos los streams en una cuadrícula de coordenadas
- [ ] Renderizar el heatmap sobre OpenStreetMap (librería Folium o Leaflet.js)
- [ ] Filtrar heatmap por disciplina (carrera, bicicleta, trail...)

### IA — Recomendación diaria
- [ ] Basada en TSB/CTL/ATL actuales, sugerir si descansar, rodar suave o entrenar fuerte
- [ ] Similar al "Training Readiness" de Garmin, pero con tus propios datos y tu propia lógica

### IA — Asistente/entrenador
- [ ] Chat con LLM que lee tu historial y métricas y responde como un entrenador
- [ ] Planificación de semanas de entrenamiento basada en objetivos

### Integración con API de Strava
- [ ] OAuth 2.0 para usuarios con suscripción premium
- [ ] Sync incremental: solo actividades nuevas desde la última sincronización

---

## Decisiones técnicas

| Decisión | Alternativa | Razonamiento |
|---|---|---|
| Flask | FastAPI | Ya conocido; el problema interesante son los datos, no el framework |
| SQLite primero | PostgreSQL | Cero fricción de setup; migración futura enseña algo valioso |
| SQL directo | SQLAlchemy | Ya domina SQL; menos magia, más control |
| Export ZIP como fuente principal | API de Strava | La API requiere suscripción de pago; el ZIP es gratuito y completo |
| Streams bajo demanda | Importación masiva previa | Evita procesar 2M+ puntos de golpe; los datos se cachean en BD al primer acceso |
| Frontend generado con IA | Frontend artesanal | El proyecto muestra valor en datos y algoritmos, no en diseño UI |

---

## Recursos

- [Strava — Descargar tus datos](https://www.strava.com/athlete/delete_your_account)
- [Formato FIT — Especificación Garmin](https://developer.garmin.com/fit/protocol/)
- [fitparse — Librería Python para FIT](https://github.com/dtcooper/python-fitparse)
- [Modelo de Banister — Training Load](https://www.trainingpeaks.com/learn/articles/the-science-of-the-performance-manager/)
- [Folium — Mapas interactivos en Python](https://python-visualization.github.io/folium/)
- [Strava API Docs](https://developers.strava.com/docs/) *(para fase futura)*
- [Formato GPX](https://www.topografix.com/gpx.asp)
- [Librería fitparse (FIT)](https://github.com/dtcooper/python-fitparse)

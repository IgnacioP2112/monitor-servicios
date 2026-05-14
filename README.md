# Monitor de Servicios Web
# Ignacio Pérez


Sistema de monitoreo de disponibilidad de servicios web construido en Python. Consulta sitios periódicamente, mide tiempos de respuesta, detecta caídas y expone los datos a través de una API REST con dashboard en tiempo real.

Inspirado conceptualmente en herramientas como UptimeRobot o Datadog, pero construido desde cero con foco en entender cada capa del sistema.

---

## ¿Qué hace?

- Consulta múltiples sitios web de forma concurrente usando `ThreadPoolExecutor`
- Mide el tiempo de respuesta de cada sitio
- Detecta errores de conexión y timeouts
- Registra todos los resultados en logs estructurados
- Genera alertas `SERVICE DOWN` cuando un sitio falla consecutivamente
- Expone los datos a través de una **API REST con FastAPI**
- Muestra un **dashboard en tiempo real** con gráficos de latencia

---

## Arquitectura

```
checker.py       →  realiza las requests HTTP y mide latencia
monitor.py       →  orquesta el monitoreo concurrente y detecta caídas
logger.py        →  registra resultados en consola y archivo de log
analizar_logs.py →  analiza el log con pandas y genera gráficos
api.py           →  expone los datos como endpoints REST (FastAPI)
static/index.html → dashboard que consume la API con fetch()
```

Cada módulo tiene una responsabilidad única. Cambiar la lógica de chequeo no afecta el logging. Cambiar el dashboard no afecta la API.

---

## Stack

- **Python 3.11**
- **requests** — HTTP requests
- **concurrent.futures** — monitoreo concurrente con ThreadPoolExecutor
- **FastAPI + uvicorn** — API REST
- **pandas** — análisis de logs
- **matplotlib** — gráficos de latencia
- **python-dotenv** — configuración por variables de entorno
- **pytest** — tests unitarios

---

## Estructura del proyecto

```
monitor-servicios/
├── tests/
│   └── test_checker.py
├── static/
│   └── index.html
├── logs/
│   └── monitor.log
├── .env.example
├── .gitignore
├── conftest.py
├── config.py
├── checker.py
├── logger.py
├── monitor.py
├── analizar_logs.py
├── api.py
└── requirements.txt
```

---

## Instalación

```bash
git clone https://github.com/tu-usuario/monitor-servicios.git
cd monitor-servicios

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

Crea tu archivo `.env` basado en el ejemplo:

```bash
cp .env.example .env
```

Edita `.env` con los sitios que quieres monitorear:

```
URLS=https://google.com,https://github.com,https://tusitio.com
CHECK_INTERVAL=30
TIMEOUT=10
MAX_FAILURES=3
```

---

## Uso

El sistema tiene dos procesos que corren en paralelo.

**Terminal 1 — Monitor:**
```bash
python monitor.py
```

**Terminal 2 — API y dashboard:**
```bash
uvicorn api:app --reload
```

Abre el dashboard en: [http://localhost:8000](http://localhost:8000)

---

## Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Dashboard web |
| GET | `/status` | Estado actual de cada sitio |
| GET | `/latencia` | Historial completo de latencias |
| GET | `/stats` | Estadísticas por sitio (promedio, min, max) |
| GET | `/alertas` | Eventos SERVICE DOWN registrados |

La documentación interactiva de la API está disponible en [http://localhost:8000/docs](http://localhost:8000/docs) (generada automáticamente por FastAPI).

---

## Análisis de logs

Para generar un gráfico de latencia a partir del historial:

```bash
python analizar_logs.py
```

Genera el archivo `logs/latencia_report.png` con:
- Latencia por sitio a lo largo del tiempo
- Latencia promedio comparativa por sitio

---

## Tests

```bash
pytest tests/ -v
```

```
tests/test_checker.py::test_retorna_campos_correctos  PASSED
tests/test_checker.py::test_sitio_ok                  PASSED
tests/test_checker.py::test_sitio_inexistente         PASSED
tests/test_checker.py::test_url_se_preserva           PASSED
```

---

## Decisiones técnicas

**¿Por qué `ThreadPoolExecutor`?**
Las requests HTTP con la librería `requests` son operaciones bloqueantes de I/O de red. `ThreadPoolExecutor` permite ejecutarlas en paralelo sin cambiar la librería ni reescribir el código con `async/await`. Si se quisiera escalar a cientos de sitios, migrar a `asyncio` con `httpx` sería el siguiente paso natural.

**¿Por qué FastAPI?**
FastAPI genera documentación interactiva automáticamente en `/docs`, incluye validación de datos con Pydantic, y tiene mejor rendimiento para APIs. Para una API de consulta simple con endpoints definidos, es la elección más directa hoy.

**¿Por qué logs en texto plano y no base de datos?**
Para mantener el proyecto simple y sin dependencias de infraestructura. El log estructurado con separador `|` permite parsearlo con pandas sin configuración adicional. Migrar a SQLite sería el siguiente paso.

---

## Próximos pasos

- [ ] Persistencia en SQLite en lugar de logs de texto
- [ ] Notificaciones por Telegram o email al detectar caídas
- [ ] Endpoint `POST /sitios` para agregar URLs sin tocar código
- [ ] Deploy en Railway o AWS EC2

---

## Autor

Ignacio Pérez (**Freebird**)
Estudiante de Ingeniería Civil Telemática — Universidad Técnica Federico Santa María
[LinkedIn](https://linkedin.com/in/ignaciopereznunez2112) · [GitHub](https://github.com/IgnacioP2112)

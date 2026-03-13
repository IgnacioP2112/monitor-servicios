

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware




#INICIALIZAR LA APP 
app = FastAPI(title="Monitor de Servicios Web")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)



#
# ── FUNCIÓN REUTILIZABLE: PARSEAR EL LOG ────────────────────────────────────
#
# Todos los endpoints necesitan leer el log.
# En lugar de repetir el código, lo ponemos en una función que todos llaman.

LOG_PATH = Path("logs/monitor.log")

def parsear_log():
    """
    Lee monitor.log y devuelve dos listas:
    - registros_ok:     líneas con estado OK (tienen latencia)
    - registros_error:  líneas con ERROR o SERVICE DOWN
    """
    registros_ok = []
    registros_error = []

    if not LOG_PATH.exists():
        return registros_ok, registros_error

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    for linea in lineas:
        partes = linea.strip().split(" | ")

        if len(partes) == 5 and partes[1] == "OK":
            registros_ok.append({
                "timestamp": partes[0],
                "url":       partes[2],
                "status":    int(partes[3]),
                "latencia":  float(partes[4].replace("s", ""))
            })

        elif len(partes) >= 3 and partes[1] == "ERROR":
            mensaje = partes[3] if len(partes) > 3 else "error desconocido"
            registros_error.append({
                "timestamp": partes[0],
                "url":       partes[2],
                "mensaje":   mensaje
            })

    return registros_ok, registros_error


# ── ENDPOINTS ────────────────────────────────────────────────────────────────
@app.get("/status")
def get_status():
    """
    Devuelve el último registro conocido de cada sitio.
    Procesa los registros en orden cronológico para que
    el último estado (OK o ERROR) sea el que prevalece.
    """
    registros_ok, registros_error = parsear_log()

    todos = {}

    # Primero procesamos todos los OK
    for r in registros_ok:
        todos[r["url"]] = {
            "url":      r["url"],
            "estado":   "OK",
            "status":   r["status"],
            "latencia": r["latencia"],
            "timestamp": r["timestamp"]
        }

    # Luego los ERROR — pero solo si la URL existe en config
    # y solo si el timestamp es más reciente que el último OK
    for r in registros_error:
        url = r["url"]

        # Ignorar URLs malformadas (que contengan "https" en el medio)
        if url.count("https://") > 1:
            continue

        if url not in todos:
            # Sitio que nunca tuvo OK, igual lo mostramos
            todos[url] = {
                "url":      url,
                "estado":   "ERROR",
                "status":   None,
                "latencia": None,
                "timestamp": r["timestamp"]
            }
        else:
            # Solo sobreescribir si el error es más reciente que el último OK
            if r["timestamp"] > todos[url]["timestamp"]:
                todos[url] = {
                    "url":      url,
                    "estado":   "ERROR",
                    "status":   None,
                    "latencia": None,
                    "timestamp": r["timestamp"]
                }

    return list(todos.values())


@app.get("/latencia")
def get_latencia():
    """
    Devuelve el historial completo de latencias.
    El dashboard usa esto para graficar la línea de tiempo.
    """
    registros_ok, _ = parsear_log()
    return registros_ok


@app.get("/alertas")
def get_alertas():
    """
    Devuelve solo los eventos SERVICE DOWN del log.
    """
    _, registros_error = parsear_log()

    alertas = [
        r for r in registros_error
        if "SERVICE DOWN" in r["mensaje"]
    ]

    return alertas


@app.get("/stats")
def get_stats():
    """
    Calcula estadísticas de latencia por sitio usando pandas.
    """
    registros_ok, _ = parsear_log()

    if not registros_ok:
        return []

    df = pd.DataFrame(registros_ok)

    stats = (
        df.groupby("url")["latencia"]
        .agg(
            mediciones="count",
            promedio="mean",
            minima="min",
            maxima="max"
        )
        .round(3)
        .reset_index()
    )

    return stats.to_dict(orient="records")

# ── SERVIR EL DASHBOARD ──────────────────────────────────────────────────────
#
# Le decimos a FastAPI que la carpeta /static contiene archivos públicos.
# Cuando alguien visite "/" le devolvemos index.html directamente.

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")
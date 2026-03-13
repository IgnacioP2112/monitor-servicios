
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path


LOG_PATH = Path("logs/monitor.log")

# Leemos todas las líneas del archivo
with open(LOG_PATH, "r", encoding="utf-8") as f:
    lineas = f.readlines()

print(f"Total de líneas en el log: {len(lineas)}")

registros = []

for linea in lineas:
    partes = linea.strip().split(" | ")
    
    # Las líneas OK tienen exactamente 5 partes
    if len(partes) == 5 and partes[1] == "OK":
        timestamp_str = partes[0]       # "2026-03-11 19:21:54"
        url           = partes[2]       # "https://google.com"
        status        = int(partes[3])  # 200
        latencia_str  = partes[4]       # "0.635s"
        
        # Quitamos la "s" del final y convertimos a float
        latencia = float(latencia_str.replace("s", ""))
        
        registros.append({
            "timestamp": pd.to_datetime(timestamp_str),
            "url":       url,
            "status":    status,
            "latencia":  latencia
        })

print(f"Registros OK parseados: {len(registros)}")

#CREACIÓN DE DATAFRAME

# Un DataFrame es una tabla. Cada fila es un registro, cada columna un campo.
df = pd.DataFrame(registros)
print("\n--- Vista previa del DataFrame ---")
print(df.head(10))
print(f"\nSitios únicos: {df['url'].unique()}")

#ESTADISTICAS POR SITIO

#groupby agrupa las filas por url y luego calculamos estadísticas de latencia

print("\n--- Estadísticas de latencia por sitio (en segundos) ---")
stats = df.groupby("url")["latencia"].agg(
    mediciones="count",
    promedio="mean",
    minima="min",
    maxima="max"
).round(3)

print(stats)

#GRAFICAR

# Creamos una figura con dos subplots:
#   - Arriba: latencia en el tiempo por sitio (línea)
#   - Abajo:  latencia promedio por sitio (barras)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle("Monitor de Servicios Web — Análisis de Latencia", fontsize=14)

# — Gráfico 1: Latencia en el tiempo —
for url, grupo in df.groupby("url"):
    ax1.plot(
        grupo["timestamp"],
        grupo["latencia"],
        marker="o",
        markersize=4,
        label=url,
        linewidth=1.5
    )

ax1.set_title("Latencia por sitio a lo largo del tiempo")
ax1.set_ylabel("Latencia (segundos)")
ax1.set_xlabel("Tiempo")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Formatear el eje X para que muestre hora:minuto
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate()

# — Gráfico 2: Latencia promedio por sitio (barras) —
promedios = df.groupby("url")["latencia"].mean().sort_values()

bars = ax2.bar(
    range(len(promedios)),
    promedios.values,
    color=["#4C72B0", "#DD8452", "#55A868"]
)

# Etiquetas encima de cada barra con el valor exacto
for bar, valor in zip(bars, promedios.values):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{valor:.3f}s",
        ha="center",
        va="bottom",
        fontsize=9
    )

ax2.set_title("Latencia promedio por sitio")
ax2.set_ylabel("Latencia promedio (segundos)")
ax2.set_xticks(range(len(promedios)))
ax2.set_xticklabels(
    [url.replace("https://", "") for url in promedios.index],
    rotation=15
)
ax2.grid(True, alpha=0.3, axis="y")

plt.tight_layout()

# Guardar el gráfico como imagen
output_path = Path("logs/latencia_report.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"\nGráfico guardado en: {output_path}")

plt.show()
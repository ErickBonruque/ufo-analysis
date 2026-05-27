"""Consulta clima histórico para coordenadas/datas dos avistamentos."""
from pathlib import Path
import requests
import pandas as pd
from tqdm import tqdm

ENDPOINT = "https://archive-api.open-meteo.com/v1/archive"
CACHE = Path("data/raw/clima_openmeteo.parquet")

def consulta_clima(lat: float, lon: float, dia: str) -> dict | None:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": dia,
        "end_date": dia,
        "hourly": "temperature_2m,cloudcover,visibility,windspeed_10m,weathercode",
        "timezone": "UTC",
    }
    try:
        r = requests.get(ENDPOINT, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

# IMPORTANTE: respeitar limites da API gratuita (~10k/dia).
# Recomendado: agrupar relatos por (cidade, dia) antes de consultar.

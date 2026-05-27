"""Gera dim_aeroporto: aeroporto mais próximo de cada localização única."""
from pathlib import Path
import numpy as np
import pandas as pd

TIPOS_RELEVANTES = {"large_airport", "medium_airport", "small_airport"}
BATCH = 500  # locais por vez para controlar memória

def haversine_matrix(lat1, lon1, lat2, lon2):
    """Retorna matriz de distâncias em km (shape: len(lat1) x len(lat2))."""
    R = 6371.0
    lat1, lon1 = np.radians(lat1)[:, None], np.radians(lon1)[:, None]
    lat2, lon2 = np.radians(lat2)[None, :], np.radians(lon2)[None, :]
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))

airports = pd.read_csv("data/raw/airports.csv", low_memory=False)
airports = airports[airports["type"].isin(TIPOS_RELEVANTES)].copy()
airports = airports.dropna(subset=["latitude_deg", "longitude_deg", "name"])
airports = airports.reset_index(drop=True)

ap_lat = airports["latitude_deg"].values.astype(float)
ap_lon = airports["longitude_deg"].values.astype(float)
ap_nome = airports["name"].values
ap_tipo = airports["type"].values

staging = pd.read_parquet("data/processed/ufo_staging.parquet",
                          columns=["cidade", "estado", "pais", "latitude", "longitude"])
locais = staging.dropna(subset=["latitude", "longitude"]).drop_duplicates(
    subset=["cidade", "estado", "pais"]
).reset_index(drop=True)

resultados = []
for i in range(0, len(locais), BATCH):
    bloco = locais.iloc[i : i + BATCH]
    lat = bloco["latitude"].values.astype(float)
    lon = bloco["longitude"].values.astype(float)
    dist = haversine_matrix(lat, lon, ap_lat, ap_lon)
    idx_min = np.argmin(dist, axis=1)
    for j, row in enumerate(bloco.itertuples()):
        resultados.append({
            "cidade":                  row.cidade,
            "estado":                  row.estado,
            "pais":                    row.pais,
            "aeroporto_mais_proximo":  ap_nome[idx_min[j]],
            "distancia_km":            round(float(dist[j, idx_min[j]]), 2),
            "tipo_aeroporto":          ap_tipo[idx_min[j]],
        })
    if (i // BATCH) % 10 == 0:
        print(f"  {i + len(bloco)}/{len(locais)} locais processados...")

df = pd.DataFrame(resultados)
df["sk_aeroporto"] = range(1, len(df) + 1)
df = df[["sk_aeroporto", "aeroporto_mais_proximo", "distancia_km", "tipo_aeroporto",
         "cidade", "estado", "pais"]]

Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_parquet("data/processed/dim_aeroporto.parquet", index=False)
print(f"dim_aeroporto: {len(df):,} linhas salvas.")

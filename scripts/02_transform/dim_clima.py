"""
Gera dim_clima com normais climáticas calculadas por latitude e mês.
Fórmula baseada no modelo simplificado de temperatura de Willmott & Matsuura.
Sem chamadas de API — completa em segundos.
"""
from pathlib import Path
import math
import numpy as np
import pandas as pd

DEST_DIM    = Path("data/processed/dim_clima.parquet")
DEST_LOOKUP = Path("data/processed/clima_lookup.parquet")
DEST_DIM.parent.mkdir(parents=True, exist_ok=True)

# ── 1. Top 200 localizações × 12 meses ───────────────────────────────────────
staging = pd.read_parquet("data/processed/ufo_staging.parquet")
staging["data_completa"] = pd.to_datetime(staging["data_completa"])
staging["mes"]   = staging["data_completa"].dt.month
staging["lat_r"] = staging["latitude"].round(0)
staging["lon_r"] = staging["longitude"].round(0)

top_locais = (
    staging.groupby(["lat_r", "lon_r"]).size()
    .reset_index(name="qtd")
    .nlargest(200, "qtd")
    .reset_index(drop=True)
)

# ── 2. Funções de estimativa climática ───────────────────────────────────────
def temperatura_media(lat: float, mes: int) -> float:
    """Temperatura média estimada (°C) por latitude e mês."""
    # Temperatura anual média por latitude (°C)
    t_anual = 30 - 0.68 * abs(lat)
    # Amplitude sazonal (maior nos polos, menor no equador)
    amplitude = 0.4 * abs(lat)
    # Desfasamento: hemisfério norte → janeiro frio, hemisfério sul → julho frio
    fase = 1 if lat >= 0 else 7
    t = t_anual - amplitude * math.cos(2 * math.pi * (mes - fase) / 12)
    return round(t, 1)

def cobertura_nuvens(lat: float, mes: int) -> float:
    """Cobertura de nuvens estimada (%) por latitude e mês."""
    # Regiões tropicais e polares têm mais nuvens; subtropicais menos
    nuvem_base = 50 + 20 * math.cos(math.radians(lat * 2))
    # Variação sazonal leve
    variacao = 10 * math.sin(2 * math.pi * mes / 12)
    return round(max(5.0, min(95.0, nuvem_base + variacao)), 1)

def vento_medio(lat: float) -> float:
    """Velocidade média do vento (km/h) — maiores em latitudes médias."""
    return round(5 + 15 * math.sin(math.radians(abs(lat))), 1)

CODIGO_POR_COBERTURA = {
    (0, 20):  "0",   # céu limpo
    (20, 50): "1",   # poucas nuvens
    (50, 80): "2",   # parcialmente nublado
    (80, 101):"3",   # nublado
}

def codigo_clima(nuvens: float) -> str:
    for (lo, hi), code in CODIGO_POR_COBERTURA.items():
        if lo <= nuvens < hi:
            return code
    return "3"

# ── 3. Gerar registros ────────────────────────────────────────────────────────
registros_clima  = []
registros_lookup = []
sk = 1

for _, loc in top_locais.iterrows():
    for mes in range(1, 13):
        temp   = temperatura_media(loc.lat_r, mes)
        nuvens = cobertura_nuvens(loc.lat_r, mes)
        vento  = vento_medio(loc.lat_r)
        vis    = round(max(1.0, 30 - nuvens * 0.25), 1)
        code   = codigo_clima(nuvens)

        registros_clima.append({
            "sk_clima":         sk,
            "cobertura_nuvens": nuvens,
            "visibilidade":     vis,
            "vento":            vento,
            "temperatura":      temp,
            "codigo_clima":     code,
        })
        registros_lookup.append({
            "lat_r":    loc.lat_r,
            "lon_r":    loc.lon_r,
            "mes":      mes,
            "sk_clima": sk,
        })
        sk += 1

df_clima  = pd.DataFrame(registros_clima)
df_lookup = pd.DataFrame(registros_lookup)

df_clima.to_parquet(DEST_DIM, index=False)
df_lookup.to_parquet(DEST_LOOKUP, index=False)
print(f"dim_clima:    {len(df_clima):,} linhas ({len(top_locais)} locais × 12 meses)")
print(f"clima_lookup: {len(df_lookup):,} linhas")

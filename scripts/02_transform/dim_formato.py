"""Gera dim_formato com normalização e agrupamento dos shapes."""
from pathlib import Path
import pandas as pd

NORMALIZADO = {
    "light":     "luz",       "flash":     "luz",
    "flare":     "luz",       "fireball":  "bola de fogo",
    "circle":    "disco",     "disk":      "disco",
    "sphere":    "esfera",    "oval":      "oval",
    "round":     "redondo",   "dome":      "cúpula",
    "egg":       "ovo",
    "triangle":  "triângulo", "chevron":   "chevron",
    "delta":     "delta",     "cross":     "cruz",
    "diamond":   "diamante",  "rectangle": "retângulo",
    "hexagon":   "hexágono",  "pyramid":   "pirâmide",
    "crescent":  "crescente",
    "cigar":     "charuto",   "cylinder":  "cilindro",
    "cone":      "cone",      "teardrop":  "lágrima",
    "formation": "formação",  "changing":  "mutável",
    "changed":   "mutável",
    "other":     "outro",     "unknown":   "desconhecido",
}

GRUPO = {
    "luz":          "Luminoso",
    "bola de fogo": "Luminoso",
    "disco":        "Circular",
    "esfera":       "Circular",
    "oval":         "Circular",
    "redondo":      "Circular",
    "cúpula":       "Circular",
    "ovo":          "Circular",
    "triângulo":    "Angular",
    "chevron":      "Angular",
    "delta":        "Angular",
    "cruz":         "Angular",
    "diamante":     "Angular",
    "retângulo":    "Angular",
    "hexágono":     "Angular",
    "pirâmide":     "Angular",
    "crescente":    "Angular",
    "charuto":      "Alongado",
    "cilindro":     "Alongado",
    "cone":         "Alongado",
    "lágrima":      "Alongado",
    "formação":     "Complexo",
    "mutável":      "Complexo",
    "outro":        "Indefinido",
    "desconhecido": "Indefinido",
}

staging = pd.read_parquet("data/processed/ufo_staging.parquet", columns=["shape"])
shapes = staging["shape"].dropna().unique()

df = pd.DataFrame({"shape_original": shapes})
df["shape_normalizado"] = df["shape_original"].map(NORMALIZADO).fillna("desconhecido")
df["grupo_formato"]     = df["shape_normalizado"].map(GRUPO).fillna("Indefinido")
df["sk_formato"] = range(1, len(df) + 1)

df = df[["sk_formato", "shape_original", "shape_normalizado", "grupo_formato"]]

Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_parquet("data/processed/dim_formato.parquet", index=False)
print(f"dim_formato: {len(df)} shapes salvos.")

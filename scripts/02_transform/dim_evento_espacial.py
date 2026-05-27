"""Gera dim_evento_espacial a partir do dataset Space Missions (Kaggle)."""
from pathlib import Path
import pandas as pd

SRC  = Path("data/raw/space_missions/Space_Corrected.csv")
DEST = Path("data/processed/dim_evento_espacial.parquet")

if not SRC.exists():
    print(f"[skip] {SRC} não encontrado.")
    exit(0)

df = pd.read_csv(SRC, encoding="latin-1")

# Extrair missão (parte após " | " no campo Detail) e rocket/agência
df["missao"]  = df["Detail"].str.split(" | ").str[-1].str.strip().str[:150]
df["agencia"] = df["Company Name"].str.strip().str[:50]

# Parsear data — formato "Fri Aug 07, 2020 05:12 UTC"
df["data_lancamento"] = pd.to_datetime(
    df["Datum"].str.replace(r"\s+\d{2}:\d{2} UTC$", "", regex=True),
    format="%a %b %d, %Y",
    errors="coerce",
).dt.date

df = df.dropna(subset=["data_lancamento"])
df = df.drop_duplicates(subset=["missao", "data_lancamento"])
df["distancia_janela"] = None
df["sk_evento_espacial"] = range(1, len(df) + 1)

df = df[["sk_evento_espacial", "missao", "agencia", "data_lancamento", "distancia_janela"]]

DEST.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(DEST, index=False)
print(f"dim_evento_espacial: {len(df):,} missões salvas.")

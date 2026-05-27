"""Gera dim_interesse_cultural a partir dos pageviews da Wikipedia."""
from pathlib import Path
import pandas as pd

SRC = Path("data/raw/pageviews.parquet")
DEST = Path("data/processed/dim_interesse_cultural.parquet")

df = pd.read_parquet(SRC)
df = df.rename(columns={"pageviews": "pageviews_mensais"})
df = df[["ano_mes", "pageviews_mensais", "termo", "idioma", "plataforma"]].drop_duplicates()
df["sk_interesse_cultural"] = range(1, len(df) + 1)
df = df[["sk_interesse_cultural", "ano_mes", "pageviews_mensais", "termo", "idioma", "plataforma"]]

DEST.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(DEST, index=False)
print(f"dim_interesse_cultural: {len(df):,} linhas salvas.")

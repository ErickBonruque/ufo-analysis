"""Gera dim_fonte com as fontes de dados do projeto."""
from pathlib import Path
import pandas as pd

FONTES = ["NUFORC", "HuggingFace", "GEIPAN"]

df = pd.DataFrame({"nome_fonte": FONTES})
df["sk_fonte"] = range(1, len(df) + 1)
df = df[["sk_fonte", "nome_fonte"]]

Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_parquet("data/processed/dim_fonte.parquet", index=False)
print(f"dim_fonte: {len(df)} fontes salvas.")

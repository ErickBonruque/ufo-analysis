"""Gera dim_tempo com granularidade horária de 1900 a 2026."""
from pathlib import Path
import pandas as pd

DIAS_PT = {
    "Monday":    "Segunda-feira",
    "Tuesday":   "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday":  "Quinta-feira",
    "Friday":    "Sexta-feira",
    "Saturday":  "Sábado",
    "Sunday":    "Domingo",
}

datas = pd.date_range("1900-01-01", "2026-12-31", freq="h")
df = pd.DataFrame({"data_completa": datas})
df["sk_tempo"]   = range(1, len(df) + 1)
df["ano"]        = df["data_completa"].dt.year
df["mes"]        = df["data_completa"].dt.month
df["dia"]        = df["data_completa"].dt.day
df["hora"]       = df["data_completa"].dt.hour
df["dia_semana"] = df["data_completa"].dt.day_name().map(DIAS_PT)
df["trimestre"]  = df["data_completa"].dt.quarter

df = df[["sk_tempo", "data_completa", "ano", "mes", "dia", "hora", "dia_semana", "trimestre"]]

Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_parquet("data/processed/dim_tempo.parquet", index=False)
print(f"dim_tempo: {len(df):,} linhas salvas.")

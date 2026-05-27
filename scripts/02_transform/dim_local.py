"""Gera dim_local a partir das localizacoes unicas do staging."""
from pathlib import Path
import pandas as pd

PAIS_REGIAO = {
    "us": "America do Norte", "ca": "America do Norte", "mx": "America Central",
    "br": "America do Sul", "ar": "America do Sul", "cl": "America do Sul",
    "co": "America do Sul",
    "gb": "Europa", "de": "Europa", "fr": "Europa", "it": "Europa",
    "es": "Europa", "pt": "Europa", "nl": "Europa", "be": "Europa",
    "ch": "Europa", "at": "Europa", "se": "Europa", "no": "Europa",
    "dk": "Europa", "fi": "Europa", "pl": "Europa", "cz": "Europa",
    "gr": "Europa", "ie": "Europa", "is": "Europa", "ru": "Europa",
    "tr": "Europa",
    "in": "Asia", "jp": "Asia", "cn": "Asia",
    "au": "Oceania", "nz": "Oceania",
    "za": "Africa",
}

staging = pd.read_parquet("data/processed/ufo_staging.parquet",
                          columns=["cidade", "estado", "pais", "latitude", "longitude"])

locais = (
    staging
    .groupby(["cidade", "estado", "pais"], dropna=False)
    .agg(latitude=("latitude", "mean"), longitude=("longitude", "mean"))
    .reset_index()
)

locais["regiao"] = locais["pais"].map(PAIS_REGIAO).fillna("Outros")
locais["sk_local"] = range(1, len(locais) + 1)
locais = locais[["sk_local", "cidade", "estado", "pais", "latitude", "longitude", "regiao"]]

Path("data/processed").mkdir(parents=True, exist_ok=True)
locais.to_parquet("data/processed/dim_local.parquet", index=False)
print(f"dim_local: {len(locais):,} locais unicos salvos.")

"""Lê o CSV bruto do Kaggle e gera ufo_staging.parquet normalizado."""
from pathlib import Path
import html
import re
import pandas as pd

SRC = Path("data/raw/ufo_kaggle/ufo_sightings_scrubbed.csv")
DEST = Path("data/processed/ufo_staging.parquet")
DEST.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SRC, encoding="latin-1", low_memory=False)

# Renomear para snake_case PT
df = df.rename(columns={
    "datetime":           "data_completa_str",
    "city":               "cidade",
    "state":              "estado",
    "country":            "pais",
    "shape":              "shape",
    "duration (seconds)": "duracao_segundos_raw",
    "date posted":        "data_postagem_str",
    "latitude":           "latitude",
    "longitude ":         "longitude",
})

# Tipos e limpeza
df["data_completa"] = pd.to_datetime(df["data_completa_str"], errors="coerce")
df["data_postagem"] = pd.to_datetime(df["data_postagem_str"], errors="coerce")
df["duracao_segundos"] = pd.to_numeric(df["duracao_segundos_raw"], errors="coerce")
df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

# Lag entre avistamento e postagem (dias)
df["lag_reporte_dias"] = (df["data_postagem"] - df["data_completa"]).dt.days

# Arredondar data para hora cheia (para join com dim_tempo)
df["data_completa"] = df["data_completa"].dt.floor("h")

# Padronizar strings
for col in ["cidade", "estado", "pais", "shape"]:
    df[col] = df[col].str.strip().str.lower()

# Decodificar HTML entities nos nomes de cidades (ex: &ccedil;anakkale → çanakkale)
df["cidade"] = df["cidade"].apply(lambda x: html.unescape(x) if isinstance(x, str) else x)

# Tentar recuperar país a partir do nome da cidade quando pais é NaN
# Ex: "çanakkale (turkey)" → pais = "tr" | "ölmstad (sweden)" → pais = "se"
PAIS_NOME_PARA_CODIGO = {
    "turkey": "tr", "sweden": "se", "iceland": "is", "mexico": "mx",
    "france": "fr", "germany": "de", "italy": "it", "spain": "es",
    "india": "in", "japan": "jp", "brazil": "br", "china": "cn",
    "australia": "au", "canada": "ca", "uk": "gb", "england": "gb",
    "scotland": "gb", "ireland": "ie", "portugal": "pt", "netherlands": "nl",
    "russia": "ru", "argentina": "ar", "chile": "cl", "colombia": "co",
    "new zealand": "nz", "south africa": "za", "norway": "no",
    "denmark": "dk", "finland": "fi", "switzerland": "ch", "austria": "at",
    "belgium": "be", "poland": "pl", "czech": "cz", "greece": "gr",
}

def extrair_pais_da_cidade(row):
    """Se pais é NaN, tenta extrair de padrões como 'cidade (country)'."""
    if pd.notna(row["pais"]):
        return row["pais"]
    cidade = row["cidade"] if isinstance(row["cidade"], str) else ""
    match = re.search(r'\(([^)]+)\)\s*$', cidade)
    if match:
        termo = match.group(1).strip().lower()
        for nome, codigo in PAIS_NOME_PARA_CODIGO.items():
            if nome in termo:
                return codigo
    return "us"  # fallback padrão

df["pais"] = df.apply(extrair_pais_da_cidade, axis=1)

df["shape"] = df["shape"].fillna("unknown")
df["fonte"] = "NUFORC"

# ── Tratar outliers de duração ────────────────────────────────────────────────
# Duração acima de 24h (86400s) é improvável — marcada como suspeita e capada
DURACAO_MAX = 86_400  # 24 horas em segundos
df["duracao_suspeita"] = df["duracao_segundos"] > DURACAO_MAX
df["duracao_segundos"] = df["duracao_segundos"].clip(lower=0, upper=DURACAO_MAX)

n_suspeitos = df["duracao_suspeita"].sum()
if n_suspeitos:
    print(f"  [warn] {n_suspeitos:,} avistamentos com duração > 24h → capados em 86400s e marcados como suspeitos")

# ── Tratar outliers de lag de reporte ────────────────────────────────────────
# Lag negativo = erro de data (postagem antes do avistamento) → NULL
# Lag > 36500 dias (~100 anos) = implausível → NULL
df.loc[df["lag_reporte_dias"] < 0,     "lag_reporte_dias"] = None
df.loc[df["lag_reporte_dias"] > 36500, "lag_reporte_dias"] = None

n_lag_nulos = df["lag_reporte_dias"].isna().sum()
print(f"  [info] lag_reporte_dias: {n_lag_nulos:,} valores nulos (negativos ou implausíveis removidos)")

# Colunas finais
colunas = [
    "data_completa", "cidade", "estado", "pais", "shape",
    "duracao_segundos", "duracao_suspeita", "lag_reporte_dias",
    "latitude", "longitude", "fonte",
]
df = df[colunas].dropna(subset=["data_completa"])

df.to_parquet(DEST, index=False)
print(f"Staging: {len(df)} linhas salvas em {DEST}")

"""
Carrega todos os dados corrigidos (parquets) no PostgreSQL.

Pre-requisito: correr sql/migrations/01_prep_reload.sql no pgAdmin primeiro.

Dependencias:
    pip install pandas pyarrow psycopg2-binary sqlalchemy python-dotenv

Configurar no .env:
    PG_HOST=localhost
    PG_PORT=5432
    PG_DB=ufo
    PG_USER=postgres
    PG_PASSWORD=admin
"""
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(encoding="utf-8-sig")  # utf-8-sig tolera BOM do Windows

# Conexao PostgreSQL
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB   = os.getenv("PG_DB",   "ufo_dw")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASS = os.getenv("PG_PASSWORD", "")

engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}",
    echo=False
)

# Testar conexao antes de comecar a carga
print(f"Conectando em {PG_HOST}:{PG_PORT}/{PG_DB} como {PG_USER}...")
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Conexao OK!\n")
except Exception as e:
    print(f"\nERRO de conexao: {e}")
    print("Verifique host, porta, banco e password no .env")
    exit(1)

# Colunas de cada dimensao (apenas as do DDL do PostgreSQL)
DIMS = {
    "dim_tempo":              ["sk_tempo","data_completa","ano","mes","dia","hora","dia_semana","trimestre"],
    "dim_local":              ["sk_local","cidade","estado","pais","latitude","longitude","regiao"],
    "dim_formato":            ["sk_formato","shape_original","shape_normalizado","grupo_formato"],
    "dim_fonte":              ["sk_fonte","nome_fonte"],
    "dim_clima":              ["sk_clima","cobertura_nuvens","visibilidade","vento","temperatura","codigo_clima"],
    "dim_aeroporto":          ["sk_aeroporto","aeroporto_mais_proximo","distancia_km","tipo_aeroporto"],
    "dim_evento_espacial":    ["sk_evento_espacial","missao","agencia","data_lancamento","distancia_janela"],
    "dim_interesse_cultural": ["sk_interesse_cultural","ano_mes","pageviews_mensais","termo","idioma","plataforma"],
}

FATO_COLUNAS = [
    "sk_avistamento","sk_tempo","sk_local","sk_formato","sk_fonte",
    "sk_clima","sk_aeroporto","sk_evento_espacial","sk_interesse_cultural",
    "duracao_segundos","duracao_suspeita","lag_reporte_dias",
    "latitude","longitude","quantidade_relato",
]

def carregar(tabela, df, engine, chunksize=10_000):
    """Insere DataFrame no PostgreSQL em chunks."""
    total = len(df)
    df.to_sql(
        tabela,
        con=engine,
        schema="public",
        if_exists="append",
        index=False,
        chunksize=chunksize,
        method="multi",
    )
    print(f"  {tabela}: {total:,} linhas carregadas")

print("=== CARGA POSTGRESQL ===\n")

# 1. Dimensoes
for tabela, colunas in DIMS.items():
    parquet = Path(f"data/processed/{tabela}.parquet")
    if not parquet.exists():
        print(f"  [SKIP] {parquet} nao encontrado")
        continue
    df = pd.read_parquet(parquet)
    df = df[[c for c in colunas if c in df.columns]]
    carregar(tabela, df, engine)

# 2. Fato — ler do warehouse/separadas (ja montada com joins)
fato_pq = Path("data/warehouse/separadas/fato_avistamento.parquet")
if fato_pq.exists():
    df_fato = pd.read_parquet(fato_pq)
    df_fato = df_fato[[c for c in FATO_COLUNAS if c in df_fato.columns]]
    # Garantir que duracao_suspeita existe (retrocompat)
    if "duracao_suspeita" not in df_fato.columns:
        df_fato["duracao_suspeita"] = False
    carregar("fato_avistamento", df_fato, engine, chunksize=5_000)
else:
    print(f"  [SKIP] {fato_pq} nao encontrado")

# 3. Verificacao final
print("\n=== VERIFICACAO FINAL ===")
with engine.connect() as con:
    for tabela in list(DIMS.keys()) + ["fato_avistamento"]:
        n = con.execute(text(f"SELECT COUNT(*) FROM public.{tabela}")).scalar()
        print(f"  {tabela}: {n:,}")

print("\nCarga concluida!")

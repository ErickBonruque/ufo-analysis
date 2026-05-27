"""Carrega todas as dimensões processadas no DW."""
from pathlib import Path
import duckdb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
con = duckdb.connect(os.getenv("DW_PATH", "data/warehouse/ufo_dw.duckdb"))

# Colunas esperadas por cada tabela (apenas as do DDL)
COLUNAS = {
    "dim_tempo":               ["sk_tempo", "data_completa", "ano", "mes", "dia", "hora", "dia_semana", "trimestre"],
    "dim_local":               ["sk_local", "cidade", "estado", "pais", "latitude", "longitude", "regiao"],
    "dim_formato":             ["sk_formato", "shape_original", "shape_normalizado", "grupo_formato"],
    "dim_fonte":               ["sk_fonte", "nome_fonte"],
    "dim_clima":               ["sk_clima", "cobertura_nuvens", "visibilidade", "vento", "temperatura", "codigo_clima"],
    "dim_aeroporto":           ["sk_aeroporto", "aeroporto_mais_proximo", "distancia_km", "tipo_aeroporto"],
    "dim_evento_espacial":     ["sk_evento_espacial", "missao", "agencia", "data_lancamento", "distancia_janela"],
    "dim_interesse_cultural":  ["sk_interesse_cultural", "ano_mes", "pageviews_mensais", "termo", "idioma", "plataforma"],
}

# Limpa fato primeiro para não violar FKs ao recarregar dims
con.execute("DELETE FROM fato_avistamento")

for dim, colunas in COLUNAS.items():
    arquivo = f"data/processed/{dim}.parquet"
    if not Path(arquivo).exists():
        print(f"  [skip] {arquivo} não encontrado")
        continue
    df = pd.read_parquet(arquivo)
    # Seleciona só as colunas do DDL (ignora colunas auxiliares de join)
    df = df[[c for c in colunas if c in df.columns]]
    con.execute(f"DELETE FROM {dim}")
    con.register("_df_temp", df)
    cols = ", ".join(df.columns)
    con.execute(f"INSERT INTO {dim} ({cols}) SELECT {cols} FROM _df_temp")
    qtd = con.execute(f"SELECT COUNT(*) FROM {dim}").fetchone()[0]
    print(f"  {dim}: {qtd:,} linhas")

con.close()

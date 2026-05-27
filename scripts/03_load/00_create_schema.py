"""Cria o schema completo do DW UFO no DuckDB."""
from pathlib import Path
import duckdb
from dotenv import load_dotenv
import os

load_dotenv()
DW_PATH = os.getenv("DW_PATH", "data/warehouse/ufo_dw.duckdb")
DDL_DIR = Path("sql/ddl")

# Tabelas que devem ser expostas via schema 'public' para o Power BI
TABELAS_PUBLIC = [
    "dim_tempo",
    "dim_local",
    "dim_formato",
    "dim_fonte",
    "dim_clima",
    "dim_aeroporto",
    "dim_evento_espacial",
    "dim_interesse_cultural",
    "fato_avistamento",
]

def criar_views_public(con: duckdb.DuckDBPyConnection) -> None:
    """
    Cria o schema 'public' e expõe todas as tabelas do DW como views.

    O Power BI (e conectores PostgreSQL/ODBC) costumam prefixar tabelas com
    'public.' — sem esse mapeamento a fato_avistamento aparece vazia no PBI.
    """
    con.execute("CREATE SCHEMA IF NOT EXISTS public")
    for tabela in TABELAS_PUBLIC:
        con.execute(
            f"CREATE OR REPLACE VIEW public.{tabela} AS SELECT * FROM main.{tabela}"
        )
        print(f"  -> view public.{tabela} criada")

def main() -> None:
    Path(DW_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(DW_PATH)

    arquivos = sorted(DDL_DIR.glob("*.sql"))
    for arquivo in arquivos:
        print(f"-> executando {arquivo.name}")
        con.execute(arquivo.read_text(encoding="utf-8"))

    print("\nCriando views public.* para compatibilidade com Power BI...")
    criar_views_public(con)

    tabelas = con.execute("SHOW TABLES").fetchall()
    print("\nTabelas criadas:")
    for (t,) in tabelas:
        print(f"  - {t}")
    con.close()

if __name__ == "__main__":
    main()

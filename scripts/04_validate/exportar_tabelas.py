"""Exporta cada tabela do DW como CSV e Parquet, prontos para entrega."""
from pathlib import Path
import duckdb
import os
from dotenv import load_dotenv

load_dotenv()
DEST = Path("data/warehouse/separadas")
DEST.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(os.getenv("DW_PATH", "data/warehouse/ufo_dw.duckdb"))

tabelas = [t for (t,) in con.execute("SHOW TABLES").fetchall()]
for t in tabelas:
    con.execute(f"COPY {t} TO '{DEST}/{t}.csv'     (HEADER, DELIMITER ';')")
    con.execute(f"COPY {t} TO '{DEST}/{t}.parquet'  (FORMAT PARQUET)")
    print(f"  {t} exportada")
con.close()

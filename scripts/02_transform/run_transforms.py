"""Executa todas as transformações na ordem correta."""
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable

ETAPAS = [
    ("Staging (Kaggle → parquet normalizado)", "scripts/02_transform/00_staging.py"),
    ("dim_tempo",                              "scripts/02_transform/dim_tempo.py"),
    ("dim_local",                              "scripts/02_transform/dim_local.py"),
    ("dim_formato",                            "scripts/02_transform/dim_formato.py"),
    ("dim_fonte",                              "scripts/02_transform/dim_fonte.py"),
    ("dim_interesse_cultural",                 "scripts/02_transform/dim_interesse_cultural.py"),
    ("dim_aeroporto (demorado ~2 min)",        "scripts/02_transform/dim_aeroporto.py"),
    ("dim_evento_espacial",                    "scripts/02_transform/dim_evento_espacial.py"),
]

for nome, script in ETAPAS:
    print(f"\n{'='*55}\n>> {nome}\n{'='*55}")
    r = subprocess.run([PYTHON, script], check=False)
    if r.returncode != 0:
        print(f"[ERRO] '{nome}' falhou. Abortando.")
        sys.exit(r.returncode)

print("\nTodas as transformações concluídas. Execute 03_load/01_load_dimensoes.py em seguida.")

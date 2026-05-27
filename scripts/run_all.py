"""Orquestra o pipeline completo do DW UFO."""
import subprocess
import sys

ETAPAS = [
    ("Schema DW",          ["python", "scripts/03_load/00_create_schema.py"]),
    ("Download Kaggle",    ["python", "scripts/01_download/01_ufo_kaggle.py"]),
    ("Download Aeroportos",["python", "scripts/01_download/02_ourairports.py"]),
    ("Pageviews Wikipedia",["python", "scripts/01_download/05_wikipedia_pageviews.py"]),
    ("Dim Tempo",          ["python", "scripts/02_transform/dim_tempo.py"]),
    ("Carga Dimensões",    ["python", "scripts/03_load/01_load_dimensoes.py"]),
]

for nome, cmd in ETAPAS:
    print(f"\n{'='*50}\n>> {nome}\n{'='*50}")
    resultado = subprocess.run(cmd, check=False)
    if resultado.returncode != 0:
        print(f"[ERRO] Etapa '{nome}' falhou (código {resultado.returncode}). Abortando.")
        sys.exit(resultado.returncode)

print("\nPipeline concluído.")

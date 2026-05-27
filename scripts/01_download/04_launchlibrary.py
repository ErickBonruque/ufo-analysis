"""Baixa histórico de lançamentos espaciais com retry para rate-limit."""
from pathlib import Path
import time
import requests
import pandas as pd

URL = "https://ll.thespacedevs.com/2.2.0/launch/?limit=100&mode=detailed&ordering=net"
DEST = Path("data/raw/lancamentos.parquet")

def get_com_retry(url: str, max_tentativas: int = 5) -> dict:
    for tentativa in range(max_tentativas):
        r = requests.get(url, timeout=60)
        if r.status_code == 429:
            espera = int(r.headers.get("Retry-After", 60)) + 5
            print(f"  Rate limit atingido, aguardando {espera}s...")
            time.sleep(espera)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Falhou após {max_tentativas} tentativas: {url}")

def main() -> None:
    todos = []
    url = URL
    pagina = 1
    while url:
        print(f"  Página {pagina}...")
        dados = get_com_retry(url)
        todos.extend(dados["results"])
        url = dados.get("next")
        pagina += 1
        if len(todos) >= 5000:  # safety cap
            break
        time.sleep(1.5)  # respeita o rate limit da API gratuita
    df = pd.json_normalize(todos)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DEST)
    print(f"{len(df)} lançamentos salvos em {DEST}")

if __name__ == "__main__":
    main()

"""Baixa o CSV de aeroportos do OurAirports."""
from pathlib import Path
import requests

URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
DEST = Path("data/raw/airports.csv")

def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    DEST.write_bytes(r.content)
    print(f"Salvo em {DEST} ({DEST.stat().st_size/1e6:.1f} MB)")

if __name__ == "__main__":
    main()

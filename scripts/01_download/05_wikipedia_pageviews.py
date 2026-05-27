"""Coleta pageviews mensais de termos relacionados a UFO."""
from pathlib import Path
import requests
import pandas as pd

TERMOS = {
    "en": ["UFO", "Unidentified_flying_object", "UAP"],
    "pt": ["OVNI", "Objeto_voador_não_identificado"],
}
BASE = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        "{idioma}.wikipedia/all-access/all-agents/{termo}/monthly/2010010100/2024123100")

def main() -> None:
    linhas = []
    for idioma, termos in TERMOS.items():
        for termo in termos:
            url = BASE.format(idioma=idioma, termo=termo)
            r = requests.get(url, headers={"User-Agent": "ufo-dw-academico/1.0"}, timeout=30)
            if r.status_code != 200:
                continue
            for item in r.json().get("items", []):
                linhas.append({
                    "termo": termo,
                    "idioma": idioma,
                    "ano_mes": item["timestamp"][:6],
                    "pageviews": item["views"],
                    "plataforma": "wikipedia",
                })
    df = pd.DataFrame(linhas)
    df.to_parquet("data/raw/pageviews.parquet")
    print(f"{len(df)} linhas coletadas")

if __name__ == "__main__":
    main()

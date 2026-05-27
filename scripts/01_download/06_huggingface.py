"""Baixa dataset complementar do Hugging Face."""
from pathlib import Path
import requests

URL = "https://huggingface.co/datasets/cjc0013/Ufo_data_clustered/resolve/main/data/ufo_data_clustered.jsonl"
DEST = Path("data/raw/ufo_huggingface.jsonl")

def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    DEST.write_bytes(r.content)
    print(f"Salvo em {DEST}")

if __name__ == "__main__":
    main()

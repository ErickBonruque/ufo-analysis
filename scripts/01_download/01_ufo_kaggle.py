"""Baixa o dataset UFO Sightings do Kaggle."""
from pathlib import Path
import shutil
import kagglehub
from dotenv import load_dotenv

load_dotenv()

DEST = Path("data/raw/ufo_kaggle")

def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    cache_path = kagglehub.dataset_download("sahityasetu/ufo-sightings")
    for arquivo in Path(cache_path).glob("*"):
        shutil.copy2(arquivo, DEST / arquivo.name)
    print(f"Arquivos salvos em: {DEST}")

if __name__ == "__main__":
    main()

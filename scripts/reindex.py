from pathlib import Path

from domani_photo_search.config.settings import settings
from domani_photo_search.indexing.ingest import ingest_csv

if __name__ == "__main__":
    csv_path = Path(settings.csv_source_path)
    ingest_csv(csv_path, settings.processed_dir)
    print(f"Reindexed from {csv_path}")

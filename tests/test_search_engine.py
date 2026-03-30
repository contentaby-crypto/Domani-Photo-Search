from pathlib import Path

from domani_photo_search.indexing.ingest import ingest_csv
from domani_photo_search.search.engine import SearchEngine
from domani_photo_search.testing.sample_data import create_sample_csv


def test_search_engine_filters_by_object(tmp_path: Path):
    csv = create_sample_csv(tmp_path / "sample_photos.csv")
    ingest_csv(csv, tmp_path)
    engine = SearchEngine(tmp_path / 'photos.jsonl', tmp_path / 'dictionaries')

    result = engine.search('DEPO вертикальные кадры с симметрией', top_k=20)

    assert result['shortlist_total'] > 0
    assert all('depo' in item['object'].lower() for item in result['shortlist'])

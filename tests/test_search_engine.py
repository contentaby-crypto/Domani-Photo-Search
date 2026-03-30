from pathlib import Path

from domani_photo_search.indexing.ingest import ingest_csv
from domani_photo_search.search.engine import SearchEngine


def test_search_engine_filters_by_object(tmp_path: Path):
    csv = Path('/mnt/data/База данных фото Domani - New (4).csv')
    ingest_csv(csv, tmp_path)
    engine = SearchEngine(tmp_path / 'photos.jsonl', tmp_path / 'dictionaries')

    result = engine.search('DEPO вертикальные кадры с симметрией', top_k=20)

    assert result['shortlist_total'] > 0
    assert all('depo' in item['object'].lower() for item in result['shortlist'])

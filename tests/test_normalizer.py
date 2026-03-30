from pathlib import Path

from domani_photo_search.indexing.ingest import ingest_csv
from domani_photo_search.search.normalizer import QueryNormalizer


def test_normalizer_uses_generated_dictionaries(tmp_path: Path):
    csv = Path('/mnt/data/База данных фото Domani - New (4).csv')
    ingest_csv(csv, tmp_path)
    normalizer = QueryNormalizer(tmp_path / 'dictionaries')

    result = normalizer.normalize('Найди серую кухню. Была на квартире у Игнатьева')

    assert 'кухня' in result.room_objects
    assert 'серый' in result.colors or 'светлые' in result.color_groups or result.colors
    assert any('игнатьев' in obj for obj in result.objects)

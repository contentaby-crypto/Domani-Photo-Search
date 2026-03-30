from pathlib import Path

from fastapi.testclient import TestClient

from domani_photo_search.api.main import create_app
from domani_photo_search.indexing.ingest import ingest_csv
from domani_photo_search.testing.sample_data import create_sample_csv


def build_client(tmp_path: Path):
    csv = create_sample_csv(tmp_path / "sample_photos.csv")
    ingest_csv(csv, tmp_path)
    app = create_app()
    app.state.search_engine = __import__('domani_photo_search.search.engine', fromlist=['SearchEngine']).SearchEngine(tmp_path / 'photos.jsonl', tmp_path / 'dictionaries')
    return TestClient(app)


def test_search_query_contract(tmp_path: Path):
    client = build_client(tmp_path)
    response = client.post('/v1/search/query', json={
        'request_id': 'req-1',
        'session_id': 's-1',
        'user_id': 'u-1',
        'message_id': 'm-1',
        'query_text': 'Найди серую кухню',
        'top_k': 10,
        'llm_top_n': 5,
        'context': {'mode': 'test'}
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload['request_id'] == 'req-1'
    assert 'normalized_query' in payload
    assert 'shortlist' in payload

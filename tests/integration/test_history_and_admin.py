from pathlib import Path

from fastapi.testclient import TestClient

from domani_photo_search.api.main import create_app
from domani_photo_search.testing.sample_data import create_sample_csv


def test_query_history_and_reindex(monkeypatch, tmp_path):
    app = create_app()
    client = TestClient(app)

    payload = {
        "request_id": "req-1",
        "session_id": "tg-1",
        "user_id": "1",
        "message_id": "1",
        "query_text": "Найди серую кухню",
        "top_k": 10,
        "llm_top_n": 5,
        "context": {"mode": "test"},
    }
    response = client.post('/v1/search/query', json=payload)
    assert response.status_code == 200
    stored = app.state.history_store.get_request('req-1')
    assert stored is not None
    assert stored['query_text'] == 'Найди серую кухню'

    csv_path = create_sample_csv(tmp_path / "sample_photos.csv")
    reindex = client.post('/admin/reindex', json={"csv_path": str(csv_path)}, headers={'x-admin-token': 'change-me'})
    assert reindex.status_code == 200
    assert reindex.json()['status'] == 'ok'

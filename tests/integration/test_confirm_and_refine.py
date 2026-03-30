from fastapi.testclient import TestClient

from domani_photo_search.api.main import create_app


def test_confirm_send_all_and_refine_from_history():
    app = create_app()
    client = TestClient(app)
    payload = {
        "request_id": "req-2",
        "session_id": "tg-2",
        "user_id": "2",
        "message_id": "2",
        "query_text": "DEPO вертикальные кадры с симметрией",
        "top_k": 10,
        "llm_top_n": 5,
        "context": {"mode": "test"},
    }
    search = client.post('/v1/search/query', json=payload)
    assert search.status_code == 200
    confirm = client.post('/v1/search/confirm-send-all', json={"request_id": "req-2", "session_id": "tg-2", "shortlist": [], "batch_size": 4})
    assert confirm.status_code == 200
    assert confirm.json()['batches_total'] >= 1
    hints = client.post('/v1/search/refine-hints', json={"request_id": "req-2", "session_id": "tg-2", "normalized_query": {}})
    assert hints.status_code == 200
    assert isinstance(hints.json()['hints'], list)

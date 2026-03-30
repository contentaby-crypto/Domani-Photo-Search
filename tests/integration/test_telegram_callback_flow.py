from fastapi.testclient import TestClient

from domani_photo_search.api.main import create_app
from domani_photo_search.bot import webhook


def test_send_all_callback_uses_latest_history_when_request_id_missing(monkeypatch):
    app = create_app()
    client = TestClient(app)

    query_payload = {
        "request_id": "req-send-all",
        "session_id": "tg-101",
        "user_id": "101",
        "message_id": "1",
        "query_text": "покажи кухни",
        "top_k": 10,
        "llm_top_n": 5,
        "context": {"mode": "test"},
    }
    assert client.post("/v1/search/query", json=query_payload).status_code == 200

    captured: dict[str, str] = {}

    async def fake_confirm(request_id: str, session_id: str) -> dict:
        captured["request_id"] = request_id
        captured["session_id"] = session_id
        return {
            "request_id": request_id,
            "batches": [[{"photo_id": "PH-1", "file_name": "a.jpg", "object_display": "Obj", "main_objects": [], "url": "http://x"}]],
            "batches_total": 1,
        }

    sent_photos: list[tuple[int | str, str, str | None]] = []

    async def fake_send_photo(chat_id, photo_url, caption=None):
        sent_photos.append((chat_id, photo_url, caption))
        return {"ok": True}

    async def fake_answer(_callback_id, text=None):
        return {"ok": True, "text": text}

    monkeypatch.setattr(webhook, "_call_confirm_send_all", fake_confirm)
    monkeypatch.setattr(webhook.telegram, "send_photo", fake_send_photo)
    monkeypatch.setattr(webhook.telegram, "answer_callback_query", fake_answer)

    response = client.post(
        "/telegram/webhook",
        json={
            "callback_query": {
                "id": "cb-1",
                "data": "send_all::0",
                "message": {"chat": {"id": 101}},
            }
        },
    )

    assert response.status_code == 200
    assert captured["request_id"] == "req-send-all"
    assert captured["session_id"] == "tg-101"
    assert len(sent_photos) == 1


def test_refine_callback_uses_latest_history_when_request_id_missing(monkeypatch):
    app = create_app()
    client = TestClient(app)

    query_payload = {
        "request_id": "req-refine",
        "session_id": "tg-202",
        "user_id": "202",
        "message_id": "1",
        "query_text": "покажи кухни",
        "top_k": 10,
        "llm_top_n": 5,
        "context": {"mode": "test"},
    }
    assert client.post("/v1/search/query", json=query_payload).status_code == 200

    captured: dict[str, str] = {}

    async def fake_refine(request_id: str, session_id: str) -> dict:
        captured["request_id"] = request_id
        captured["session_id"] = session_id
        return {"request_id": request_id, "hints": ["Добавьте цвет"]}

    sent_messages: list[str] = []

    async def fake_send_message(_chat_id, text, reply_markup=None):
        sent_messages.append(text)
        return {"ok": True}

    async def fake_answer(_callback_id, text=None):
        return {"ok": True, "text": text}

    monkeypatch.setattr(webhook, "_call_refine_hints", fake_refine)
    monkeypatch.setattr(webhook.telegram, "send_message", fake_send_message)
    monkeypatch.setattr(webhook.telegram, "answer_callback_query", fake_answer)

    response = client.post(
        "/telegram/webhook",
        json={
            "callback_query": {
                "id": "cb-2",
                "data": "refine::0",
                "message": {"chat": {"id": 202}},
            }
        },
    )

    assert response.status_code == 200
    assert captured["request_id"] == "req-refine"
    assert captured["session_id"] == "tg-202"
    assert sent_messages
    assert "Последний запрос: покажи кухни" in sent_messages[0]


def test_telegram_direct_flow_falls_back_to_deterministic_when_ranking_fails(monkeypatch):
    app = create_app()
    client = TestClient(app)

    async def fake_search_api(_payload: dict) -> dict:
        return {
            "request_id": "req-telegram-direct",
            "delivery_mode": "direct",
            "normalized_query": {"objects": ["depo"]},
            "shortlist": [
                {"photo_id": "PH-2", "score_det": 7, "file_name": "b.jpg", "object_display": "Obj B", "main_objects": [], "url": "http://b"},
                {"photo_id": "PH-1", "score_det": 10, "file_name": "a.jpg", "object_display": "Obj A", "main_objects": [], "url": "http://a"},
            ],
        }

    async def fake_ranking_api(**_kwargs):
        raise RuntimeError("ranking unavailable")

    sent_ids: list[str] = []

    async def fake_send_photo(_chat_id, photo_url, caption=None):
        sent_ids.append(photo_url)
        return {"ok": True}

    monkeypatch.setattr(webhook, "_call_search_api", fake_search_api)
    monkeypatch.setattr(webhook, "_call_ranking_api", fake_ranking_api)
    monkeypatch.setattr(webhook.telegram, "send_photo", fake_send_photo)

    response = client.post(
        "/telegram/webhook",
        json={
            "message": {
                "message_id": 77,
                "text": "найди depo",
                "chat": {"id": 303},
                "from": {"id": 404},
            }
        },
    )

    assert response.status_code == 200
    assert sent_ids == ["http://b", "http://a"]

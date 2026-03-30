from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request
import httpx

from domani_photo_search.bot.telegram_client import TelegramClient
from domani_photo_search.config.settings import settings

router = APIRouter(prefix="/telegram", tags=["telegram"])
telegram = TelegramClient()


def _inline_keyboard(search_result: dict) -> dict | None:
    action = search_result.get("prompt_user_action")
    if not action or not action.get("buttons"):
        return None
    buttons = []
    request_id = search_result.get("request_id", "")
    for button in action["buttons"]:
        buttons.append([
            {"text": button["title"], "callback_data": f"{button['action']}:{request_id}"}
        ])
    return {"inline_keyboard": buttons}


def _caption(item: dict) -> str:
    tags = ", ".join(item.get("main_objects", [])[:4])
    return f"{item['file_name']}\n{item['object_display']}\n{tags}".strip()


async def _call_search_api(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{settings.search_api_base_url}/v1/search/query", json=payload)
        response.raise_for_status()
        return response.json()


async def _call_confirm_send_all(request_id: str, session_id: str) -> dict:
    payload = {"request_id": request_id, "session_id": session_id, "shortlist": [], "batch_size": 8}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{settings.search_api_base_url}/v1/search/confirm-send-all", json=payload)
        response.raise_for_status()
        return response.json()


async def _call_refine_hints(request_id: str, session_id: str) -> dict:
    payload = {"request_id": request_id, "session_id": session_id, "normalized_query": {}}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{settings.search_api_base_url}/v1/search/refine-hints", json=payload)
        response.raise_for_status()
        return response.json()


async def _call_ranking_api(
    *,
    request_id: str,
    query_text: str,
    normalized_query: dict,
    shortlist: list[dict],
    top_n: int,
) -> dict:
    payload = {
        "request_id": request_id,
        "query_text": query_text,
        "normalized_query": normalized_query,
        "shortlist": shortlist,
        "top_n": top_n,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{settings.search_api_base_url}/v1/ranking/rank", json=payload)
        response.raise_for_status()
        return response.json()


def _resolve_callback_request_id(*, request: Request, session_id: str, request_id: str) -> str:
    if request_id:
        return request_id
    stored = request.app.state.history_store.get_latest_request_for_session(session_id)
    if stored:
        return stored["request_id"]
    return ""


def _ordered_items(search_result: dict, ranking_result: dict | None, top_n: int) -> list[dict]:
    shortlist = search_result.get("shortlist", [])
    if not ranking_result:
        return shortlist[:top_n]
    ranked_items = ranking_result.get("ranked_items", [])
    if not ranking_result.get("safe_to_show", True) or not ranked_items:
        return shortlist[:top_n]
    by_id = {item["photo_id"]: item for item in shortlist}
    ordered: list[dict] = []
    for ranked in sorted(ranked_items, key=lambda x: x.get("rank", 9999)):
        photo_id = ranked.get("photo_id")
        if photo_id in by_id:
            ordered.append(by_id[photo_id])
    return ordered[:top_n] if ordered else shortlist[:top_n]


@router.post("/webhook")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    expected = settings.telegram_secret_token or None
    if expected and x_telegram_bot_api_secret_token != expected:
        raise HTTPException(status_code=401, detail="invalid_secret_token")

    update = await request.json()
    callback = update.get("callback_query")
    if callback:
        chat_id = callback.get("message", {}).get("chat", {}).get("id")
        data = callback.get("data", "")
        callback_id = callback.get("id", "")
        parts = data.split(":", 2)
        action = parts[0] if parts else ""
        request_id = parts[1] if len(parts) > 1 else ""
        session_id = f"tg-{chat_id}"
        request_id = _resolve_callback_request_id(request=request, session_id=session_id, request_id=request_id)
        if not request_id:
            await telegram.answer_callback_query(callback_id, text="Контекст запроса не найден")
            return {"ok": True, "handled": "callback_query", "data": data, "status": "missing_request_context"}
        if action == "send_all":
            result = await _call_confirm_send_all(request_id, session_id)
            total = 0
            for batch in result.get("batches", []):
                for item in batch:
                    total += 1
                    await telegram.send_photo(
                        chat_id,
                        item.get("preview_url") or item.get("url", ""),
                        caption=_caption(item),
                    )
            await telegram.answer_callback_query(callback_id, text=f"Отправлено фото: {total}")
        elif action == "refine":
            result = await _call_refine_hints(request_id, session_id)
            stored = request.app.state.history_store.get_request(request_id)
            query_prefix = f"Последний запрос: {stored['query_text']}\n" if stored else ""
            hints_text = f"{query_prefix}Как уточнить запрос:\n- " + "\n- ".join(result.get("hints", []))
            await telegram.send_message(chat_id, hints_text)
            await telegram.answer_callback_query(callback_id, text="Показал подсказки")
        else:
            await telegram.answer_callback_query(callback_id, text="Неизвестное действие")
        return {"ok": True, "handled": "callback_query", "data": data}

    message = update.get("message", {})
    text = message.get("text", "").strip()
    chat = message.get("chat", {})
    from_user = message.get("from", {})

    if not text:
        return {"ok": True, "ignored": "non_text_update"}

    payload = {
        "request_id": f"tg-{message.get('message_id', '0')}-{from_user.get('id', '0')}",
        "session_id": f"tg-{chat.get('id', '0')}",
        "user_id": str(from_user.get('id', '0')),
        "message_id": str(message.get('message_id', '0')),
        "query_text": text,
        "top_k": 50,
        "llm_top_n": 10,
        "context": {"mode": "telegram"},
    }
    search_result = await _call_search_api(payload)

    if search_result["delivery_mode"] == "not_found":
        text = search_result["prompt_user_action"]["text"]
        await telegram.send_message(chat["id"], text)
    elif search_result["delivery_mode"] == "ask_user":
        text = search_result["prompt_user_action"]["text"]
        await telegram.send_message(chat["id"], text, reply_markup=_inline_keyboard(search_result))
    else:
        ranking_result = None
        try:
            ranking_result = await _call_ranking_api(
                request_id=payload["request_id"],
                query_text=payload["query_text"],
                normalized_query=search_result.get("normalized_query", {}),
                shortlist=search_result.get("shortlist", []),
                top_n=payload["llm_top_n"],
            )
        except Exception:
            ranking_result = None

        for item in _ordered_items(search_result, ranking_result, top_n=10):
            await telegram.send_photo(
                chat["id"],
                item.get("preview_url") or item.get("url", ""),
                caption=_caption(item),
            )

    return {"ok": True, "search_result": search_result}

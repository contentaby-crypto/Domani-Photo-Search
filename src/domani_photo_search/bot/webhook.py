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
        action, _, request_id = data.partition(":")
        session_id = f"tg-{chat_id}"
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
            hints_text = "Как уточнить запрос:\n- " + "\n- ".join(result.get("hints", []))
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
        for item in search_result.get("shortlist", [])[:10]:
            await telegram.send_photo(
                chat["id"],
                item.get("preview_url") or item.get("url", ""),
                caption=_caption(item),
            )

    return {"ok": True, "search_result": search_result}

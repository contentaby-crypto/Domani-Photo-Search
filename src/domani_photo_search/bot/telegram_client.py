from __future__ import annotations

import httpx

from domani_photo_search.config.settings import settings


class TelegramClient:
    def __init__(self) -> None:
        self.base_url = f"{settings.telegram_api_base}/bot{settings.bot_token}" if settings.bot_token else ""

    async def send_message(self, chat_id: int | str, text: str, reply_markup: dict | None = None) -> dict:
        if not self.base_url:
            return {"ok": False, "reason": "bot_token_missing", "text": text, "reply_markup": reply_markup}
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/sendMessage", json=payload)
            response.raise_for_status()
            return response.json()

    async def answer_callback_query(self, callback_query_id: str, text: str | None = None) -> dict:
        if not self.base_url:
            return {"ok": False, "reason": "bot_token_missing", "callback_query_id": callback_query_id, "text": text}
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/answerCallbackQuery", json=payload)
            response.raise_for_status()
            return response.json()

    async def send_photo(self, chat_id: int | str, photo_url: str, caption: str | None = None) -> dict:
        if not self.base_url:
            return {"ok": False, "reason": "bot_token_missing", "photo": photo_url, "caption": caption}
        payload = {"chat_id": chat_id, "photo": photo_url}
        if caption:
            payload["caption"] = caption
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/sendPhoto", json=payload)
            response.raise_for_status()
            return response.json()

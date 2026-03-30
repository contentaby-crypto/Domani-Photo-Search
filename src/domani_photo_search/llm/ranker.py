from __future__ import annotations

import json

from domani_photo_search.config.settings import settings

RANKER_INSTRUCTIONS = """
Ты ранжируешь shortlist фотографий интерьеров.
Запрещено придумывать новые photo_id, URL, объекты или теги.
Разрешено только: выбрать до top_n фото из входного shortlist, переставить их по релевантности и кратко объяснить выбор.
Если уверенного совпадения нет, верни пустой массив ranked_items и reason=no_confident_match.
Ответ только JSON.
""".strip()


class RankingService:
    def __init__(self) -> None:
        self.enabled = settings.enable_llm_ranking and bool(settings.openai_api_key)
        if self.enabled:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_sec)
        else:
            self.client = None

    def _fallback(self, request_id: str, model: str, shortlist: list[dict], top_n: int, reason: str) -> dict:
        ranked = [
            {"photo_id": item["photo_id"], "rank": idx + 1, "reason": "Deterministic fallback ranking by score_det."}
            for idx, item in enumerate(sorted(shortlist, key=lambda x: (-x.get("score_det", 0), x["photo_id"]))[:top_n])
        ]
        return {"request_id": request_id, "model": model, "ranked_items": ranked, "safe_to_show": True, "reason": reason}

    def rank(self, request_id: str, query_text: str, normalized_query: dict, shortlist: list[dict], top_n: int, model: str | None = None) -> dict:
        model = model or settings.openai_model
        if not shortlist:
            return {"request_id": request_id, "model": model, "ranked_items": [], "safe_to_show": True, "reason": "no_confident_match"}
        if not self.enabled:
            return self._fallback(request_id, model, shortlist, top_n, "llm_disabled_fallback")

        try:
            response = self.client.responses.create(
                model=model,
                instructions=RANKER_INSTRUCTIONS,
                input=[{
                    "role": "user",
                    "content": json.dumps({
                        "query_text": query_text,
                        "normalized_query": normalized_query,
                        "top_n": top_n,
                        "shortlist": shortlist,
                    }, ensure_ascii=False),
                }],
            )
            raw = response.output_text.strip()
            payload = json.loads(raw)
        except Exception:
            return self._fallback(request_id, model, shortlist, top_n, "llm_error_fallback")

        shortlist_ids = {item["photo_id"] for item in shortlist}
        for item in payload.get("ranked_items", []):
            if item.get("photo_id") not in shortlist_ids:
                return {"request_id": request_id, "model": model, "ranked_items": [], "safe_to_show": False, "reason": "ranking_mismatch"}

        payload["request_id"] = request_id
        payload["model"] = model
        payload.setdefault("safe_to_show", True)
        payload.setdefault("ranked_items", [])
        return payload

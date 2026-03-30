from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from domani_photo_search.models.photo import PhotoCard
from domani_photo_search.search.normalizer import QueryNormalizer
from domani_photo_search.utils.io import read_jsonl
from domani_photo_search.utils.text import normalize_text

WEIGHTS = {
    "object": 10,
    "main_object": 7,
    "secondary_object": 3,
    "color": 5,
    "color_group": 3,
    "style": 4,
    "material": 3,
    "plan": 2,
    "format": 2,
    "composition": 2,
}


class SearchEngine:
    def __init__(self, index_path: Path, dictionaries_path: Path | None = None):
        self.index_path = index_path
        self.normalizer = QueryNormalizer(dictionaries_path)
        self.cards = [PhotoCard(**row) for row in read_jsonl(index_path)]

    def health(self) -> dict:
        return {"photos_loaded": len(self.cards), "index_path": str(self.index_path)}

    def _matches_object(self, card: PhotoCard, obj: str) -> bool:
        corpus = [card.object_canonical, *card.object_aliases, card.object_display]
        corpus_text = " | ".join(normalize_text(v) for v in corpus if v)
        return obj in corpus_text

    def search(self, query_text: str, top_k: int = 50) -> dict:
        normalized = self.normalizer.normalize(query_text)
        candidates = []
        matched_dicts = set()
        hard_filters = []
        scoring_terms = []

        for card in self.cards:
            score = 0
            if normalized.objects:
                if not all(self._matches_object(card, obj) for obj in normalized.objects):
                    continue
                score += WEIGHTS["object"] * len(normalized.objects)
                matched_dicts.add("object_aliases")
                hard_filters.extend([f"object={obj}" for obj in normalized.objects])

            for room in normalized.room_objects:
                if room in card.main_objects:
                    score += WEIGHTS["main_object"]
                    matched_dicts.add("room_object_dict")
                    scoring_terms.append(room)
                elif room in card.secondary_objects:
                    score += WEIGHTS["secondary_object"]
                    matched_dicts.add("room_object_dict")
                    scoring_terms.append(room)

            for color in normalized.colors:
                if color in card.colors:
                    score += WEIGHTS["color"]
                    matched_dicts.add("color_dict")
                    scoring_terms.append(color)
            for group in normalized.color_groups:
                if group in card.color_groups:
                    score += WEIGHTS["color_group"]
                    matched_dicts.add("color_dict")
                    scoring_terms.append(group)
            for style in normalized.style:
                if style in card.style:
                    score += WEIGHTS["style"]
                    matched_dicts.add("style_dict")
                    scoring_terms.append(style)
            for material in normalized.material:
                if material in card.material:
                    score += WEIGHTS["material"]
                    matched_dicts.add("material_dict")
                    scoring_terms.append(material)
            for plan in normalized.plan:
                if plan == card.plan:
                    score += WEIGHTS["plan"]
                    matched_dicts.add("plan_dict")
                    scoring_terms.append(plan)
            for fmt in normalized.format:
                if fmt == card.format:
                    score += WEIGHTS["format"]
                    matched_dicts.add("format_dict")
                    scoring_terms.append(fmt)
            for composition in normalized.composition:
                if composition in card.composition:
                    score += WEIGHTS["composition"]
                    matched_dicts.add("composition_dict")
                    scoring_terms.append(composition)

            if score > 0 or normalized.objects:
                candidates.append((score, card))

        candidates.sort(key=lambda item: (-item[0], item[1].photo_id))
        shortlist = [
            {
                "photo_id": card.photo_id,
                "score_det": score,
                "file_name": card.file_name,
                "object_display": card.object_display,
                "object": card.object_display,
                "main_objects": card.main_objects,
                "secondary_objects": card.secondary_objects,
                "colors": card.colors,
                "style": card.style,
                "plan": card.plan,
                "format": card.format,
                "composition": card.composition,
                "material": card.material,
                "preview_url": card.preview_url,
                "url": card.preview_url,
            }
            for score, card in candidates[:top_k]
        ]
        total = len(shortlist)
        if total == 0:
            mode = "not_found"
            action = {
                "text": "Совпадений не найдено. Попробуйте указать объект, комнату, цвет или стиль.",
                "suggestions": ["DEPO, кухня", "Japandi, гостиная", "крупный план, шпон"],
            }
        elif total <= 10:
            mode = "direct"
            action = None
        else:
            mode = "ask_user"
            action = {
                "text": f"Найдено {total} фото. Уточнить запрос или прислать все?",
                "buttons": [
                    {"action": "send_all", "title": "Прислать найденное"},
                    {"action": "refine", "title": "Уточнить запрос"},
                ],
            }
        return {
            "request_id": "",
            "query_text": query_text,
            "normalized_query": normalized.to_dict(),
            "candidates_total": len(candidates),
            "shortlist_total": total,
            "delivery_mode": mode,
            "prompt_user_action": action,
            "shortlist": shortlist,
            "trace": {
                "timestamp": datetime.now(UTC).isoformat(),
                "matched_dictionaries": sorted(matched_dicts),
                "hard_filters": list(dict.fromkeys(hard_filters)),
                "scoring_terms": list(dict.fromkeys(scoring_terms)),
            },
        }

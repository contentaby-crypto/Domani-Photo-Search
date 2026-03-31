from __future__ import annotations

import hashlib
import re
from typing import Iterable

STOP_WORDS = {
    "найди", "покажи", "нужен", "нужна", "нужно", "хочу", "фото", "картинка",
    "была", "был", "были", "где", "мне", "пожалуйста", "покажите", "надо",
    "нужны", "есть", "покаж",
}

TOKEN_CANONICALS = {
    "кухню": "кухня", "кухни": "кухня", "кухне": "кухня",
    "гостиной": "гостиная", "гостиную": "гостиная",
    "спальне": "спальня", "спальню": "спальня",
    "игнатьева": "игнатьев", "игнатьеву": "игнатьев",
    "игнатьевым": "игнатьев", "игнатьеве": "игнатьев",
    "игнатьевского": "игнатьев",
    "серую": "серый", "серой": "серый", "серые": "серый",
    "бежевые": "бежевый", "бежевую": "бежевый", "бежевой": "бежевый",
    "бежевых": "бежевый",
    "коричневые": "коричневый", "коричневую": "коричневый",
    "темное": "темный", "темные": "темный", "тёмное": "темный", "тёмные": "темный",
    "темная": "темный", "темную": "темный",
    "светлые": "светлый", "светлое": "светлый",
    "светлая": "светлый", "светлую": "светлый",
    "деревянная": "дерево", "деревянный": "дерево", "деревянные": "дерево",
    "мраморная": "мрамор", "мраморный": "мрамор", "мраморные": "мрамор",
    "латунная": "латунь", "латунный": "латунь", "латунные": "латунь",
    "дерева": "дерево",
    "кадры": "кадр", "кадрах": "кадр",
    "вертикальные": "вертикальный", "горизонтальные": "горизонтальный",
    "крупным": "крупный", "крупного": "крупный",
    "тв": "телевизор", "tv": "телевизор",
}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = value.strip().lower().replace("ё", "е")
    text = re.sub(r"[^\w\s\-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_csv_tags(value: str | None) -> list[str]:
    text = value or ""
    parts = [normalize_text(p) for p in re.split(r",|;", text)]
    return [p for p in parts if p and p != "nan"]


def generate_photo_id(seed: str, index: int) -> str:
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
    return f"PH-{index:06d}-{digest}"


def slugify_object(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"^\d+\.?\s*", "", text)
    return text.strip()


def make_search_text(parts: Iterable[str]) -> str:
    cleaned = [normalize_text(p) for p in parts if p]
    return " | ".join([p for p in cleaned if p])


def canonicalize_token(token: str) -> str:
    token = normalize_text(token)
    return TOKEN_CANONICALS.get(token, token)


def tokenize(text: str) -> list[str]:
    norm = normalize_text(text)
    if not norm:
        return []
    tokens = [canonicalize_token(tok) for tok in norm.split()]
    return [tok for tok in tokens if tok and tok not in STOP_WORDS]


def ngrams(tokens: list[str], max_n: int = 3) -> list[str]:
    grams: list[str] = []
    for n in range(1, max_n + 1):
        for i in range(len(tokens) - n + 1):
            grams.append(" ".join(tokens[i : i + n]))
    return grams

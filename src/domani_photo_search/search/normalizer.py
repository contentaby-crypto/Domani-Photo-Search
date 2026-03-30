from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from domani_photo_search.dictionaries.loader import DictionaryStore
from domani_photo_search.utils.text import ngrams, normalize_text, tokenize

PLAN_VALUES = {"общий", "средний", "крупный"}
FORMAT_VALUES = {"вертикальный", "горизонтальный", "квадрат"}
MATERIAL_ALIASES = {"дерево": "шпон", "деревянная поверхность": "шпон", "шпон": "шпон", "мрамор": "мрамор", "латунь": "латунь", "камень": "камень"}
COLOR_GROUP_ALIASES = {"светлый": "светлые", "темный": "темные", "светлые тона": "светлые", "темные тона": "темные"}
BASE_COLOR_ALIASES = {"серый": "серый", "бежевый": "бежевый", "коричневый": "коричневый", "черный": "черный", "чёрный": "черный", "терракотовый": "терракотовый", "графитовый": "серый", "кремовый": "бежевый"}


@dataclass
class NormalizedQuery:
    objects: list[str] = field(default_factory=list)
    room_objects: list[str] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)
    color_groups: list[str] = field(default_factory=list)
    style: list[str] = field(default_factory=list)
    plan: list[str] = field(default_factory=list)
    format: list[str] = field(default_factory=list)
    composition: list[str] = field(default_factory=list)
    material: list[str] = field(default_factory=list)
    unknown_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return self.__dict__.copy()


class QueryNormalizer:
    def __init__(self, dictionaries_path: Path | None = None):
        self.store = DictionaryStore.from_dir(dictionaries_path) if dictionaries_path else DictionaryStore()

    def _resolve(self, gram: str, mapping: dict[str, str]) -> str | None:
        gram = normalize_text(gram)
        return mapping.get(gram)

    def normalize(self, query_text: str) -> NormalizedQuery:
        tokens = tokenize(query_text)
        grams = list(dict.fromkeys(ngrams(tokens, max_n=3)))
        result = NormalizedQuery()
        matched_grams: set[str] = set()

        for gram in grams:
            if canonical := self._resolve(gram, self.store.object_aliases):
                result.objects.append(canonical)
                matched_grams.add(gram)
                continue
            if canonical := self._resolve(gram, self.store.room_object_aliases):
                result.room_objects.append(canonical)
                matched_grams.add(gram)
                continue
            if canonical := self._resolve(gram, self.store.color_aliases):
                result.colors.append(canonical)
                result.color_groups.extend(self.store.color_groups_by_color.get(canonical, []))
                matched_grams.add(gram)
                continue
            if canonical := self._resolve(gram, self.store.style_aliases):
                result.style.append(canonical)
                matched_grams.add(gram)
                continue
            if canonical := self._resolve(gram, self.store.composition_aliases):
                result.composition.append(canonical)
                matched_grams.add(gram)
                continue
            if gram in COLOR_GROUP_ALIASES:
                result.color_groups.append(COLOR_GROUP_ALIASES[gram])
                matched_grams.add(gram)
                continue
            if gram in MATERIAL_ALIASES:
                result.material.append(MATERIAL_ALIASES[gram])
                matched_grams.add(gram)
                continue
            if gram in PLAN_VALUES:
                result.plan.append(gram)
                matched_grams.add(gram)
                continue
            if gram in FORMAT_VALUES:
                result.format.append(gram)
                matched_grams.add(gram)
                continue

        matched_tokens = set()
        for gram in matched_grams:
            matched_tokens.update(gram.split())

        for token in tokens:
            if token in matched_tokens:
                continue
            if canonical := self.store.object_aliases.get(token):
                result.objects.append(canonical)
            elif canonical := self.store.room_object_aliases.get(token):
                result.room_objects.append(canonical)
            elif canonical := self.store.color_aliases.get(token):
                result.colors.append(canonical)
                result.color_groups.extend(self.store.color_groups_by_color.get(canonical, []))
            elif token in BASE_COLOR_ALIASES:
                canonical = BASE_COLOR_ALIASES[token]
                result.colors.append(canonical)
                result.color_groups.extend(self.store.color_groups_by_color.get(canonical, []))
            elif canonical := self.store.style_aliases.get(token):
                result.style.append(canonical)
            elif canonical := self.store.composition_aliases.get(token):
                result.composition.append(canonical)
            elif token in MATERIAL_ALIASES:
                result.material.append(MATERIAL_ALIASES[token])
            elif token in COLOR_GROUP_ALIASES:
                result.color_groups.append(COLOR_GROUP_ALIASES[token])
            elif token in PLAN_VALUES:
                result.plan.append(token)
            elif token in FORMAT_VALUES:
                result.format.append(token)
            elif token not in {"на", "в", "у", "с", "для", "и"}:
                result.unknown_terms.append(token)

        for field_name in result.__dict__.keys():
            values = list(dict.fromkeys(getattr(result, field_name)))
            setattr(result, field_name, values)
        return result

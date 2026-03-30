from __future__ import annotations

from collections import defaultdict

from domani_photo_search.utils.text import normalize_text, slugify_object, split_csv_tags

COLOR_GROUP_RULES = {
    "светлые": {"светло-бежевый", "бежевый", "кремовый", "слоновая кость", "белый", "молочный", "светлый"},
    "темные": {"темно-коричневый", "коричневый", "черный", "чёрный", "графитовый", "ореховый", "темный"},
    "нейтральные": {"серый", "темно-серый", "светло-серый", "серо-коричневый", "графитовый"},
    "теплые акценты": {"терракотовый", "кирпичный"},
}

STYLE_CANONICAL = {
    "современный минимализм": "минимализм",
    "скандинавский минимализм": "минимализм",
    "индустриальный минимализм": "минимализм",
    "японский минимализм": "japandi",
    "современная неоклассика": "неоклассика",
    "современная классика": "классика",
    "индустриальный лофт": "лофт",
    "современный арт-деко": "арт-деко",
}

COMPOSITION_CANONICAL = {
    "правило третей": "правило третей",
    "фрейминг": "фрейминг",
    "симметрия": "симметрия",
    "симметричная композиция": "симметрия",
    "центральная симметрия": "симметрия",
    "ведущие линии": "ведущие линии",
    "направляющие линии": "ведущие линии",
    "отрицательное пространство": "негативное пространство",
    "центровая композиция": "центральная композиция",
    "зеркальное отражение": "отражение",
}

MATERIAL_ALIASES = {
    "дерево": "шпон",
    "деревянная поверхность": "шпон",
    "шпон": "шпон",
    "мрамор": "мрамор",
    "латунь": "латунь",
    "камень": "камень",
    "керамогранит": "камень",
}

ROOM_OBJECT_ALIASES = {
    "кофейный столик": "журнальный столик",
    "тв": "телевизор",
    "tv": "телевизор",
    "кухонная зона": "кухня",
    "диванная группа": "гостиная",
    "остров": "кухонный остров",
}


def color_groups_for(colors: list[str]) -> list[str]:
    groups = set()
    for color in colors:
        color = normalize_text(color)
        for group, values in COLOR_GROUP_RULES.items():
            if color in values:
                groups.add(group)
    return sorted(groups)


def infer_materials(main_objects: list[str], secondary_objects: list[str], colors: list[str]) -> list[str]:
    texts = main_objects + secondary_objects + colors
    found = set()
    for token in texts:
        token = normalize_text(token)
        for alias, canonical in MATERIAL_ALIASES.items():
            if alias in token:
                found.add(canonical)
    return sorted(found)


def canonical_style(value: str) -> str:
    value = normalize_text(value)
    return STYLE_CANONICAL.get(value, value)


def canonical_composition(value: str) -> str:
    value = normalize_text(value)
    return COMPOSITION_CANONICAL.get(value, value)


GENERIC_OBJECT_TOKENS = {"кухня", "дом", "квартира", "офис", "пентхаус", "жк", "фото"}

def object_aliases(display_name: str) -> list[str]:
    canonical = slugify_object(display_name)
    aliases = {canonical}
    tokens = canonical.split()
    if tokens:
        last = tokens[-1]
        if last not in GENERIC_OBJECT_TOKENS and len(last) >= 4:
            aliases.add(last)
        if len(tokens) >= 2:
            tail = " ".join(tokens[-2:])
            if not any(tok in GENERIC_OBJECT_TOKENS for tok in tail.split()):
                aliases.add(tail)
    aliases.add(canonical.replace("квартира ", ""))
    aliases.add(canonical.replace("объект ", ""))
    aliases.add(canonical.replace(" жк", ""))
    aliases.add(canonical.replace(". ", " "))
    return sorted(a.strip() for a in aliases if a and len(a.strip()) >= 2)


def build_dictionaries(rows: list[dict]) -> dict:
    objects = []
    object_seen = {}
    room_objects = defaultdict(set)
    colors = defaultdict(set)
    styles = defaultdict(set)
    compositions = defaultdict(set)

    for row in rows:
        display_name = str(row["Объект/ Папка/ Адреса"])
        canonical = slugify_object(display_name)
        if canonical not in object_seen:
            object_id = f"OBJ-{len(object_seen) + 1:04d}"
            obj = {
                "object_id": object_id,
                "canonical_name": canonical,
                "display_name": display_name,
                "aliases": object_aliases(display_name),
                "is_active": True,
            }
            object_seen[canonical] = obj
            objects.append(obj)

        for item in split_csv_tags(row.get("Главные объекты на фото", "")):
            room_objects[ROOM_OBJECT_ALIASES.get(item, item)].add(item)
        for item in split_csv_tags(row.get("Второстепенные объекты на фото", "")):
            room_objects[ROOM_OBJECT_ALIASES.get(item, item)].add(item)
        for color in split_csv_tags(row.get("Цвета", "")):
            color = normalize_text(color)
            colors[color].add(color)
        for style in split_csv_tags(row.get("Стилистика", "")):
            styles[canonical_style(style)].add(normalize_text(style))
        for comp in split_csv_tags(row.get("Композиционный прием", "")):
            compositions[canonical_composition(comp)].add(normalize_text(comp))

    room_object_items = []
    for key, aliases in sorted(room_objects.items()):
        merged = set(aliases)
        merged.add(key)
        if key in ROOM_OBJECT_ALIASES:
            merged.add(ROOM_OBJECT_ALIASES[key])
        room_object_items.append({"canonical": key, "aliases": sorted(merged)})

    color_items = []
    for color, aliases in sorted(colors.items()):
        color_items.append({
            "canonical_color": color,
            "aliases": sorted(aliases),
            "color_groups": color_groups_for([color]),
        })

    return {
        "objects": objects,
        "room_objects": room_object_items,
        "colors": color_items,
        "styles": [{"canonical": k, "aliases": sorted(v | {k})} for k, v in sorted(styles.items())],
        "compositions": [{"canonical": k, "aliases": sorted(v | {k})} for k, v in sorted(compositions.items())],
    }

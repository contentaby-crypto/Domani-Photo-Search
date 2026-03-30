from __future__ import annotations

from pathlib import Path

import pandas as pd

from domani_photo_search.indexing.dictionary_builder import (
    build_dictionaries,
    canonical_composition,
    canonical_style,
    color_groups_for,
    infer_materials,
)
from domani_photo_search.models.photo import PhotoCard
from domani_photo_search.utils.io import ensure_dir, write_json, write_jsonl
from domani_photo_search.utils.text import generate_photo_id, make_search_text, normalize_text, slugify_object, split_csv_tags

REQUIRED_COLUMNS = [
    "Название файла", "Объект/ Папка/ Адреса", "Главные объекты на фото", "Цвета", "Стилистика",
    "Дата обработки", "URL файла", "Height", "Width", "Второстепенные объекты на фото",
    "Какой план?", "Формат фото?", "Композиционный прием",
]


def ingest_csv(csv_path: Path, output_dir: Path) -> dict:
    ensure_dir(output_dir)
    ensure_dir(output_dir / "dictionaries")
    df = pd.read_csv(csv_path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    rows = df.fillna("").to_dict(orient="records")
    dictionaries = build_dictionaries(rows)
    object_map = {o["canonical_name"]: o for o in dictionaries["objects"]}

    photo_rows = []
    for idx, row in enumerate(rows, start=1):
        file_name = str(row.get("Название файла", "")).strip()
        object_display = str(row.get("Объект/ Папка/ Адреса", "")).strip()
        object_canonical = slugify_object(object_display)
        object_aliases = object_map.get(object_canonical, {}).get("aliases", [object_canonical])
        main_objects = split_csv_tags(row.get("Главные объекты на фото", ""))
        secondary_objects = split_csv_tags(row.get("Второстепенные объекты на фото", ""))
        colors = split_csv_tags(row.get("Цвета", ""))
        style = [canonical_style(s) for s in split_csv_tags(row.get("Стилистика", ""))]
        composition = [canonical_composition(c) for c in split_csv_tags(row.get("Композиционный прием", ""))]
        plan = normalize_text(row.get("Какой план?", ""))
        fmt = normalize_text(row.get("Формат фото?", ""))
        color_groups = color_groups_for(colors)
        materials = infer_materials(main_objects, secondary_objects, colors)
        preview_url = str(row.get("URL файла", "")).strip()
        seed = "|".join([file_name, object_display, preview_url])
        photo_id = generate_photo_id(seed, idx)
        search_text = make_search_text([
            object_display, object_canonical, " ".join(object_aliases),
            " ".join(main_objects), " ".join(secondary_objects),
            " ".join(colors), " ".join(color_groups), " ".join(style),
            plan, fmt, " ".join(composition), " ".join(materials),
        ])
        card = PhotoCard(
            photo_id=photo_id,
            file_name=file_name,
            object_display=object_display,
            object_canonical=object_canonical,
            object_aliases=object_aliases,
            main_objects=main_objects,
            secondary_objects=secondary_objects,
            colors=colors,
            color_groups=color_groups,
            style=style,
            plan=plan,
            format=fmt,
            composition=composition,
            material=materials,
            preview_url=preview_url,
            original_url=preview_url,
            width=int(float(row.get("Width") or 0)),
            height=int(float(row.get("Height") or 0)),
            search_text=search_text,
        )
        photo_rows.append(card.model_dump())

    write_jsonl(output_dir / "photos.jsonl", photo_rows)
    for key in ("objects", "room_objects", "colors", "styles", "compositions"):
        write_json(output_dir / "dictionaries" / f"{key}.json", dictionaries[key])

    return {
        "photos_total": len(photo_rows),
        "objects_total": len(dictionaries["objects"]),
        "output_dir": str(output_dir),
    }

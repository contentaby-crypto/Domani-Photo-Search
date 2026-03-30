from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from domani_photo_search.utils.io import read_json
from domani_photo_search.utils.text import normalize_text


@dataclass
class DictionaryStore:
    object_aliases: dict[str, str] = field(default_factory=dict)
    room_object_aliases: dict[str, str] = field(default_factory=dict)
    color_aliases: dict[str, str] = field(default_factory=dict)
    color_groups_by_color: dict[str, list[str]] = field(default_factory=dict)
    style_aliases: dict[str, str] = field(default_factory=dict)
    composition_aliases: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dir(cls, path: Path) -> "DictionaryStore":
        store = cls()
        if not path.exists():
            return store
        for item in read_json(path / "objects.json") if (path / "objects.json").exists() else []:
            canonical = normalize_text(item["canonical_name"])
            for alias in item.get("aliases", []):
                store.object_aliases[normalize_text(alias)] = canonical
        for item in read_json(path / "room_objects.json") if (path / "room_objects.json").exists() else []:
            canonical = normalize_text(item["canonical"])
            for alias in item.get("aliases", []):
                store.room_object_aliases[normalize_text(alias)] = canonical
        for item in read_json(path / "colors.json") if (path / "colors.json").exists() else []:
            canonical = normalize_text(item["canonical_color"])
            for alias in item.get("aliases", []):
                store.color_aliases[normalize_text(alias)] = canonical
            store.color_groups_by_color[canonical] = [normalize_text(v) for v in item.get("color_groups", [])]
        for item in read_json(path / "styles.json") if (path / "styles.json").exists() else []:
            canonical = normalize_text(item["canonical"])
            for alias in item.get("aliases", []):
                store.style_aliases[normalize_text(alias)] = canonical
        for item in read_json(path / "compositions.json") if (path / "compositions.json").exists() else []:
            canonical = normalize_text(item["canonical"])
            for alias in item.get("aliases", []):
                store.composition_aliases[normalize_text(alias)] = canonical
        return store

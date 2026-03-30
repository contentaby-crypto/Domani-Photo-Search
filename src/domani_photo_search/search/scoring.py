from __future__ import annotations

DEFAULT_SCORING_WEIGHTS: dict[str, int] = {
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


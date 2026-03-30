from __future__ import annotations

from pydantic import BaseModel, Field


class PhotoCard(BaseModel):
    photo_id: str
    file_name: str
    object_display: str
    object_canonical: str
    object_aliases: list[str] = Field(default_factory=list)
    main_objects: list[str] = Field(default_factory=list)
    secondary_objects: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    color_groups: list[str] = Field(default_factory=list)
    style: list[str] = Field(default_factory=list)
    plan: str = ""
    format: str = ""
    composition: list[str] = Field(default_factory=list)
    material: list[str] = Field(default_factory=list)
    preview_url: str = ""
    original_url: str = ""
    width: int = 0
    height: int = 0
    search_text: str = ""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchQueryRequest(BaseModel):
    request_id: str
    session_id: str
    user_id: str
    message_id: str | None = None
    query_text: str
    top_k: int = 50
    llm_top_n: int = 10
    context: dict[str, Any] | None = None


class ConfirmSendAllRequest(BaseModel):
    request_id: str
    session_id: str
    shortlist: list[dict[str, Any]] = Field(default_factory=list)
    batch_size: int = 8


class RefineHintsRequest(BaseModel):
    request_id: str
    session_id: str
    normalized_query: dict[str, Any] = Field(default_factory=dict)


class ReindexRequest(BaseModel):
    csv_path: str | None = None


class RankedShortlistItem(BaseModel):
    photo_id: str
    rank: int
    reason: str


class RankingRequest(BaseModel):
    request_id: str
    query_text: str
    normalized_query: dict[str, Any]
    shortlist: list[dict[str, Any]]
    top_n: int = 10
    model: str = "gpt-5"


class RankingResponse(BaseModel):
    request_id: str
    model: str
    ranked_items: list[RankedShortlistItem]
    safe_to_show: bool = True
    reason: str | None = None

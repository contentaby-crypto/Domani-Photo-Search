from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class QueryHistoryStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS query_history (
                    request_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    user_id TEXT,
                    message_id TEXT,
                    query_text TEXT,
                    normalized_query TEXT,
                    delivery_mode TEXT,
                    shortlist_json TEXT,
                    result_json TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS event_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT,
                    event_type TEXT,
                    payload_json TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_search_result(
        self,
        *,
        request_id: str,
        session_id: str,
        user_id: str,
        message_id: str | None,
        query_text: str,
        normalized_query: dict[str, Any],
        delivery_mode: str,
        shortlist: list[dict[str, Any]],
        result: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO query_history (
                    request_id, session_id, user_id, message_id, query_text,
                    normalized_query, delivery_mode, shortlist_json, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    session_id,
                    user_id,
                    message_id,
                    query_text,
                    json.dumps(normalized_query, ensure_ascii=False),
                    delivery_mode,
                    json.dumps(shortlist, ensure_ascii=False),
                    json.dumps(result, ensure_ascii=False),
                ),
            )

    def get_request(self, request_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT request_id, session_id, user_id, message_id, query_text, normalized_query, delivery_mode, shortlist_json, result_json, created_at FROM query_history WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        if not row:
            return None
        keys = ["request_id", "session_id", "user_id", "message_id", "query_text", "normalized_query", "delivery_mode", "shortlist_json", "result_json", "created_at"]
        data = dict(zip(keys, row, strict=False))
        data["normalized_query"] = json.loads(data["normalized_query"] or "{}")
        data["shortlist"] = json.loads(data.pop("shortlist_json") or "[]")
        data["result"] = json.loads(data.pop("result_json") or "{}")
        return data

    def log_event(self, request_id: str, event_type: str, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO event_history (request_id, event_type, payload_json) VALUES (?, ?, ?)",
                (request_id, event_type, json.dumps(payload, ensure_ascii=False)),
            )

    def get_latest_request_for_session(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT request_id FROM query_history WHERE session_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        if not row:
            return None
        return self.get_request(row[0])

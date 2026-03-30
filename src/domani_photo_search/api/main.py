from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from domani_photo_search.api.routes import router
from domani_photo_search.bot.webhook import router as telegram_router
from domani_photo_search.config.settings import settings
from domani_photo_search.indexing.ingest import ingest_csv
from domani_photo_search.search.engine import SearchEngine
from domani_photo_search.services.history import QueryHistoryStore


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    if not settings.photos_index_path.exists() and settings.csv_source_path:
        ingest_csv(Path(settings.csv_source_path), settings.processed_dir)
    app.state.search_engine = SearchEngine(settings.photos_index_path, settings.dictionaries_path)
    app.state.history_store = QueryHistoryStore(settings.history_db)
    app.include_router(router)
    app.include_router(telegram_router)

    @app.get('/health')
    def health() -> dict:
        return {"status": "ok", **app.state.search_engine.health(), "history_db": str(settings.history_db)}

    return app


app = create_app()

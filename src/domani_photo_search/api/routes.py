from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request

from domani_photo_search.config.settings import settings
from domani_photo_search.indexing.ingest import ingest_csv
from domani_photo_search.llm.ranker import RankingService
from domani_photo_search.models.api import ConfirmSendAllRequest, RankingRequest, RefineHintsRequest, ReindexRequest, SearchQueryRequest
from domani_photo_search.search.engine import SearchEngine

router = APIRouter(tags=["api"])
ranker = RankingService()


@router.post('/v1/search/query')
def search_query(payload: SearchQueryRequest, request: Request):
    query = payload.query_text.strip()
    if not query or len(query) > 500:
        raise HTTPException(status_code=400, detail='invalid_query')
    engine = request.app.state.search_engine
    result = engine.search(query, top_k=payload.top_k)
    result['request_id'] = payload.request_id
    request.app.state.history_store.save_search_result(
        request_id=payload.request_id,
        session_id=payload.session_id,
        user_id=payload.user_id,
        message_id=payload.message_id,
        query_text=payload.query_text,
        normalized_query=result.get('normalized_query', {}),
        delivery_mode=result.get('delivery_mode', ''),
        shortlist=result.get('shortlist', []),
        result=result,
    )
    request.app.state.history_store.log_event(payload.request_id, 'search.query', {'query_text': payload.query_text})
    return result


@router.post('/v1/ranking/rank')
def ranking_rank(payload: RankingRequest, request: Request):
    result = ranker.rank(
        request_id=payload.request_id,
        query_text=payload.query_text,
        normalized_query=payload.normalized_query,
        shortlist=payload.shortlist,
        top_n=payload.top_n,
        model=payload.model,
    )
    request.app.state.history_store.log_event(payload.request_id, 'ranking.rank', {'reason': result.get('reason')})
    if result.get('reason') == 'ranking_mismatch':
        raise HTTPException(status_code=409, detail='ranking_mismatch')
    return result


@router.post('/v1/search/confirm-send-all')
def confirm_send_all(payload: ConfirmSendAllRequest, request: Request):
    batch_size = max(1, min(payload.batch_size, 10))
    shortlist = payload.shortlist
    if not shortlist:
        stored = request.app.state.history_store.get_request(payload.request_id)
        shortlist = stored['shortlist'] if stored else []
    batches = [shortlist[i:i + batch_size] for i in range(0, len(shortlist), batch_size)]
    request.app.state.history_store.log_event(payload.request_id, 'search.confirm_send_all', {'batches_total': len(batches)})
    return {"request_id": payload.request_id, "batches": batches, "batches_total": len(batches)}


@router.post('/v1/search/refine-hints')
def refine_hints(payload: RefineHintsRequest, request: Request):
    normalized = payload.normalized_query
    if not normalized:
        stored = request.app.state.history_store.get_request(payload.request_id)
        normalized = stored['normalized_query'] if stored else {}
    hints = []
    if not normalized.get('objects'):
        hints.append('Уточните объект или фамилию клиента')
    if not normalized.get('room_objects'):
        hints.append('Добавьте комнату или предмет: кухня, гостиная, остров')
    if not normalized.get('colors') and not normalized.get('color_groups'):
        hints.append('Добавьте цвет или группу оттенков')
    if not hints:
        hints.append('Уточните план, формат или композицию')
    request.app.state.history_store.log_event(payload.request_id, 'search.refine_hints', {'hints': hints[:3]})
    return {"request_id": payload.request_id, "hints": hints[:3]}


@router.post('/admin/reindex')
def admin_reindex(payload: ReindexRequest, request: Request, x_admin_token: str | None = Header(default=None)):
    if x_admin_token != settings.admin_api_token:
        raise HTTPException(status_code=401, detail='invalid_admin_token')
    csv_path = Path(payload.csv_path or settings.csv_source_path)
    ingest_csv(csv_path, settings.processed_dir)
    request.app.state.search_engine = SearchEngine(settings.photos_index_path, settings.dictionaries_path)
    return {'status': 'ok', 'reindexed_from': str(csv_path), **request.app.state.search_engine.health()}

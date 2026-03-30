from domani_photo_search.llm.ranker import RankingService


def test_ranking_fallback_when_disabled(monkeypatch):
    monkeypatch.setenv('ENABLE_LLM_RANKING', 'false')
    service = RankingService()
    result = service.rank(
        request_id='r1',
        query_text='depo кухня',
        normalized_query={'objects': ['depo'], 'room_objects': ['кухня']},
        shortlist=[{'photo_id': 'PH-1', 'score_det': 10}, {'photo_id': 'PH-2', 'score_det': 7}],
        top_n=1,
        model='gpt-5',
    )
    assert result['safe_to_show'] is True
    assert result['ranked_items'][0]['photo_id'] == 'PH-1'

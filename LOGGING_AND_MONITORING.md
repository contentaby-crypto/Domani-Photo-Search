# LOGGING_AND_MONITORING

## 1. Назначение

Документ описывает, какие логи, trace и метрики нужны для MVP Domani, чтобы:
- диагностировать ошибки;
- улучшать словари;
- анализировать качество поиска;
- воспроизводить проблемные кейсы.

## 2. Принципы

1. Каждый пользовательский запрос получает `request_id`.
2. Все технические события логируются в JSON.
3. Один и тот же `request_id` проходит через bot, search и ranking.
4. Логи должны быть полезны для дебага, но не содержать лишних секретов.
5. Критически важные шаги должны иметь `duration_ms`.

## 3. Обязательные поля любого лога

| Поле | Описание |
|---|---|
| `timestamp` | Время события |
| `level` | log level |
| `service` | `bot`, `search`, `ranking`, `data` |
| `env` | `dev`, `stage`, `prod` |
| `request_id` | Корреляционный ID |
| `session_id` | ID диалога |
| `event` | Краткое имя события |
| `status` | `ok`, `error`, `fallback` |
| `duration_ms` | Длительность шага, если применимо |

## 4. События, которые нужно логировать

### 4.1 Telegram Bot
- `telegram.update_received`
- `telegram.message_validated`
- `telegram.callback_received`
- `telegram.reply_sent`
- `telegram.media_batch_sent`
- `telegram.reply_failed`

### 4.2 Search
- `search.query_received`
- `search.query_normalized`
- `search.candidates_built`
- `search.shortlist_built`
- `search.not_found`
- `search.completed`

### 4.3 Ranking
- `ranking.request_sent`
- `ranking.response_received`
- `ranking.validation_failed`
- `ranking.fallback_used`
- `ranking.completed`

### 4.4 Data / Index
- `index.build_started`
- `index.build_completed`
- `index.validation_failed`
- `dictionary.loaded`

## 5. Полезная нагрузка для search-логов

В search-событиях нужно сохранять:
- `query_text`
- `normalized_query`
- `matched_dictionaries`
- `hard_filters`
- `scoring_terms`
- `candidates_total`
- `shortlist_total`
- `shortlist_ids`

## 6. Полезная нагрузка для ranking-логов

В ranking-событиях нужно сохранять:
- `model`
- `prompt_version`
- `shortlist_ids`
- `top_n`
- `ranked_ids`
- `validation_status`
- `fallback_reason`

## 7. Полезная нагрузка для Telegram-логов

Сохранять:
- `user_id`
- `message_id`
- `callback_action`
- `delivery_mode`
- `media_batch_size`
- `result_count`

Не сохранять:
- bot token;
- API keys;
- полные бинарные payload;
- чувствительные внутренние секреты.

## 8. Метрики MVP

### Продуктовые
- количество поисковых запросов в день;
- доля `direct`;
- доля `ask_user`;
- доля `not_found`;
- среднее количество результатов;
- топ-10 неизвестных терминов;
- топ-10 неуспешных запросов.

### Технические
- среднее время `search.query`;
- среднее время `ranking.rank`;
- p95 полного ответа;
- число ошибок Telegram API;
- число ошибок OpenAI API;
- число `ranking_mismatch`.

## 9. KPI качества поиска

На MVP полезно считать:
- `% запросов с ручным refine`;
- `% запросов с send_all`;
- `% not_found`;
- `% ranking fallback`;
- долю успешных эталонных тестов.

## 10. Формат лога

Пример:

```json
{
  "timestamp": "2026-03-30T14:10:11Z",
  "level": "INFO",
  "service": "search",
  "env": "prod",
  "request_id": "b6d1c769-0b73-4c91-b6c9-7a1eb4438d11",
  "session_id": "tg-59300211",
  "event": "search.completed",
  "status": "ok",
  "duration_ms": 742,
  "query_text": "Найди серую кухню. Была на квартире у Игнатьева",
  "normalized_query": {
    "objects": ["игнатьев"],
    "room_objects": ["кухня"],
    "colors": ["серый"]
  },
  "candidates_total": 18,
  "shortlist_total": 18,
  "shortlist_ids": ["PH-000812", "PH-000834"]
}
```

## 11. Error logging

Ошибки нужно логировать с:
- `error_type`
- `error_message`
- `stack_trace` (в dev/stage)
- `request_id`

### Категории ошибок
- `invalid_query`
- `telegram_api_error`
- `openai_api_error`
- `ranking_mismatch`
- `index_not_loaded`
- `media_unavailable`

## 12. Monitoring MVP

Минимально нужны:
- health endpoint;
- метрики по времени ответа;
- алерт на всплеск 5xx;
- алерт на рост `ranking_mismatch`;
- алерт на проблемы отправки медиа.

## 13. Retention

Рекомендуемый минимум:
- application logs: 30 дней;
- audit logs по поиску: 60–90 дней;
- aggregated metrics: 180 дней.

## 14. Что анализировать еженедельно

1. Какие unknown terms чаще всего встречаются.
2. Какие объекты ищут чаще всего.
3. Где слишком много `ask_user`.
4. Где пользователи жмут `send_all`, а не уточняют.
5. На каких кейсах ranking чаще уходит в fallback.

## 15. Границы MVP

На MVP допустимо:
- хранить JSON-логи на диске или в стандартной log-system;
- считать метрики простым счетчиком;
- не внедрять полноценный distributed tracing.

Но структура логов должна быть такой, чтобы потом безболезненно подключить более зрелый monitoring stack.

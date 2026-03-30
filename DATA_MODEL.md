# DATA_MODEL

## 1. Назначение

Документ описывает каноническую модель данных MVP: как хранится карточка фото, нормализованный запрос, shortlist, ranking result и технические артефакты индекса.

## 2. Главные сущности

1. `PhotoCard`
2. `NormalizedPhotoCard`
3. `SearchQuery`
4. `NormalizedQuery`
5. `ShortlistItem`
6. `RankingItem`
7. `SearchTrace`
8. `EventLog`

## 3. PhotoCard — исходная карточка фото

Это минимальная доменная запись, загружаемая из CSV.

### Поля

| Поле | Тип | Обяз. | Описание |
|---|---|---:|---|
| `photo_id` | string | да | Внутренний стабильный ID |
| `file_name` | string | да | Название файла |
| `object_display` | string | да | Название объекта для интерфейса |
| `object_id` | string | да | Канонический ID объекта |
| `main_objects_raw` | list[str] | да | Главные объекты как в базе |
| `secondary_objects_raw` | list[str] | да | Второстепенные объекты |
| `colors_raw` | list[str] | да | Цвета в исходном виде |
| `styles_raw` | list[str] | да | Стили |
| `plan_raw` | string | да | Общий / средний / крупный |
| `format_raw` | string | да | Вертикальный / горизонтальный / квадрат |
| `composition_raw` | list[str] | да | Композиционные приемы |
| `url_file` | string | да | Ссылка на файл |
| `google_file_id` | string \| null | нет | Google ID, если есть |
| `width_px` | int | да | Ширина |
| `height_px` | int | да | Высота |
| `processed_at` | datetime | да | Дата обработки |

## 4. NormalizedPhotoCard

Это индексируемая запись, построенная на основе `PhotoCard` и словарей.

### Поля

| Поле | Тип | Описание |
|---|---|---|
| `photo_id` | string | Стабильный ключ |
| `object_id` | string | Канонический объект |
| `object_aliases` | list[str] | Алиасы объекта |
| `main_objects` | list[str] | Нормализованные главные сущности |
| `secondary_objects` | list[str] | Нормализованные второстепенные сущности |
| `colors` | list[str] | Канонические цвета |
| `color_groups` | list[str] | Светлые / темные / нейтральные и т.п. |
| `styles` | list[str] | Канонические стили |
| `style_families` | list[str] | Style family |
| `plan` | string | Канонический план |
| `format` | string | Канонический формат |
| `composition` | list[str] | Канонические композиции |
| `materials` | list[str] | Выведенные материалы |
| `search_text` | string | Объединенное индексное поле |
| `preview_ref` | string | Рабочая ссылка или media ref |
| `display` | object | Данные для UI |

## 5. Display model

Минимальный набор для показа пользователю:

```json
{
  "photo_id": "PH-000812",
  "file_name": "IMG_4581.jpg",
  "object_display": "81. DEPO Пентхаус",
  "main_objects": ["кухонный остров", "смеситель"],
  "colors": ["серый", "бежевый"],
  "preview_url": "https://..."
}
```

## 6. SearchQuery

Вход пользователя и transport-метаданные.

| Поле | Тип | Описание |
|---|---|---|
| `request_id` | UUID | ID запроса |
| `session_id` | string | Идентификатор диалога |
| `user_id` | string | Telegram user id |
| `message_id` | string \| null | Telegram message id |
| `query_text` | string | Исходный текст |
| `top_k` | int | Размер shortlist |
| `llm_top_n` | int | Сколько карточек вернуть после ranking |
| `context` | dict \| null | Контекст предыдущего поиска |

## 7. NormalizedQuery

Итог работы нормализатора.

```json
{
  "objects": ["игнатьев"],
  "room_objects": ["кухня"],
  "colors": ["серый"],
  "color_groups": [],
  "styles": [],
  "plan": [],
  "format": [],
  "composition": [],
  "materials": [],
  "unknown_terms": []
}
```

### Поля

- `objects: list[str]`
- `room_objects: list[str]`
- `colors: list[str]`
- `color_groups: list[str]`
- `styles: list[str]`
- `plan: list[str]`
- `format: list[str]`
- `composition: list[str]`
- `materials: list[str]`
- `unknown_terms: list[str]`

## 8. ShortlistItem

Карточка-кандидат после детерминированного поиска.

| Поле | Тип | Описание |
|---|---|---|
| `photo_id` | string | ID карточки |
| `score_det` | float | Детерминированный score |
| `matched_fields` | list[str] | Какие поля совпали |
| `match_explain` | list[str] | Краткое объяснение |
| `display_card` | object | UI-данные |
| `ranking_payload` | object | Сжатые данные для LLM |

## 9. RankingItem

Ответ ranking-сервиса.

| Поле | Тип | Описание |
|---|---|---|
| `photo_id` | string | Только из shortlist |
| `rank` | int | Позиция |
| `reason` | string | Объяснение релевантности |
| `confidence` | float \| null | Необязательное поле |

## 10. SearchTrace

Технический артефакт аудита поиска.

| Поле | Тип | Описание |
|---|---|---|
| `matched_dictionaries` | list[str] | Сработавшие словари |
| `hard_filters` | list[str] | Жесткие фильтры |
| `scoring_terms` | list[str] | Термины scoring |
| `candidates_total` | int | Сколько карточек прошло в кандидаты |
| `shortlist_ids` | list[str] | ID shortlist |
| `duration_ms` | int | Время шага |

## 11. EventLog

Единый формат логируемых событий.

| Поле | Тип | Описание |
|---|---|---|
| `timestamp` | datetime | Время события |
| `request_id` | UUID | Корреляция |
| `session_id` | string | Диалог |
| `step` | string | Например, `search.query` |
| `status` | string | `ok`, `error`, `fallback` |
| `payload` | dict | Нормализованный контекст события |

## 12. Производные артефакты индекса

### 12.1 Object registry
Справочник объектов:
- `object_id`
- `display_name`
- `canonical_name`
- `aliases[]`
- `is_active`

### 12.2 Dictionaries
JSON-словари по типам сущностей.

### 12.3 Golden dataset
Набор эталонных запросов и ожидаемых top results.

## 13. Идентификаторы

### photo_id
Формат: `PH-000001`

### object_id
Формат: `OBJ-0001`

### request_id
UUID v4

## 14. Правила валидации модели

### PhotoCard
- `photo_id` обязателен;
- `file_name` не пустой;
- `object_display` не пустой;
- `width_px > 0`, `height_px > 0`;
- должен быть хотя бы один рабочий media reference.

### NormalizedQuery
- все массивы без дублей;
- строки только в lower case;
- неизвестные термины уходят в `unknown_terms`, а не теряются.

### RankingItem
- `photo_id` обязан входить в shortlist;
- `rank` уникален в рамках ответа.

## 15. Рекомендуемые Pydantic-модели

- `PhotoCardModel`
- `NormalizedPhotoCardModel`
- `SearchQueryRequest`
- `SearchQueryResponse`
- `RankRequest`
- `RankResponse`
- `TelegramCallbackPayload`
- `EventLogModel`

## 16. Версионирование схемы

Каждая индексная сборка должна содержать:
- `schema_version`
- `dictionary_version`
- `build_timestamp`
- `source_csv_hash`

Это позволит понимать, какой именно индекс использовался в проде.

# OPENAI_RANKING_PROMPT_SPEC

## 1. Назначение

Документ описывает, как использовать OpenAI для финального ранжирования shortlist в MVP Domani.

LLM применяется только после deterministic shortlist и не является самостоятельным поисковиком по базе.

## 2. Цель LLM-слоя

На вход модель получает:
- исходный запрос пользователя;
- нормализованные сущности;
- shortlist из 1..50 карточек.

На выходе модель должна:
- отсортировать shortlist;
- вернуть top N;
- кратко объяснить релевантность каждой карточки;
- не создавать новых сущностей и `photo_id`.

## 3. Рекомендуемый API-подход

Для новых интеграций использовать **OpenAI Responses API**.

Причины:
- это рекомендуемый API для новых проектов;
- поддерживает структурированные ответы;
- поддерживает ограничение длины ответа через `max_output_tokens`;
- хорошо подходит для JSON output.

## 4. Модель

Базовая модель MVP:
- `gpt-5.4`

Модель задается через env:
- `OPENAI_MODEL=gpt-5.4`

## 5. Роль модели

Модель — это **ranker**, а не retriever.

Она не должна:
- искать по всей базе;
- придумывать фото;
- создавать новые `photo_id`;
- дополнять метаданные карточек;
- пытаться “догадаться”, чего нет во входе.

## 6. Вход в модель

### Обязательные поля
- `query_text`
- `normalized_query`
- `shortlist`
- `top_n`

### Формат shortlist
В prompt передавать только сжатые данные:

```json
{
  "photo_id": "PH-000812",
  "object": "81. DEPO Пентхаус",
  "main_objects": ["кухонный остров", "смеситель"],
  "secondary_objects": ["барный стул"],
  "colors": ["серый", "бежевый"],
  "styles": ["japandi"],
  "plan": "средний",
  "format": "вертикальный",
  "composition": ["симметрия"]
}
```

Не передавать в LLM избыточные поля:
- raw CSV строки;
- большие URL;
- бинарные данные;
- полные user/session metadata.

## 7. Выход модели

Только JSON-структура:

```json
{
  "ranked_items": [
    {
      "photo_id": "PH-000812",
      "rank": 1,
      "reason": "Совпадают объект, кухня и серые оттенки."
    }
  ],
  "safe_to_show": true,
  "reason": null
}
```

### Возможный fallback
Если модель не уверена:
```json
{
  "ranked_items": [],
  "safe_to_show": true,
  "reason": "no_confident_match"
}
```

## 8. Жесткие правила prompt'а

1. Используй только карточки из входного shortlist.
2. Не создавай новые `photo_id`.
3. Не выдумывай объекты, стили, цвета и помещения.
4. Возвращай только JSON, без markdown.
5. Сортируй по степени совпадения с пользовательским запросом.
6. Если объект указан явно — это самый сильный сигнал.
7. Если совпадение слабое, ранжируй ниже или не включай в top N.
8. Если подходящих карточек нет — верни пустой список.

## 9. Приоритеты релевантности

При ранжировании использовать тот же общий порядок важности, что и в deterministic scoring:
1. объект / alias объекта;
2. помещение / главный объект;
3. цвет;
4. стиль;
5. второстепенные объекты;
6. план / формат / композиция.

## 10. Prompt architecture

### system prompt
Фиксирует:
- роль модели;
- запрет придумывать новые карточки;
- запрет выходить за рамки shortlist;
- обязательный JSON output.

### developer prompt
Фиксирует:
- правила ранжирования;
- логику приоритетов;
- формат объяснений;
- что делать при низкой уверенности.

### user input
Содержит:
- query_text
- normalized_query
- shortlist
- top_n

## 11. Пример system prompt

```text
You rank image metadata for a Telegram search bot.
You are not a search engine over the whole database.
You must use only the provided shortlist.
Never invent new photo_id values, objects, colors, styles, or URLs.
Return only valid JSON matching the response schema.
If no item is confidently relevant, return an empty ranked_items array.
```

## 12. Пример developer prompt

```text
Rank the shortlist by how well each photo matches the user's original request.

Priorities:
1. exact object match
2. room or main object match
3. color match
4. style match
5. secondary object match
6. plan / format / composition

Rules:
- ranked_items must contain only photo_id values present in the shortlist
- use concise Russian explanations
- do not mention fields that are absent in the item
- do not fabricate confidence
- if the query is broad, still prefer the most specific matches
```

## 13. Структурированный ответ

Рекомендуется использовать JSON schema validation в коде.

### Поля ответа
- `ranked_items[].photo_id: string`
- `ranked_items[].rank: integer`
- `ranked_items[].reason: string`
- `safe_to_show: boolean`
- `reason: string | null`

## 14. Validation после ответа модели

Код обязан проверить:
1. все `photo_id` принадлежат shortlist;
2. нет дублей `photo_id`;
3. ранги уникальны и идут по порядку;
4. количество элементов не больше `top_n`;
5. ответ валиден как JSON по схеме.

Если проверка не проходит:
- логировать `ranking_mismatch`;
- использовать fallback: deterministic results.

## 15. Параметры запроса к модели

Рекомендуемые значения MVP:
- низкая вариативность;
- короткий ответ;
- ограниченный `max_output_tokens`.

Цель — стабильность и контролируемость, а не креативность.

## 16. Prompt files в репозитории

```text
prompts/
└─ ranking/
   ├─ system.md
   ├─ developer.md
   └─ examples.json
```

## 17. Версионирование prompt'ов

Каждый ranking-response лог должен содержать:
- `prompt_version`
- `model`
- `schema_version`

Это поможет сопоставлять качество выдачи с конкретной версией prompt'а.

# REPO_STRUCTURE

## 1. Назначение

Документ фиксирует рекомендуемую структуру репозитория для MVP, чтобы Codex и команда работали в единой схеме.

## 2. Принципы

- монорепозиторий;
- модульная структура;
- отдельные каталоги для кода, данных, словарей, тестов и инженерной документации;
- все документы этапа 1 хранятся в репозитории как source of truth.

## 3. Рекомендуемое дерево проекта

```text
domani-photo-search/
├─ README.md
├─ AGENTS.md
├─ CONTRIBUTING.md
├─ pyproject.toml
├─ .env.example
├─ .gitignore
├─ Makefile
├─ docs/
│  ├─ business/
│  │  ├─ BA_MVP_REQUIREMENTS.md
│  │  ├─ DICTIONARIES_SPEC.md
│  │  ├─ API_CONTRACT.md
│  │  ├─ TEST_CASES.md
│  │  └─ DATA_ENTRY_REGULATION.md
│  └─ engineering/
│     ├─ ARCHITECTURE.md
│     ├─ REPO_STRUCTURE.md
│     ├─ ENV_SPEC.md
│     ├─ DATA_MODEL.md
│     ├─ TELEGRAM_INTEGRATION_SPEC.md
│     ├─ OPENAI_RANKING_PROMPT_SPEC.md
│     ├─ LOGGING_AND_MONITORING.md
│     ├─ INDEXING_RUNBOOK.md
│     └─ TEST_PLAN.md
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ api/
│  │  ├─ router.py
│  │  ├─ search_endpoints.py
│  │  ├─ ranking_endpoints.py
│  │  └─ health.py
│  ├─ bot/
│  │  ├─ webhook.py
│  │  ├─ handlers.py
│  │  ├─ callbacks.py
│  │  ├─ keyboards.py
│  │  └─ presenters.py
│  ├─ search/
│  │  ├─ normalizer.py
│  │  ├─ tokenizer.py
│  │  ├─ dictionaries.py
│  │  ├─ filters.py
│  │  ├─ scorer.py
│  │  ├─ shortlist.py
│  │  └─ service.py
│  ├─ ranking/
│  │  ├─ client.py
│  │  ├─ prompts.py
│  │  ├─ schema.py
│  │  ├─ validator.py
│  │  └─ service.py
│  ├─ data/
│  │  ├─ loaders.py
│  │  ├─ validators.py
│  │  ├─ index_builder.py
│  │  └─ repositories.py
│  ├─ domain/
│  │  ├─ models.py
│  │  ├─ enums.py
│  │  └─ contracts.py
│  ├─ observability/
│  │  ├─ logging.py
│  │  ├─ metrics.py
│  │  └─ tracing.py
│  └─ utils/
│     ├─ ids.py
│     ├─ hashing.py
│     └─ time.py
├─ prompts/
│  └─ ranking/
│     ├─ system.md
│     ├─ developer.md
│     └─ examples.json
├─ dictionaries/
│  ├─ object_aliases.json
│  ├─ room_object_dict.json
│  ├─ color_dict.json
│  ├─ style_dict.json
│  ├─ plan_dict.json
│  ├─ format_dict.json
│  ├─ composition_dict.json
│  └─ material_dict.json
├─ data/
│  ├─ raw/
│  │  └─ domani_photos.csv
│  ├─ normalized/
│  ├─ index/
│  └─ fixtures/
├─ logs/
│  └─ .gitkeep
├─ scripts/
│  ├─ validate_csv.py
│  ├─ assign_photo_ids.py
│  ├─ build_index.py
│  ├─ smoke_search.py
│  └─ export_golden_dataset.py
└─ tests/
   ├─ unit/
   ├─ integration/
   ├─ contracts/
   ├─ fixtures/
   └─ e2e/
```

## 4. Назначение ключевых файлов

### README.md
Краткий запуск проекта, команды, структура.

### AGENTS.md
Правила для Codex:
- где можно изменять код;
- что нельзя менять без явного задания;
- обязательные команды проверки;
- соглашения по названию файлов и функций.

### CONTRIBUTING.md
Правила для команды:
- workflow веток;
- PR checklist;
- code review;
- тесты перед merge.

### Makefile
Стандартизированные команды:
- `make install`
- `make lint`
- `make test`
- `make run`
- `make reindex`

## 5. Правила размещения кода

1. HTTP endpoints — только в `app/api/`.
2. Telegram logic — только в `app/bot/`.
3. Поисковая логика — только в `app/search/`.
4. OpenAI integration — только в `app/ranking/`.
5. Pydantic domain-модели — только в `app/domain/`.
6. Все prompt templates — только в `prompts/`.
7. Все словари — только в `dictionaries/`.
8. Скрипты разовой подготовки — только в `scripts/`.

## 6. Правила для Codex

- не переносить словари в код хардкодом;
- не смешивать endpoint code и business logic;
- не вызывать Telegram API из search-модуля;
- не вызывать OpenAI API из bot-handlers напрямую;
- не создавать новые каталоги без необходимости;
- использовать существующие Pydantic-схемы, а не дублировать структуры.

## 7. Именование

### Python
- snake_case для модулей и функций;
- PascalCase для классов;
- явные имена: `build_shortlist`, `rank_shortlist`, `validate_ranking_output`.

### Документы
- UPPER_SNAKE_CASE для инженерных спек;
- бизнес-документы можно хранить в readable title.

### ID
- `photo_id`: `PH-000001`
- `object_id`: `OBJ-0001`
- `request_id`: UUID

## 8. Минимальный набор файлов для первого коммита разработки

- `pyproject.toml`
- `.env.example`
- `README.md`
- `AGENTS.md`
- `app/main.py`
- `app/config.py`
- `app/domain/contracts.py`
- `app/search/service.py`
- `app/ranking/service.py`
- `app/bot/webhook.py`
- `tests/unit/test_normalizer.py`

## 9. Запрещенные паттерны

- бизнес-правила внутри webhook handler;
- prompt text внутри Python-кода длинными строками;
- CSV path, bot token и API keys прямо в исходниках;
- ручное формирование JSON-ответов без Pydantic-моделей;
- запись логики shortlist в SQL/ORM без необходимости на MVP.

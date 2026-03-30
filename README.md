# Domani Photo Search MVP

MVP-сервис поиска по фотобазе Domani для Telegram-бота.

## Цель

Система принимает свободный текстовый запрос на русском языке, детерминированно отбирает shortlist по словарям и индексам, а затем использует ChatGPT 5.4 только для финального ранжирования shortlist.

Ключевой принцип проекта:

**deterministic shortlist -> LLM ranking -> Telegram delivery**

## Что входит в bootstrap

- базовая структура репозитория под Codex;
- конфигурация Python-проекта через `pyproject.toml`;
- `.env.example` с обязательными переменными окружения;
- `Makefile` с основными командами разработки;
- папки и заглушки для модулей `bot`, `search`, `llm`, `indexing`, `api`;
- папки для словарей, данных, тестов и скриптов;
- инженерные документы Stage 1.

## Предлагаемый стек

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- aiogram 3
- httpx
- pandas
- rapidfuzz
- orjson
- structlog
- pytest

## Быстрый старт

```bash
cp .env.example .env
make install
make check
make run-api
```

## Основные сценарии

1. Пользователь пишет запрос в Telegram.
2. Бот отправляет текст в Search API.
3. Search API нормализует запрос, считает deterministic score и формирует shortlist.
4. Ranking service вызывает OpenAI только по shortlist.
5. Бот отправляет пользователю top results или предлагает уточнение.

## Telegram callback flow (`send_all` / `refine`)

- При `delivery_mode=ask_user` бот отправляет inline-кнопки с callback в формате `action:request_id:page`.
- В callback `send_all` бот запрашивает `/v1/search/confirm-send-all` и отправляет карточки батчами.
- В callback `refine` бот запрашивает `/v1/search/refine-hints` и показывает подсказки для уточнения.
- Если `request_id` в callback отсутствует, бот использует последний запрос из `QueryHistoryStore` для текущей сессии Telegram.
- Для `delivery_mode=direct` бот пытается вызвать `/v1/ranking/rank`; при любой ошибке ранжирования пользователю отправляются deterministic-результаты из shortlist (authoritative fallback).

## Структура проекта

См. файл `REPO_STRUCTURE.md`.

## Документы проекта

- `ARCHITECTURE.md`
- `DATA_MODEL.md`
- `ENV_SPEC.md`
- `TELEGRAM_INTEGRATION_SPEC.md`
- `OPENAI_RANKING_PROMPT_SPEC.md`
- `LOGGING_AND_MONITORING.md`
- `INDEXING_RUNBOOK.md`
- `TEST_PLAN.md`

## Ограничения MVP

- поиск не делается по всей базе через LLM;
- LLM не может придумывать новые `photo_id`;
- `photo_id` должен быть стабильным внутренним идентификатором;
- при `shortlist_total > 10` бот не отправляет все фото автоматически.

## Следующий шаг после bootstrap

- реализовать ingest CSV;
- собрать normalized dictionaries;
- реализовать deterministic scoring engine;
- подключить Telegram webhook;
- подключить OpenAI ranking с JSON-ответом.

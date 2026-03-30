# Domani Photo Search — Stage 5 hardening & deployment

Stage 5 добавляет production hardening поверх Stage 4:
- Dockerfile и docker-compose для локального запуска;
- GitHub Actions CI;
- SQLite query history для audit trail и callback flow;
- admin reindex endpoint и CLI;
- реальные Telegram callbacks `send_all` и `refine`;
- шаблон ручной валидации top-50 эталонных запросов.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
make ingest
make test
make run-api
```

## Docker

```bash
docker compose up --build
```

## Основные endpoints

- `GET /health`
- `POST /v1/search/query`
- `POST /v1/ranking/rank`
- `POST /v1/search/confirm-send-all`
- `POST /v1/search/refine-hints`
- `POST /admin/reindex`
- `POST /telegram/webhook`

## Query history

Каждый вызов `/v1/search/query` сохраняется в `data/processed/query_history.sqlite3`.
Это используется для audit trail и для Telegram callback действий `send_all/refine`.

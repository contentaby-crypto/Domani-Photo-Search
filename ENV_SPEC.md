# ENV_SPEC

## 1. Назначение

Документ описывает переменные окружения, обязательные для локального запуска, тестирования и деплоя MVP.

## 2. Общие правила

- все секреты передаются только через env;
- `.env` не коммитится;
- в репозитории хранится только `.env.example`;
- приложение должно падать на старте, если отсутствует критичный секрет.

## 3. Обязательные переменные

| Переменная | Обязательна | Пример | Назначение |
|---|---:|---|---|
| `APP_ENV` | да | `dev` | Окружение: `dev`, `stage`, `prod`, `test` |
| `APP_HOST` | да | `0.0.0.0` | Хост сервиса |
| `APP_PORT` | да | `8080` | Порт сервиса |
| `LOG_LEVEL` | да | `INFO` | Уровень логирования |
| `JSON_LOGS` | да | `true` | JSON-формат логов |

## 4. Telegram

| Переменная | Обязательна | Пример | Назначение |
|---|---:|---|---|
| `TELEGRAM_BOT_TOKEN` | да | `123456:ABC...` | Токен Telegram-бота |
| `TELEGRAM_WEBHOOK_SECRET` | да | `domani-secret-2026` | Secret token для webhook |
| `TELEGRAM_WEBHOOK_URL` | да | `https://example.com/webhook/telegram` | Полный внешний URL webhook |
| `TELEGRAM_PARSE_MODE` | нет | `HTML` | Режим форматирования сообщений |
| `TELEGRAM_MEDIA_BATCH_SIZE` | да | `5` | Размер пачки карточек/превью |
| `TELEGRAM_MAX_CAPTION_LEN` | нет | `900` | Ограничение длины подписи |

## 5. OpenAI

| Переменная | Обязательна | Пример | Назначение |
|---|---:|---|---|
| `OPENAI_API_KEY` | да | `sk-...` | Серверный API-ключ |
| `OPENAI_MODEL` | да | `gpt-5.4` | Модель ранжирования |
| `OPENAI_TIMEOUT_SEC` | да | `30` | Таймаут запроса к OpenAI |
| `OPENAI_MAX_OUTPUT_TOKENS` | да | `800` | Ограничение длины ответа |
| `OPENAI_REASONING_EFFORT` | нет | `low` | Настройка reasoning, если используется |
| `OPENAI_VERBOSITY` | нет | `low` | Короткий ответ модели |
| `OPENAI_PROJECT` | нет | `proj_...` | Идентификатор проекта OpenAI |
| `OPENAI_ORG` | нет | `org_...` | Идентификатор организации |

## 6. Данные и индекс

| Переменная | Обязательна | Пример | Назначение |
|---|---:|---|---|
| `RAW_CSV_PATH` | да | `data/raw/domani_photos.csv` | Путь к исходному CSV |
| `NORMALIZED_DATA_DIR` | да | `data/normalized` | Нормализованные артефакты |
| `INDEX_DIR` | да | `data/index` | Индекс поиска |
| `DICTIONARIES_DIR` | да | `dictionaries` | Справочники нормализации |
| `PREVIEW_URL_MODE` | да | `url` | `url` или `google_id` |
| `ALLOW_BROKEN_MEDIA` | нет | `false` | Разрешить ли выдачу карточек без preview |

## 7. Поисковый слой

| Переменная | Обязательна | Пример | Назначение |
|---|---:|---|---|
| `SEARCH_TOP_K_DEFAULT` | да | `50` | Размер shortlist |
| `SEARCH_TOP_K_MAX` | да | `50` | Верхний предел shortlist |
| `SEARCH_LLM_TOP_N_DEFAULT` | да | `10` | Сколько карточек вернуть после ranking |
| `SEARCH_QUERY_MAX_LEN` | да | `500` | Максимальная длина запроса |
| `SEARCH_ENABLE_FUZZY_MATCH` | да | `true` | Разрешить fuzzy alias matching |
| `SEARCH_FUZZY_THRESHOLD` | нет | `88` | Порог fuzzy match |
| `SEARCH_MIN_SCORE` | нет | `1` | Минимальный детерминированный score |

## 8. Observability

| Переменная | Обязательна | Пример | Назначение |
|---|---:|---|---|
| `REQUEST_ID_HEADER` | нет | `X-Request-ID` | Имя заголовка корреляции |
| `LOG_DIR` | нет | `logs` | Каталог для локальных логов |
| `ENABLE_METRICS` | нет | `true` | Включить сбор метрик |
| `METRICS_PORT` | нет | `9090` | Порт метрик |
| `ENABLE_TRACE_LOGS` | нет | `true` | Логирование shortlist/ranking trace |

## 9. Тестирование

| Переменная | Обязательна | Пример | Назначение |
|---|---:|---|---|
| `PYTHON_ENV_FOR_TESTS` | нет | `1` | Маркер test-окружения |
| `TEST_FIXTURES_DIR` | нет | `tests/fixtures` | Путь к фикстурам |
| `DISABLE_EXTERNAL_APIS` | нет | `true` | Запрет на реальные внешние вызовы в тестах |
| `OPENAI_MOCK_MODE` | нет | `true` | Использовать mock ranking client |

## 10. Пример `.env.example`

```env
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8080
LOG_LEVEL=INFO
JSON_LOGS=true

TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_WEBHOOK_URL=https://example.com/webhook/telegram
TELEGRAM_PARSE_MODE=HTML
TELEGRAM_MEDIA_BATCH_SIZE=5

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.4
OPENAI_TIMEOUT_SEC=30
OPENAI_MAX_OUTPUT_TOKENS=800
OPENAI_REASONING_EFFORT=low
OPENAI_VERBOSITY=low

RAW_CSV_PATH=data/raw/domani_photos.csv
NORMALIZED_DATA_DIR=data/normalized
INDEX_DIR=data/index
DICTIONARIES_DIR=dictionaries
PREVIEW_URL_MODE=url

SEARCH_TOP_K_DEFAULT=50
SEARCH_TOP_K_MAX=50
SEARCH_LLM_TOP_N_DEFAULT=10
SEARCH_QUERY_MAX_LEN=500
SEARCH_ENABLE_FUZZY_MATCH=true
SEARCH_FUZZY_THRESHOLD=88

ENABLE_METRICS=true
ENABLE_TRACE_LOGS=true
```

## 11. Правила загрузки конфигурации

1. Использовать `pydantic-settings`.
2. Валидировать env на старте приложения.
3. Для boolean использовать явные значения: `true` / `false`.
4. Не дублировать env-переменные в нескольких модулях.
5. Конфиг должен импортироваться из одного места: `app/config.py`.

## 12. Ошибки конфигурации

Приложение должно завершать запуск с понятной ошибкой, если:
- пустой `TELEGRAM_BOT_TOKEN`;
- пустой `OPENAI_API_KEY`;
- отсутствует `RAW_CSV_PATH`;
- `SEARCH_TOP_K_DEFAULT > SEARCH_TOP_K_MAX`;
- `PREVIEW_URL_MODE` содержит недопустимое значение.

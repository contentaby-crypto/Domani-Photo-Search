# TEST_PLAN

## 1. Назначение

Документ описывает стратегию тестирования MVP Domani: какие уровни тестов нужны, что считается блокером и как подтвердить готовность к пилоту.

## 2. Цели тестирования

- подтвердить корректность нормализации;
- подтвердить стабильность deterministic shortlist;
- подтвердить корректность ranking только внутри shortlist;
- подтвердить корректную работу Telegram-сценариев;
- выявить ошибки в данных и интеграциях до пилота.

## 3. Уровни тестирования

### 3.1 Unit tests
Проверяют отдельные функции:
- tokenizer;
- n-gram extraction;
- alias matching;
- color normalization;
- scoring;
- ranking output validator.

### 3.2 Integration tests
Проверяют связки:
- search service + dictionaries + index;
- bot handlers + search client;
- ranking service + output validation.

### 3.3 Contract tests
Проверяют соответствие внутренним API-контрактам:
- `/v1/search/query`
- `/v1/ranking/rank`
- `/v1/search/confirm-send-all`

### 3.4 E2E / scenario tests
Проверяют пользовательский путь:
- Telegram text → search → ranking → answer;
- Telegram text → ask_user → send_all;
- Telegram text → ask_user → refine.

### 3.5 Smoke tests
Короткий набор проверок после деплоя и после reindex.

## 4. Обязательные test suites

### Suite A. Нормализация
Проверить:
- lower case;
- `ё -> е`;
- устойчивые n-граммы;
- стоп-слова;
- alias-словарь объектов;
- room/object synonyms;
- material extraction.

### Suite B. Deterministic search
Проверить:
- hard filters по объекту;
- scoring by color/style/room;
- shortlist length;
- стабильность порядка shortlist.

### Suite C. Ranking
Проверить:
- LLM получает только shortlist;
- LLM не может вернуть новый `photo_id`;
- fallback работает при mismatch;
- top N не превышает лимит.

### Suite D. Telegram
Проверить:
- `/start`
- обычный текстовый запрос
- ask_user flow
- send_all flow
- refine flow
- обработку ошибок

## 5. Матрица тестов

| Уровень | Что проверяем | Инструмент |
|---|---|---|
| Unit | логика функций | pytest |
| Integration | сервисы и контракты | pytest + test clients |
| Contract | Pydantic/JSON schema | pytest |
| E2E | пользовательские сценарии | pytest + mocks |
| Smoke | быстрые проверки после выката | scripts |

## 6. Минимальный набор критических тестов

### Blocker
1. Неправильная нормализация объекта.
2. Появление в ranking `photo_id` вне shortlist.
3. Потеря контекста после кнопки `Уточнить запрос`.
4. Дубли фото при `send_all`.
5. Падение на валидном пользовательском запросе.
6. Невозможность собрать индекс.

### Major
1. Неправильная группировка цветов.
2. Нестабильный порядок shortlist без изменения данных.
3. Неполный лог `request_id`.
4. Неработающие медиа в карточках.

### Minor
1. Неудачный текст подсказки.
2. Слишком длинный caption.
3. Неполный help-text.

## 7. Эталонные запросы

Взять за основу уже согласованные кейсы и дополнить реальными `photo_id` после первой индексации.

Минимальный golden set:
- `Найди серую кухню`
- `Была на квартире у Игнатьева`
- `Найди серую кухню. Была на квартире у Игнатьева`
- `Покажи Japandi, гостиная, светлые тона`
- `Нужен крупный план дерева на кухне`
- `DEPO вертикальные кадры с симметрией`
- `кухня с островом`
- `кофейный столик в гостиной`
- `фото с тв в спальне`
- `лучшие фото интерьеров`

## 8. Mock policy

В тестах:
- Telegram API должен быть mock/stub;
- OpenAI API должен быть mock/stub;
- CSV и index — через фикстуры;
- сетевые вызовы запрещены по умолчанию.

## 9. Test data

Создать:
- маленький fixture CSV (10–20 строк);
- fixture dictionaries;
- fixture shortlist;
- fixture ranking output;
- golden dataset для сценариев QA.

## 10. Definition of Done для MVP по тестам

MVP считается готовым к пилоту, если:
- все unit tests проходят;
- все contract tests проходят;
- все blocker-кейсы закрыты;
- smoke tests зеленые;
- golden queries подтверждены на актуальном индексе;
- Telegram-сценарии вручную проверены.

## 11. Smoke checklist после деплоя

- [ ] health endpoint отвечает
- [ ] webhook принимает Telegram update
- [ ] search/query работает на тестовом запросе
- [ ] ranking/rank возвращает валидный JSON
- [ ] кнопка send_all работает
- [ ] кнопка refine работает
- [ ] логи содержат request_id
- [ ] медиа отправляются без дублей

## 12. Регрессия после изменения словарей

После любого изменения словарей обязательно прогонять:
1. unit tests нормализации;
2. integration tests поиска;
3. golden queries;
4. smoke search на свежем индексе.

## 13. Результаты тестирования

Рекомендуемый артефакт:
- `test_report.md`
- дата запуска;
- версия индекса;
- версия словарей;
- версия prompt'ов;
- список blocker/major/minor дефектов.

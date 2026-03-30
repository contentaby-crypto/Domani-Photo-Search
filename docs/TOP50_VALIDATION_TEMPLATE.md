# Top-50 validation checklist

Использовать после первой живой индексации.

## Цель
Проверить 50 эталонных запросов на реальной базе и зафиксировать:
- корректность нормализации;
- корректность shortlist;
- отсутствие чужих объектов;
- полезность Telegram-ответа.

## Поля проверки
- request_id
- query_text
- normalized_query_expected
- normalized_query_actual
- shortlist_ok (yes/no)
- top10_ok (yes/no)
- wrong_object_leak (yes/no)
- comments
- action_items

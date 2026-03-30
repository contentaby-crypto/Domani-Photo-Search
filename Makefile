ingest:
	python scripts/ingest_csv.py

reindex:
	python scripts/reindex.py

run-api:
	uvicorn domani_photo_search.api.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -q

compose-up:
	docker compose up --build

PYTHONPATH ?= src

install:
	python -m pip install -e . --no-build-isolation

format:
	python -m compileall -q src tests

lint:
	python -m compileall -q src

verify-imports:
	PYTHONPATH=$(PYTHONPATH) python -c "import domani_photo_search; import domani_photo_search.api.main; import domani_photo_search.search.engine; import domani_photo_search.indexing.ingest; import domani_photo_search.llm.ranker; import domani_photo_search.bot.webhook"

check: lint verify-imports test

ingest:
	python scripts/ingest_csv.py

reindex:
	python scripts/reindex.py

run-api:
	PYTHONPATH=$(PYTHONPATH) uvicorn domani_photo_search.api.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -q

compose-up:
	docker compose up --build

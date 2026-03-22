.PHONY: install bootstrap run test lint

install:
	python -m pip install -r requirements.txt

bootstrap:
	./scripts/bootstrap_env.sh

run:
	python -m app.main --http

test:
	pytest -q

lint:
	ruff check app tests

# ==============================================================================
# Backend Commands (Django Ninja) - Executado no Ambiente do Container
# ==============================================================================
SHELL := /bin/bash
PYTHON := python manage.py

.PHONY: migrate makemigrations superuser shell reqs back-install \
        test test-cov lint mypy format openapi check-backend

migrate:
	$(PYTHON) migrate

makemigrations:
	$(PYTHON) makemigrations

superuser:
	$(PYTHON) createsuperuser

shell:
	$(PYTHON) shell

reqs:
	uv lock
	@echo "✅ uv.lock atualizado no container!"

back-install:
	@if [ -z "$(pkg)" ]; then echo "❌ Erro: Use make back-install pkg=nome"; exit 1; fi
	uv add "$(pkg)"
	@echo "✅ $(pkg) instalado com sucesso."

test:
	uv run pytest -v

test-cov:
	uv run pytest --cov=apps --cov-report=term -v

lint:
	uv run ruff check .

mypy:
	uv run mypy . --show-error-codes --no-color-output

format:
	uv run ruff format .
	uv run ruff check . --fix

openapi:
	$(PYTHON) export_openapi_schema --api config.api.api --output openapi.json --settings=config.settings.development --indent 2
	@echo "✅ Schema OpenAPI exportado para openapi.json dentro do container."

check-backend: lint mypy test openapi
	@echo "✅ Todos os checks do backend passaram com sucesso!"

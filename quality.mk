# ==============================================================================
# Quality, Testing & API Sync (Orval)
# ==============================================================================

.PHONY: openapi orval sync-api test test-cov lint mypy format check-backend check-frontend check-frontend-dev check-landing check-ci check

openapi:
	@echo "📝 Gerando schema OpenAPI a partir do Django Ninja..."
	cd backend && uv run python manage.py export_openapi_schema --api config.api.api --output ../openapi.json --settings=$(DJANGO_SETTINGS_MODULE)
	@echo "✅ openapi.json gerado na raiz do projeto."

orval:
	@echo "📦 Gerando hooks do Orval para o Frontend..."
	cd frontend && npm run generate:api

sync-api: openapi orval
	@echo "🔄 API e Frontend sincronizados com sucesso!"

test:
	$(EXEC_BACK) uv run pytest -v

test-cov:
	$(EXEC_BACK) uv run pytest --cov=apps --cov-report=term -v

lint:
	$(EXEC_BACK) uv run ruff check .

mypy:
	$(EXEC_BACK) uv run mypy . --show-error-codes --no-color-output

format:
	$(EXEC_BACK) uv run ruff format .
	$(EXEC_BACK) uv run ruff check . --fix

check-backend: lint mypy test openapi
	@echo "✅ Pipeline de qualidade do backend passou!"

check-frontend:
	cd frontend && npm ci && npm run lint && npm run type-check && npm test && npm run build
	@echo "✅ Pipeline de qualidade do frontend passou!"

check-frontend-dev:
	cd frontend && npm ci && npm run lint && npm run type-check && npm test
	@echo "✅ Pipeline dev do frontend passou (sem build de produção)! Rode min 1x 'make check-frontend' antes de push."

check-landing:
	cd landing && npm ci && npx astro check && npm run build
	@echo "✅ Pipeline de qualidade da landing page passou!"

check-ci: check-backend check-frontend check-landing
	@echo "✅ Gate local de qualidade completo (backend + frontend + landing)!"

check: check-backend

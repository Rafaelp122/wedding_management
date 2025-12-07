.PHONY: help build up down restart logs shell migrate test clean

# Docker Compose files
COMPOSE_DEV = docker compose -f docker/docker-compose.yml
COMPOSE_LOCAL = docker compose -f docker/docker-compose.local.yml
COMPOSE_PROD = docker compose -f docker/docker-compose.prod.yml

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development (full Docker)
build: ## Build Docker images (dev)
	$(COMPOSE_DEV) build

up: ## Start all services (dev)
	$(COMPOSE_DEV) up -d

down: ## Stop all services (dev)
	$(COMPOSE_DEV) down

restart: down up ## Restart all services (dev)

logs: ## Show logs from all services
	$(COMPOSE_DEV) logs -f

logs-web: ## Show logs from web service
	$(COMPOSE_DEV) logs -f web

logs-celery: ## Show logs from celery worker
	$(COMPOSE_DEV) logs -f celery_worker

shell: ## Open Django shell
	$(COMPOSE_DEV) exec web python manage.py shell

bash: ## Open bash shell in web container
	$(COMPOSE_DEV) exec web bash

migrate: ## Run database migrations
	$(COMPOSE_DEV) exec web python manage.py migrate

makemigrations: ## Create new migrations
	$(COMPOSE_DEV) exec web python manage.py makemigrations

createsuperuser: ## Create a superuser
	$(COMPOSE_DEV) exec web python manage.py createsuperuser

collectstatic: ## Collect static files
	$(COMPOSE_DEV) exec web python manage.py collectstatic --noinput

test: ## Run tests
	$(COMPOSE_DEV) exec web python manage.py test

test-coverage: ## Run tests with coverage
	$(COMPOSE_DEV) exec web pytest --cov=apps --cov-report=html

local-test: ## Run tests locally (fast)
	@bash -c 'source venv/bin/activate && pytest -n auto --tb=short -q'

local-test-verbose: ## Run tests locally with verbose output
	@bash -c 'source venv/bin/activate && pytest -n auto -v'

local-test-coverage: ## Run tests locally with coverage
	@bash -c 'source venv/bin/activate && pytest -n auto --cov=apps --cov-report=html --cov-report=term-missing'

local-test-failed: ## Re-run only failed tests
	@bash -c 'source venv/bin/activate && pytest --lf -n auto -v'

local-test-specific: ## Run specific test (usage: make local-test-specific TEST=apps/users/tests/test_models.py)
	@bash -c 'source venv/bin/activate && pytest $(TEST) -v'

local-test-debug: ## Run tests without parallelism (best for debugging)
	@bash -c 'source venv/bin/activate && pytest -vv --maxfail=1'

clean: ## Remove containers, volumes, and orphans
	$(COMPOSE_DEV) down -v --remove-orphans
	rm -rf htmlcov .coverage

clean-temp: ## Remove temporary files (cache, logs, etc)
	rm -f celerybeat-schedule db.sqlite3
	rm -rf htmlcov/ __pycache__/ staticfiles/ .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

clean-logs: ## Clear log files
	rm -rf logs/*
	mkdir -p logs

clean-all: clean clean-temp ## Complete cleanup (Docker + temp files)

ps: ## Show running containers
	$(COMPOSE_DEV) ps

# Local development (hybrid - db/redis in Docker, Django local)
local-up: ## Start local services (db, redis only)
	$(COMPOSE_LOCAL) up -d

local-down: ## Stop local services
	$(COMPOSE_LOCAL) down

local-ps: ## Show local containers
	$(COMPOSE_LOCAL) ps

local-logs: ## Show logs from local services
	$(COMPOSE_LOCAL) logs -f

runserver: ## Run Django development server locally
	@bash -c 'source venv/bin/activate && python manage.py runserver 0.0.0.0:8000'

local-migrate: ## Run database migrations locally
	@bash -c 'source venv/bin/activate && python manage.py migrate'

local-makemigrations: ## Create new migrations locally
	@bash -c 'source venv/bin/activate && python manage.py makemigrations'

local-shell: ## Open Django shell locally
	@bash -c 'source venv/bin/activate && python manage.py shell'

local-createsuperuser: ## Create superuser locally
	@bash -c 'source venv/bin/activate && python manage.py createsuperuser'

# Production
prod-build: ## Build production images
	$(COMPOSE_PROD) build

prod-up: ## Start production services
	$(COMPOSE_PROD) up -d

prod-down: ## Stop production services
	$(COMPOSE_PROD) down

prod-logs: ## Show production logs
	$(COMPOSE_PROD) logs -f

prod-ps: ## Show production containers
	$(COMPOSE_PROD) ps

# Docker image management
images: ## List Docker images
	@echo "=== Docker Images ==="
	@docker images | grep -E "wedding|REPOSITORY" || docker images

image-size: ## Compare image sizes
	@echo "=== Image Size Comparison ==="
	@echo ""
	@echo "📦 Development (Dockerfile.dev):"
	@docker images wedding_management-web:latest 2>/dev/null | tail -1 | awk '{print "   " $$7 " " $$8}' || echo "   Not built yet"
	@echo ""
	@echo "🚀 Production (Dockerfile):"
	@docker images wedding_management-web:prod 2>/dev/null | tail -1 | awk '{print "   " $$7 " " $$8}' || echo "   Not built yet"
	@echo ""
	@echo "💡 Tip: Production image is ~50% smaller!"

celery-worker: ## Run Celery worker locally
	@bash -c 'source venv/bin/activate && celery -A wedding_management worker --loglevel=info'

celery-beat: ## Run Celery beat locally
	@bash -c 'source venv/bin/activate && celery -A wedding_management beat --loglevel=info'

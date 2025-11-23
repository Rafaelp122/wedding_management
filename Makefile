.PHONY: help build up down restart logs shell migrate test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: down up ## Restart all services

logs: ## Show logs from all services
	docker compose logs -f

logs-web: ## Show logs from web service
	docker compose logs -f web

logs-celery: ## Show logs from celery worker
	docker compose logs -f celery_worker

shell: ## Open Django shell
	docker compose exec web python manage.py shell

bash: ## Open bash shell in web container
	docker compose exec web bash

migrate: ## Run database migrations
	docker compose exec web python manage.py migrate

makemigrations: ## Create new migrations
	docker compose exec web python manage.py makemigrations

createsuperuser: ## Create a superuser
	docker compose exec web python manage.py createsuperuser

collectstatic: ## Collect static files
	docker compose exec web python manage.py collectstatic --noinput

test: ## Run tests
	docker compose exec web python manage.py test

test-coverage: ## Run tests with coverage
	docker compose exec web pytest --cov=apps --cov-report=html

clean: ## Remove containers, volumes, and orphans
	docker compose down -v --remove-orphans
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
	docker compose ps

# Local development (without Docker)
local-up: ## Start local services (db, redis only)
	docker compose -f docker-compose.local.yml up -d

local-down: ## Stop local services
	docker compose -f docker-compose.local.yml down

runserver: ## Run Django development server locally
	python manage.py runserver 0.0.0.0:8000

celery-worker: ## Run Celery worker locally
	celery -A wedding_management worker --loglevel=info

celery-beat: ## Run Celery beat locally
	celery -A wedding_management beat --loglevel=info

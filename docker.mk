# ==============================================================================
# Docker Commands
# ==============================================================================

.PHONY: up dev logs build rebuild frontend-dev frontend-refresh-deps down clean

up:
	@echo "🚀 Iniciando containers..."
	$(DC) up -d
	$(EXEC_BACK) $(PYTHON) migrate
	@echo "✅ Pronto!"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Backend:  http://localhost:8000/api/v1/docs"

dev:
	$(DC) up -d
	$(EXEC_BACK) $(PYTHON) migrate
	$(DC) logs -f

logs:
	$(DC) logs -f

build:
	@echo "🔨 Reconstruindo e iniciando..."
	$(DC) up --build -d
	$(EXEC_BACK) $(PYTHON) migrate

rebuild:
	@echo "⚠️  Destruindo containers, volumes e redes..."
	$(DC) down -v
	@echo "🔨 Reconstruindo do zero..."
	$(DC) up --build -d
	@echo "⏳ Aguardando banco de dados..."
	@until $(DC) exec db pg_isready -U $${DB_USER:-wedding_user} -d $${DB_NAME:-wedding_db} 2>/dev/null; do sleep 2; done
	$(EXEC_BACK) $(PYTHON) migrate
	@echo "✅ Rebuild completo!"

frontend-dev:
	@echo "🔥 Iniciando Vite dev server local (fora do Docker)..."
	@echo "   Frontend: http://localhost:5173"
	@echo "   ⚠️  Requer backend rodando (make up) e node_modules instalados"
	cd frontend && npm run dev

frontend-refresh-deps:
	@echo "♻️  Recriando frontend com node_modules limpo..."
	$(DC) up -d --force-recreate --renew-anon-volumes frontend
	@echo "📦 Sincronizando dependências do frontend no container..."
	$(DC) exec frontend npm install
	@echo "✅ Dependências do frontend sincronizadas com sucesso!"

down:
	$(DC) down

clean:
	$(DC) down -v
	docker system prune -f

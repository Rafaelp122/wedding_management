# ==============================================================================
# Backend Commands (Django Ninja) - Desenvolvimento
# ==============================================================================

.PHONY: migrate makemigrations superuser shell reqs back-install

migrate:
	$(EXEC_BACK) $(PYTHON) migrate

makemigrations:
	$(EXEC_BACK) $(PYTHON) makemigrations

superuser:
	$(EXEC_BACK) $(PYTHON) createsuperuser

shell:
	$(EXEC_BACK) $(PYTHON) shell

reqs:
	$(EXEC_BACK) uv lock
	@echo "✅ uv.lock atualizado no container!"

back-install:
	@if [ -z "$(pkg)" ]; then echo "❌ Erro: Use make back-install pkg=nome"; exit 1; fi
	$(EXEC_BACK) uv add "$(pkg)"
	@echo "✅ $(pkg) instalado. Rode 'make build' se o container não atualizar."

# ==============================================================================
# Produção
# ==============================================================================

.PHONY: prod-build prod-up prod-migrate prod-shell

prod-build:
	@echo "🏗️  Build da imagem de produção..."
	cd backend && docker build --target production --build-arg BUILD_SECRET_KEY=dummy-build-key-not-for-runtime -t wedding-backend:prod .

prod-up:
	@echo "🚀 Iniciando produção (HTTP local, SSL desativado)..."
	@docker rm -f wedding_backend_prod >/dev/null 2>&1 || true
	docker run -d \
		--name wedding_backend_prod \
		--env-file .env \
		-e DJANGO_SETTINGS_MODULE=config.settings.production \
		-e SECURE_SSL_REDIRECT=False \
		-p 8000:8000 \
		wedding-backend:prod

prod-migrate:
	@echo "🔄 Aplicando migrations em produção..."
	docker exec wedding_backend_prod python manage.py migrate

prod-shell:
	docker exec -it wedding_backend_prod python manage.py shell

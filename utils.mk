# ==============================================================================
# Utilities
# ==============================================================================

.PHONY: env-setup secret-key fix-perms

env-setup:
	@if [ ! -f .env ]; then cp .env.example .env; fi

secret-key:
	@python3 generate_secret_key.py

fix-perms:
	sudo chown -R $$USER:$$USER .

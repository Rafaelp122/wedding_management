# How-To: Executando a Suíte de Testes Pytest no Backend

> **Objetivo:** Rodar a suíte completa de testes unitários e de integração no backend.

---

## Executando os Testes

```bash
cd backend
# Executar toda a suíte de testes
uv run pytest

# Executar testes de um aplicativo específico (ex: finances)
uv run pytest apps/finances/

# Executar com relatório de cobertura
uv run pytest --cov=apps
```

# Visão de Arquitetura: Suíte de Testes de Guard-Rails Arquiteturais e Segurança

> **Módulo:** [system-overview](system-overview.md) | [guard-rails-index](../../3-reference/architecture-standards/guard-rails/index.md)
> **Código:** `backend/apps/core/tests/`

---

## 1. Visão Geral

A suíte em `backend/apps/core/tests/` funciona como a **barreira de integridade dinâmica** do sistema. Em vez de testar regras de negócio individuais, esses testes auditam metaprogramaticamente a base de código inteira (`backend/apps/`) durante a execução do `pytest`, garantindo que nenhuma refatoração ou contribuição fira as regras de arquitetura (ADRs) ou introduza vulnerabilidades de segurança.

---

## 2. Especificações dos Guard-Rails

As especificações técnicas dos principais guard-rails estão disponíveis nas notas de referência:

- 🔒 **[tenant-isolation-guard](../../3-reference/architecture-standards/guard-rails/tenant-isolation-guard.md)**: Audita se todas as consultas ORM nos modelos tenants utilizam a filtragem de escopo por empresa (`Company`).
- ⚡ **[atomic-service-audit-guard](../../3-reference/architecture-standards/guard-rails/atomic-service-audit-guard.md)**: Audita funções de mutação em `services.py` validando a presença do decorador `@transaction.atomic`.
- 🔑 **[security-permissions-guard](../../3-reference/architecture-standards/guard-rails/security-permissions-guard.md)**: Testa endpoints e schemas buscando por vazamento de dados sensíveis (`password`, `hash`) e isolamento de permissões.
- 📋 **[guard-rails/index.md](../../3-reference/architecture-standards/guard-rails/index.md)**: MOC com as especificações atômicas dos guard-rails de integridade dinâmica documentados atualmente.

---

## 3. Integração no Pipeline de CI/CD

A suíte é acionada em dois pontos críticos:
- **Localmente:** Via `make check-ci` ou `pytest backend/apps/core/tests/`.
- **Esteira de CI/CD:** Executada automaticamente no GitHub Actions em todo *Pull Request* antes do merge na branch principal.

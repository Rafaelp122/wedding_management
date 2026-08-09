# 🛡️ Especificações Técnicas de Guard-Rails de Integridade e Segurança (MOC)

> **Módulo:** [architecture-standards](../index.md) | [architectural-guard-rails-suite](../../../4-explanation/architecture/architectural-guard-rails-suite.md)
> **Código Backend:** `backend/apps/core/tests/`

---

## Visão Geral

A suíte em `backend/apps/core/tests/` atua como a **barreira dinâmica de integridade** do sistema. Em vez de testar regras de negócio individuais, estes testes auditam a base de código inteira (`backend/apps/`) durante a execução do `pytest`.

Para manter a documentação **atômica e sustentável**, a especificação técnica de cada guard-rail é dividida nas seguintes notas de referência:

---

## 📌 Especificações Atômicas de Guard-Rails

1. 🔒 **[tenant-isolation-guard.md](tenant-isolation-guard.md)** — Auditoria de Isolação Multitenant (`test_tenant_isolation.py`).
2. ⚡ **[atomic-service-audit-guard.md](atomic-service-audit-guard.md)** — Auditoria de Transações em `services.py` (`test_atomic_service_audit.py`).
3. 🔑 **[security-permissions-guard.md](security-permissions-guard.md)** — Auditoria de Segurança, Permissões e Prevenção de Vazamento de Dados (`test_security_audit.py` e `test_sensitive_data_leak.py`).

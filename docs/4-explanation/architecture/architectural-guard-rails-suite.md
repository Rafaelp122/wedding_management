# Visão de Arquitetura: Suíte de Testes de Guard-Rails Arquiteturais e Segurança

> **Módulo:** [core-domain](../domains/core-domain.md) | [system-overview](system-overview.md)
> **Código:** `backend/apps/core/tests/`

---

## Visão Geral

A suíte em `backend/apps/core/tests/` funciona como a **barreira de integridade dinâmica** do sistema. Em vez de testar regras de negócio individuais, esses testes auditam metaprogramaticamente a base de código inteira (`backend/apps/`) durante a execução do `pytest`, garantindo que nenhuma refatoração ou contribuição fira as regras de arquitetura (ADRs) ou introduza vulnerabilidades de segurança.

---

## Os 12 Pilares da Suíte de Integridade

### 1. Isolação Multitenant (`test_tenant_isolation.py`)
- **Objetivo:** Audita se todas as consultas ORM nos modelos tenants utilizam a filtragem de escopo por empresa (`Company`).
- **Garantia:** Impede o vazamento de dados entre empresas (ADR-009 / ADR-016).

### 2. Proteção contra Deleções em Cascata (`test_cascade_delete_safety.py`)
- **Objetivo:** Verifica se chaves estrangeiras financeiras e contratuais utilizam `models.PROTECT` ou `models.SET_NULL`.
- **Garantia:** Impede a perda acidental de histórico contábil ou contratos por deleções `CASCADE`.

### 3. Auditoria de Serviços Atômicos (`test_atomic_service_audit.py`)
- **Objetivo:** Varre as funções de mutação em `services.py` e valida a presença do decorador `@transaction.atomic`.
- **Garantia:** Garante atomicidade transacional e evita inconsistências no banco de dados PostgreSQL em falhas parciais (ADR-011).

### 4. Padronização da API REST (`test_api_architecture.py`)
- **Objetivo:** Valida se todas as rotas Django Ninja declaram obrigatoriamente o atributo `operation_id`.
- **Garantia:** Garante a geração perfeita de SDKs e hooks TypeScript no frontend via Orval sem nomes aleatórios.

### 5. Consistência de Envelopes de Erro (`test_error_envelope_consistency.py`)
- **Objetivo:** Testa se todas as exceções HTTP retornadas pelo backend seguem o schema de erro padronizado (`detail`, `code`, `timestamp`).
- **Garantia:** Mantém a resposta previsível para o interceptor do frontend (ADR-010).

### 6. Prevenção de Vazamento de Dados Sensíveis (`test_sensitive_data_leak.py`)
- **Objetivo:** Inspeciona schemas e respostas de API buscando por campos como `password`, `hash` ou `secret`.
- **Garantia:** Segurança contra exposição indevida de credenciais de usuários ou parceiros.

### 7. Travas de Concorrência & Locks (`test_concurrency_locks.py`)
- **Objetivo:** Simula acessos concorrentes para validar o comportamento de `select_for_update()` em operações críticas.
- **Garantia:** Previne *race conditions* no cálculo de orçamentos e parcelas.

### 8. Padrão de Comentários & Docstrings em PT-BR (`test_commenting_standards.py`)
- **Objetivo:** Audita docstrings de módulos, classes e funções verificando a conformidade com as diretrizes de documentação em português.
- **Garantia:** Mantém a clareza do código empresarial (conforme `COMMENTING_STANDARDS.md`).

### 9. Prevenção de Regressão N+1 & Performance (`test_api_performance.py`, `test_write_performance.py`)
- **Objetivo:** Monitora a quantidade de queries SQL executadas em endpoints de listagem e escrita.
- **Garantia:** Detecta regressões de performance e força o uso de `select_related`, `prefetch_related` ou `Subquery`.

### 10. Integridade de Schemas DTO (`test_schema_integrity.py`)
- **Objetivo:** Valida se schemas Pydantic/Ninja possuem tipagem estrita e sem inconsistências com os campos do modelo.

### 11. Auditoria de Segurança & Permissões (`test_security_audit.py`)
- **Objetivo:** Testa endpoints contra acessos anônimos e requisições de usuários pertencentes a outros tenants.
- **Garantia:** Validação rigorosa de controle de acesso (RBAC).

### 12. Integridade Transacional no PostgreSQL (`test_transactions.py`)
- **Objetivo:** Valida o comportamento de rollback automático de transações quando exceções são disparadas.

---

## Integração no Pipeline de CI/CD

A suíte é acionada em dois pontos críticos:
- **Localmente:** Via `make check-ci` ou `pytest backend/apps/core/tests/`.
- **Esteira de CI/CD:** Executada automaticamente no GitHub Actions em todo *Pull Request* antes do merge na branch principal.

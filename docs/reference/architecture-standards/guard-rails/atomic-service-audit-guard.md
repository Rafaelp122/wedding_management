# Especificação Técnica: Guard-Rail de Auditoria de Serviços Atômicos

> **Módulo:** [guard-rails](index.md) | [service-layer-pattern](../../../architecture/concepts/service-layer-pattern.md)
> **Teste:** `backend/apps/core/tests/test_atomic_service_audit.py`

---

## 1. Visão Geral

O guard-rail **`test_atomic_service_audit.py`** varre metaprogramaticamente os arquivos `services.py` da camada de serviço no backend buscando por funções que realizam gravações ou atualizações no banco de dados.

---

## 2. Garantias do Teste

1. **Decorador `@transaction.atomic`**: Garante que qualquer método de serviço que execute múltiplas operações de escrita no banco de dados esteja encapsulado em `@transaction.atomic` ou `with transaction.atomic():`.
2. **Rollback em Falhas**: Previne registros parciais e inconsistências de dados no PostgreSQL caso ocorram exceções durante a execução do serviço.

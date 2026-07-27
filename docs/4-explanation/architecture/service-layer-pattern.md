# Arquitetura: Padrão Service Layer

> **Módulo:** [service-layer-pattern](service-layer-pattern.md) | [system-overview](system-overview.md)
> **ADR de Referência:** ADR-006

---

## Visão Geral

A Service Layer é o coração das regras de negócio do backend. O Django Ninja atua estritamente como um adaptador de transporte HTTP, delegando toda a orquestração e lógica de domínio para classes e métodos puramente Python em `services.py`.

---

## Fluxo de Execução

```text
HTTP Request -> Django Ninja Router (api.py) -> Service Function (services.py) -> ORM / Domain Model (models.py)
```

---

## Regras Obrigatórias da Service Layer

1. **Assinatura Explicita de Tenant:** Toda função de serviço deve receber a `Company` como primeiro argumento (ex: `def create_expense(company: Company, ...)`).
2. **Validação de Modelo Integrada (`full_clean`):** Conforme a ADR-011, a Service Layer garante que `full_clean()` seja chamado antes de persistir alterações no banco.
3. **Transações Atômicas:** Transações que afetam múltiplas tabelas (ex: criação de despesa com geração automática de parcelas) são envolvidas por `@transaction.atomic`.
4. **Exceções de Domínio:** A camada de serviço lança exceções de validação (`ValidationError` ou exceções customizadas) que são interceptadas e envelopeadas pelo Django Ninja Exception Handler.

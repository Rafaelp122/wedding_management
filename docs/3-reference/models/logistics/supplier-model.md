# Referência do Modelo: Supplier

> **Módulo:** [logistics-domain](../../../4-explanation/domains/logistics-domain.md) | [cnpj-validation-rules](../../../4-explanation/business-rules/logistics/cnpj-validation-rules.md)
> **Código:** `backend/apps/logistics/models/supplier.py`

---

## Estrutura do Modelo `Supplier`

Herda de `TenantModel`. Cadastra fornecedores globais da assessoria.

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `name`: `CharField(max_length=200)` — Razão social / Nome fantasia.
- `cnpj`: `CharField(max_length=18, validators=[cnpj_validator])` — CNPJ único por tenant.
- `email`: `EmailField(blank=True)`.
- `phone`: `CharField(max_length=20, blank=True)`.
- `website`: `URLField(blank=True)`.
- `address`: `CharField(max_length=255, blank=True)`.
- `city`: `CharField(max_length=100, blank=True)`.
- `state`: `CharField(max_length=2, blank=True)`.
- `notes`: `TextField(blank=True)`.
- `is_active`: `BooleanField(default=True)`.

### Properties:
- `full_address`: Formatação amigável do endereço completo.

---
title: "Modelo de Contrato"
domain: logistics
type: model-reference
code: backend/apps/logistics/models/contract.py
tests: backend/apps/logistics/tests/contracts/test_models.py
---

# Referência do Modelo: Contract

> **Módulo:** [logistics-domain](../../../4-explanation/domains/logistics-domain.md) | [contract-parent-child-hierarchy](../../../4-explanation/business-rules/logistics/contract-parent-child-hierarchy.md)
> **Código:** `backend/apps/logistics/models/contract.py`

---

## Estrutura do Modelo `Contract`

Herda de `TenantModel` e `WeddingOwnedMixin`. Representa um contrato de serviço firmado para um casamento.

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `wedding`: `ForeignKey` (`weddings.Wedding`, `on_delete=CASCADE`).
- `supplier`: `ForeignKey` (`logistics.Supplier`, `on_delete=CASCADE`, `related_name="contracts"`).
- `parent`: `ForeignKey('self', null=True, blank=True, on_delete=PROTECT, related_name="addendums")` — Hierarquia pai/filho (Termos Aditivos).
- `name`: `CharField(max_length=200)` — Identificação do contrato.
- `total_amount`: `DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])`.
- `status`: `CharField(max_length=20, choices=StatusChoices, default='DRAFT')`:
  - `DRAFT` ("Rascunho"), `PENDING` ("Pendente"), `SIGNED` ("Assinado"), `CANCELED` ("Cancelado").
- `pdf_file`: `FileField(upload_to=contract_file_path, validators=[FileExtensionValidator(['pdf']), validate_file_size_10mb])`.
- `signed_date`: `DateField(null=True, blank=True)`.
- `expiration_date`: `DateField(null=True, blank=True)`.
- `alert_days_before`: `PositiveIntegerField(default=30)`.
- `notes`: `TextField(blank=True)`.

### Máquina de Estados (`ALLOWED_TRANSITIONS`):
- `DRAFT` -> `PENDING`, `SIGNED`, `CANCELED`
- `PENDING` -> `SIGNED`, `CANCELED`
- `SIGNED` -> `CANCELED`

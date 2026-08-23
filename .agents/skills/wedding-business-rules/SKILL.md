---
name: wedding-business-rules
description: "Validation Prompt for Wedding Management System Business Rules (Finances, Logistics, Scheduler, Weddings). Use when implementing services, validating domain rules, or performing code reviews."
---

# Validation Prompt — Wedding Business Rules

Use this operational checklist when implementing, validating, or reviewing business rules across domain services. Each check links directly to its single source of truth in `docs/`.

---

## 1. Domain: Weddings & Multi-Tenancy

- [ ] **BR-W01 (Completion Status)**: A wedding can only be marked as `CONCLUDED` after the event date has passed. Prevent premature closure. → [wedding-status-lifecycle.md](../../../docs/architecture/business-rules/weddings/wedding-status-lifecycle.md)
- [ ] **BR-W02 (Multi-Tenancy Isolation)**: All access to weddings, categories, suppliers, and items is strictly isolated by tenant `company`. Use `for_tenant(company)`. → [multi-tenancy-strategy.md](../../../docs/architecture/concepts/multi-tenancy-strategy.md)

---

## 2. Domain: Finances

- [ ] **BR-F01 (Installment Integrity / Zero Tolerance)**: Sum of all installment amounts MUST equal the exact total expense value. Last installment absorbs rounding. → [installment-overdue-logic.md](../../../docs/architecture/business-rules/finances/installment-overdue-logic.md)
- [ ] **BR-F02 (Legal Anchor)**: Expenses linked to a contract MUST have an amount identical to the document amount. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F03 (Payment Consistency)**: Installment marked `PAID` requires `paid_date`. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F04 (Budget Monitoring)**: Warn planner if category expenses exceed allocated budget. → [budget-category-distribution.md](../../../docs/architecture/business-rules/finances/budget-category-distribution.md)
- [ ] **BR-F05 (Status Machine)**: PENDING → PAID (with paid_date) or PENDING → OVERDUE (automatic when `due_date < today`). → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F06 (Paid Immutability)**: `PAID` installments cannot change amount or due date directly. Adjustments require reversal or addendum. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F07 (Mandatory Installment)**: Every expense auto-generates at least 1 installment if unassigned. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F08 (Redistribution Guard)**: Installments can only be redistributed if NO installment has been `PAID`. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F09 (Composite Status)**: Expense status (`PENDING`, `PARTIALLY_PAID`, `SETTLED`) is derived dynamically from installments. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F10 (Expense Identification)**: Every expense requires a mandatory `name`. `description` is optional. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **BR-F11 (Unmarking Reversal)**: Paid installments can be unmarked, clearing `paid_date` and returning status to PENDING or OVERDUE. → [financial-integrity-rules.md](../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
- [ ] **Payment Schedule Integration**: Payments auto-generate calendar events. → [payment-schedule-integration.md](../../../docs/architecture/business-rules/finances/payment-schedule-integration.md)

---

## 3. Domain: Logistics & Contracts

- [ ] **BR-L01 (Signed Document Rules)**: Contracts marked `SIGNED` require PDF file upload, value > 0, and signature date. → [contract-state-machine.md](../../../docs/architecture/business-rules/logistics/contract-state-machine.md)
- [ ] **BR-L02 (Cross-Wedding Guard)**: Parent-child contracts, addendums, and items MUST belong to the same wedding. → [contract-parent-child-hierarchy.md](../../../docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md)
- [ ] **BR-L03 (Supplier Sharing)**: Suppliers are linked to the planner and can be reused across multiple weddings. → [contract-state-machine.md](../../../docs/architecture/business-rules/logistics/contract-state-machine.md)
- [ ] **BR-L04 (Acquisition Decoupling)**: Item delivery/acquisition status is independent of payment status. → [contract-state-machine.md](../../../docs/architecture/business-rules/logistics/contract-state-machine.md)
- [ ] **CNPJ Validation**: Supplier CNPJ validation and sanitization rules enforced. → [cnpj-validation-rules.md](../../../docs/architecture/business-rules/logistics/cnpj-validation-rules.md)

---

## 4. Domain: Scheduler

- [ ] **BR-S01 (Read-Only Payment Events)**: `PAYMENT` calendar events are auto-generated and read-only. → [payment-event-readonly-guard.md](../../../docs/architecture/business-rules/scheduler/payment-event-readonly-guard.md)
- [ ] **BR-S02 (Recurrence Engine)**: Recurring task alerts and installment overdue notifications follow standard recurrence schedule. → [recurrence-rules-engine.md](../../../docs/architecture/business-rules/scheduler/recurrence-rules-engine.md)

---

## 5. Cross-Cutting Validation

- [ ] **BR-VAL01 (Decimal for Money)**: All monetary fields MUST use `Decimal` with 2 decimal places. `float` is strictly forbidden.
- [ ] **BR-VAL02 (Future Due Dates)**: New installments/events CANNOT be created with past due dates.

> **Instruction for AI Agent:** If you need deeper architectural context, motivation, or exceptions for any rule above, read the linked atomic note in `docs/` before proceeding with code changes.
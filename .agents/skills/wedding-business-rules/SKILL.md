---
name: wedding-business-rules
description: "Business rules for Wedding Management System — BR-F01 to BR-F11 (finances), BR-L01 to BR-L04 (logistics), BR-S01 to BR-S02 (scheduler), BR-VAL01 to BR-VAL02 (validation). Use when implementing services, writing tests, or reviewing code."
---

# Wedding Business Rules

Business rules centralized here. These rules are technology-agnostic and focus on data integrity and business process consistency.

---

## 1. Domain: Weddings

### BR-W01: Completion Status
- **Rule**: A wedding can only be marked as CONCLUDED after the actual event date has passed.
- **Purpose**: Prevent accidental closure of weddings still in progress.

### BR-W02: Multi-tenancy Data Isolation
- **Rule**: Access to weddings and data is isolated by `company` (tenant). Users of the same company share data; users from different companies cannot access each other's data.
- **Purpose**: Ensure data privacy and security (LGPD compliance).

---

## 2. Domain: Finances

### BR-F01: Installment Integrity (Zero Tolerance)
- **Rule**: The exact sum of all installments must equal the total expense value.
- **Math**: `base_value = total ÷ n` (rounded to 2 decimals). First `n−1` installments = `base_value`. Last installment = `total − (base_value × (n−1))` — absorbs rounding.
- **Example**: R$ 10,000 ÷ 3 → base = 3,333.33 → Installments: 3,333.33, 3,333.33, 3,333.34. Sum = 10,000.00 ✅
- **Purpose**: Absolute precision for accounting audit and bank reconciliation.

### BR-F02: Legal Anchor (Document ↔ Expense)
- **Rule**: When an expense is linked to a reference document (e.g. contract), the expense amount must be identical to the total amount in the document.
- **Purpose**: Maintain consistency between legal commitment and financial execution.

### BR-F03: Payment Consistency
- **Rule**: Every installment marked as PAID must record the payment date. Conversely, installments with a payment date filled must be in PAID status.

### BR-F04: Budget Monitoring
- **Rule**: The system must alert the planner if the sum of expenses in a category exceeds the allocated budget.
- **Note**: Soft warning — does not block the operation.

### BR-F05: Installment Status Transitions
- **Rule**: Lifecycle: PENDING → PAID (when paid) or PENDING → OVERDUE (when due date passes without payment).
- **Conditions**:
  - PENDING → PAID: requires payment date
  - PENDING → OVERDUE: automatic when `due_date < today` and status is PENDING
  - OVERDUE → PAID: allowed (late payment), records payment date

### BR-F06: Paid Installment Immutability
- **Rule**: PAID installments cannot have their value, due date, or number changed.
- **Purpose**: Guarantee accounting integrity. Adjustments must be done via reversal and new installment.

### BR-F07: Mandatory Installment
- **Rule**: Every expense must have at least 1 installment. The system auto-generates 1 installment if none is specified.
- **Default**: `num_installments = 1`, `first_due_date = today`.

### BR-F08: Installment Redistribution
- **Rule**: The number of installments can be changed only if NO installment is PAID. If any is paid, redistribution is blocked.
- **Mechanism**: Deletes all existing installments and regenerates with the new count, recalculating Zero Tolerance (BR-F01) in an atomic transaction.

### BR-F09: Composite Expense Status
- **Rule**: Expense status is derived automatically from its installments:
  - `PENDING`: no installment paid
  - `PARTIALLY_PAID`: at least one paid, but not all
  - `SETTLED`: all installments paid
- **Note**: Computed in real-time via DB annotation (not persisted).

### BR-F10: Expense Identification
- **Rule**: Every expense requires a mandatory `name`. The `description` field is optional.
- **Purpose**: Separate short identification from detailed description.

### BR-F11: Unmarking Paid Installments
- **Rule**: Paid installments can be unmarked (reversed). On unmark:
  - `paid_date` is cleared (null)
  - If `due_date < today` → status returns to OVERDUE
  - Otherwise → status returns to PENDING

---

## 3. Domain: Logistics

### BR-L01: Signed Document Requirements
- **Rule**: Documents marked as SIGNED require:
  1. Upload of file (PDF)
  2. Total value greater than zero
  3. Signature date recorded

### BR-L02: Budget Isolation (Cross-Wedding)
- **Rule**: Logistics items and budget categories cannot be shared between different weddings, even if under the same planner.
- **Cross-Wedding Validation**: Every operation involving `BudgetCategory` must validate the category belongs to the same `wedding` as the related entity.

### BR-L03: Supplier Sharing
- **Rule**: Supplier registration is linked to the planner and can be reused across multiple weddings.

### BR-L04: Acquisition-Payment Decoupling
- **Rule**: Item delivery/acquisition status is independent of payment status. An item can be marked as delivered even with pending installments.

---

## 4. Domain: Scheduler

### BR-S01: Financial Event Automation
- **Rule**: Calendar events of type PAYMENT are auto-generated from financial installments and cannot be manually edited in the calendar.
- **Purpose**: Ensure the schedule faithfully reflects planned cash flow.

### BR-S02: Due Date Reminders
- **Rule**: The system must generate automatic alerts for installments reaching their due date without payment (OVERDUE status).

---

## 5. Cross-Cutting Validation Rules

### BR-VAL01: Decimal for Monetary Values
- **Rule**: All monetary values MUST use fixed decimal precision (2 decimal places). Float is PROHIBITED for money.
- **Purpose**: Ensure accuracy in financial calculations and bank reconciliation.

### BR-VAL02: Future Due Dates
- **Rule**: When creating an installment or event, the due date CANNOT be in the past.
- **Exception**: Allowed when editing existing records for historical correction.

---

## 6. Business Glossary

| Term | Definition |
| :--- | :--- |
| **Zero Tolerance** | Principle that not a single cent can be lost in installment rounding. |
| **Cross-Wedding** | Accidental mixing of data between different weddings — prevented via validation. |
| **Planner** | The wedding planner or company using the system. |
| **Tenant** | Entity that isolates one company's data from another in the database. |
| **OVERDUE** | Installment status when due date has passed without payment. |

---

## 7. References by Domain

### Finances
- **BR-F01**: Zero Tolerance — see ADR-010
- **BR-F02**: Legal Anchor — expense amount = document amount
- **BR-F03**: Payment Consistency — PAID requires date, date requires PAID
- **BR-F04**: Budget Monitoring — soft warning on overspend
- **BR-F05**: Status Transitions — PENDING → PAID or OVERDUE
- **BR-F06**: Paid Installment Immutability — no edits after payment
- **BR-F07**: Mandatory Installment — minimum 1 per expense
- **BR-F08**: Redistribution — only if no PAID installments
- **BR-F09**: Composite Status — derived from installments
- **BR-F10**: Expense Identification — name required, description optional
- **BR-F11**: Unmark Paid — reversal with conditional status

### Logistics
- **BR-L01**: Signed Document Requirements — file, value, date
- **BR-L02**: Cross-Wedding Isolation — no shared categories
- **BR-L03**: Supplier Sharing — reusable across weddings
- **BR-L04**: Acquisition-Payment Decoupling — independent states

### Scheduler
- **BR-S01**: Financial Event Automation — auto-generated from installments
- **BR-S02**: Due Date Reminders — alerts for OVERDUE

### Validation
- **BR-VAL01**: Decimal for Money — never float
- **BR-VAL02**: Future Due Dates — no past dates on create
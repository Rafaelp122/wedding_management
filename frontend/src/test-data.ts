import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import type { TaskOut } from "@/api/generated/v1/models/taskOut";
import type { EventOut } from "@/api/generated/v1/models/eventOut";
import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import type { SupplierFormState } from "@/features/logistics/types";
import { EMPTY_SUPPLIER_FORM_STATE } from "@/features/logistics/types";
import type { DashboardSummaryOut } from "@/api/generated/v1/models/dashboardSummaryOut";
import type { CriticalWeddingOut } from "@/api/generated/v1/models/criticalWeddingOut";
import type { InstallmentOut } from "@/api/generated/v1/models/installmentOut";

export function createMockWedding(overrides?: Partial<WeddingOut>): WeddingOut {
  return {
    uuid: "w-1",
    groom_name: "João Silva",
    bride_name: "Maria Souza",
    date: "2025-06-15",
    location: "São Paulo",
    expected_guests: 150,
    status: "IN_PROGRESS",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
    ...overrides,
  };
}

export function createMockSupplier(
  overrides?: Partial<SupplierOut>,
): SupplierOut {
  return {
    uuid: "s-1",
    name: "Fornecedor Teste",
    cnpj: "12.345.678/0001-90",
    phone: "(11) 99999-0000",
    email: "teste@fornecedor.com",
    is_active: true,
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
    ...overrides,
  };
}

export function createMockExpense(
  overrides?: Partial<ExpenseOut>,
): ExpenseOut {
  return {
    uuid: "e-1",
    wedding: "w-1",
    category: "c-1",
    name: "Buffet Principal",
    estimated_amount: "5000.00",
    actual_amount: "4800.00",
    category_name: "Buffet",
    installments_count: 3,
    paid_installments_count: 1,
    status: "PARTIALLY_PAID",
    ...overrides,
  };
}

export function createMockTask(overrides?: Partial<TaskOut>): TaskOut {
  return {
    uuid: "t-1",
    company_id: "comp-1",
    wedding: "w-1",
    title: "Contratar buffet",
    description: "Pesquisar e fechar contrato",
    due_date: "2025-03-15",
    is_completed: false,
    ...overrides,
  };
}

export function createMockEvent(overrides?: Partial<EventOut>): EventOut {
  return {
    uuid: "ev-1",
    company_id: "comp-1",
    wedding: "w-1",
    title: "Reunião com noivos",
    event_type: "MEETING",
    start_time: "2025-06-15T10:00:00Z",
    location: "Escritório",
    ...overrides,
  };
}

export function createMockBudgetCategory(
  overrides?: Partial<BudgetCategoryOut>,
): BudgetCategoryOut {
  return {
    uuid: "bc-1",
    wedding: "w-1",
    name: "Buffet",
    description: "Comida e bebidas",
    allocated_budget: "5000.00",
    total_spent: "3200.00",
    ...overrides,
  };
}

export function createMockContract(
  overrides?: Partial<ContractOut>,
): ContractOut {
  return {
    uuid: "c-1",
    wedding: "w-1",
    supplier: "supplier-uuid-123",
    total_amount: "5000.00",
    status: "ACTIVE",
    description: "Buffet contrato",
    signed_date: "2025-01-15",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
    ...overrides,
  };
}

export function createMockItem(overrides?: Partial<ItemOut>): ItemOut {
  return {
    uuid: "i-1",
    wedding: "w-1",
    name: "Cadeiras",
    description: "Cadeiras Tiffany",
    quantity: 150,
    acquisition_status: "PENDING",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
    ...overrides,
  };
}

export function createMockSupplierFormState(
  overrides?: Partial<SupplierFormState>,
): SupplierFormState {
  return {
    ...EMPTY_SUPPLIER_FORM_STATE,
    ...overrides,
  };
}

export function createMockDashboardSummary(
  overrides?: Partial<DashboardSummaryOut>,
): DashboardSummaryOut {
  return {
    active_weddings: 12,
    pending_installments_7d: "5000.00",
    events_this_week: 3,
    urgent_tasks_count: 2,
    weddings_this_month: 4,
    critical_weddings: [],
    ...overrides,
  };
}

export function createMockCriticalWedding(
  overrides?: Partial<CriticalWeddingOut>,
): CriticalWeddingOut {
  return {
    uuid: "cw-1",
    groom_name: "João",
    bride_name: "Maria",
    days_until: 45,
    incomplete_tasks: 5,
    pending_installments: 2,
    overdue_tasks: 1,
    overdue_installments: 0,
    ...overrides,
  };
}

export function createMockInstallment(
  overrides?: Partial<InstallmentOut>,
): InstallmentOut {
  const today = new Date();
  const future = new Date(today);
  future.setDate(future.getDate() + 5);
  return {
    uuid: "inst-1",
    wedding: "w-1",
    expense: "e-1",
    installment_number: 1,
    amount: "500.00",
    due_date: future.toISOString().slice(0, 10),
    status: "PENDING",
    ...overrides,
  };
}

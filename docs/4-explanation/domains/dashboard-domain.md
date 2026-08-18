# MOC de Domínio: Dashboard (Painel de Métricas e Operações)

> **Hub de Domínio:** [dashboard-domain](dashboard-domain.md) | [system-overview](../architecture/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/reporting/` & `frontend/src/features/dashboard/`

---

## Visão Geral do Domínio

O domínio de **Dashboard e Reporting** consolida as métricas financeiras, operacionais e de cronograma da plataforma, oferecendo visões tanto no nível da assessoria de eventos quanto no nível de um casamento específico.

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/reporting/`)
- **Query Selectors:**
  - `selectors/dashboard_selectors.py` (`dashboard_summary_selector`, `wedding_overview_selector`) — Agrega KPIs consolidados da empresa e métricas do casamento.
  - `selectors/summaries/financial.py` — Cálculo de gasto total, saldo livre, parcelas pendentes e atrasadas.
  - `selectors/summaries/contract.py` — Status de contratos e fornecedores vinculados.
  - `selectors/summaries/task.py` — Contagem e listagem de tarefas pendentes e urgentes.
- **Service Layer (`services.py`):** Camada reservada para operações analíticas e geração de relatórios (Issue #339).
- **Endpoints (`api.py`):** GET `/api/v1/dashboard/summary/` e GET `/api/v1/dashboard/wedding/{uuid}/`. Veja [openapi-schema](../../3-reference/api/openapi-schema.md).


### 2. Camada de Frontend (`frontend/src/features/dashboard/`)
- **Containers (Smart):**
  - `DashboardPage.tsx` — Conteiner principal da página de Dashboard.
  - `DashboardOperations.tsx` — Conteiner de operações da assessoria (contratos pendentes, tarefas urgentes, próximos casamentos).
  - `WeddingMonthlyChart.tsx` — Conteiner do gráfico financeiro mensal com Recharts.
- **Views (Dumb Presenters):**
  - `DashboardPageView.tsx` — Visão principal do dashboard com alternador de abas e métricas.
  - `StatsCards.tsx` & `WeddingStatsCards.tsx` — Cards de métricas gerais e por casamento.
  - `CriticalWeddings.tsx` — Lista de casamentos com data próxima.
  - `UpcomingAppointments.tsx` & `UpcomingInstallments.tsx` — Listas de reuniões e parcelas a vencer.
  - `WeddingBudgetBreakdown.tsx` — Distribuição visual do orçamento.
- **Hooks Customizados:**
  - `useDashboardData.ts` — Orquestra buscas Orval, calcula saudações e dados derivados.
  - `useDashboardOperations.ts` — Gerencia ações e invalidação de cache do dashboard via TanStack Query.
- **Utilitários:** `chart-helpers.ts` — Funções puras de agregação de dados para gráficos.

---

## Domínios Relacionados
- [weddings-domain](weddings-domain.md) — Gestão de casamentos ativos.
- [finances-domain](finances-domain.md) — Dados orçamentários e parcelamento.
- [scheduler-domain](scheduler-domain.md) — Compromissos e tarefas do cronograma.
- [logistics-domain](logistics-domain.md) — Status de contratos e fornecedores.

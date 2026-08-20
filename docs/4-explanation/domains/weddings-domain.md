# MOC de Domínio: Weddings (Gestão de Casamentos)

> **Hub de Domínio:** [weddings-domain](weddings-domain.md) | [system-overview](../architecture/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/weddings/` & `frontend/src/features/weddings/`

---

## Visão Geral do Domínio

O domínio de **Weddings** é o eixo central da plataforma. Define os casamentos gerenciados por cada assessoria (tenant), o status do planejamento e serve de referência para todos os demais módulos (finanças, logística e cronograma).

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/weddings/`)
- **Modelo de Dados:** [wedding-model](../../3-reference/models/weddings/wedding-model.md) — Entidade `Wedding`.
- **Camadas Arquiteturais:** `services.py` (mutação), `selectors.py` (consultas CQRS) e `api.py` (rotas Django Ninja).


### 2. Camada de Frontend (`frontend/src/features/weddings/`)
- **Páginas (Smart Containers):**
  - `WeddingsListPage.tsx` — Listagem de casamentos da assessoria.
  - `WeddingDetailPage.tsx` — Detalhes do casamento selecionado.
- **Componentes & Orquestradores:**
  - `WeddingHeader.tsx` — Cabeçalho com badge de status e atalhos.
  - `WeddingOverview.tsx` — Visão geral resumida (cards financeiros, próximas tarefas).
  - `WeddingDetailTabs.tsx` — Orquestrador de abas com *lazy loading* de Finanças, Fornecedores e Cronograma.
  - `WeddingsTable.tsx` & `WeddingFilters.tsx` — Tabela e filtros de casamentos.
- **Dialogs de Manutenção:** `CreateWeddingDialog.tsx`, `EditWeddingDialog.tsx`, `DeleteWeddingDialog.tsx`.
- **Estado Global & Hooks:** `useWeddingStore` (`src/stores/weddingStore.ts`), `useWeddingsPage.ts`, `useWeddingDetail.ts`.

---

## Regras de Negócio Associadas
- [wedding-status-lifecycle](../business-rules/weddings/wedding-status-lifecycle.md): Ciclo de vida e transições de status (`IN_PROGRESS` -> `COMPLETED` / `CANCELED`).
- [dashboard-domain](dashboard-domain.md): Agregação de KPIs do Dashboard.

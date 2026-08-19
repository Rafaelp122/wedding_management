# MOC de Domínio: Relatórios & Métricas (Reporting)

> **Hub de Domínio:** [reporting-domain](reporting-domain.md) | [dashboard-domain](dashboard-domain.md) | [system-overview](../architecture/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/reporting/` & `frontend/src/features/reporting/`

---

## Visão Geral do Domínio

O domínio de **Reporting** é responsável pela consolidação, análise, diagramação e exportação de dados operacionais e financeiros da plataforma de casamentos. Ele fornece tanto visualizações em tempo real (painéis agregados) quanto geração de documentos exportáveis de alta fidelidade em **PDF** (via ReportLab) e **Excel** (via openpyxl).

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/reporting/`)

- **Query Selectors (`selectors/`):**
  - `dashboard_selectors.py` (`dashboard_summary_selector`, `wedding_overview_selector`) — Agregação lazy de KPIs consolidados multi-tenant.
  - `selectors/summaries/financial.py` — Cálculos de orçamento, total gasto, parcelas pendentes e atrasadas.
  - `selectors/summaries/contract.py` — Resumo de contratos e fornecedores vinculados.
  - `selectors/summaries/task.py` — Resumo do checklist de tarefas operacionais.
- **Service Layer (`services.py`):**
  - `ReportGenerationService.generate_wedding_pdf` — Diagramação completa de relatório do casamento em PDF (A4) com cabeçalhos, KPIs, tabelas estilizadas e paginação em dois passos (`NumberedCanvas`).
  - `ReportGenerationService.generate_wedding_excel` — Geração de planilha multi-aba (.xlsx) com Resumo Executivo, Categorias, Parcelas, Contratos e Tarefas com formatação monetária automática.
  - `ReportGenerationService.generate_and_store_report` — Geração e persistência segura no Storage de Nuvem (Cloudflare R2 / S3) via `StorageService`.
- **Background Tasks (`tasks.py`):**
  - `generate_wedding_report_task` — Tarefa assíncrona (`django.tasks`) para processamento pesado em segundo plano, despachando notificação in-app com link de download seguro.
- **Endpoints (`api.py`):**
  - `GET /api/v1/reports/weddings/{uuid}/` (`reports_wedding_export`) — Download síncrono imediato de relatórios em PDF ou Excel.
  - `POST /api/v1/reports/weddings/{uuid}/async/` (`reports_wedding_export_async`) — Enfileiramento de geração em segundo plano (HTTP 202 Accepted).
  - `GET /api/v1/dashboard/summary/` & `GET /api/v1/dashboard/wedding/{uuid}/` — Endpoints do dashboard executivo. Veja [openapi-schema](../../3-reference/api/openapi-schema.md).

### 2. Camada de Frontend (`frontend/src/features/reporting/`)

- **Componentes:**
  - `ExportReportDropdown.tsx` — Dropdown com opções de download síncrono direto (PDF/Excel) e disparo em segundo plano para o worker.
- **Hooks Customizados:**
  - `useExportReport.ts` — Orquestra downloads imediatos via Blob e mutações assíncronas com notificações via Sonner.
- **Integração na Visão do Casamento:**
  - `WeddingOverview.tsx` (`frontend/src/features/weddings/components/WeddingOverview.tsx`) — Botão de exportação integrado ao cabeçalho da visão geral do casamento.

---

## Domínios Relacionados

- [dashboard-domain](dashboard-domain.md) — Painel analítico de métricas da assessoria.
- [weddings-domain](weddings-domain.md) — Gestão do ciclo de vida dos casamentos.
- [finances-domain](finances-domain.md) — Dados de orçamento, categorias e parcelamento.
- [scheduler-domain](scheduler-domain.md) — Tarefas e compromissos operacionais.
- [logistics-domain](logistics-domain.md) — Contratos e fornecedores.
- [core-domain](core-domain.md) — Infraestrutura e serviços de storage (`StorageService`).

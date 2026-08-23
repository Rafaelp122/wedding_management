# MOC de Domínio: Relatórios & Métricas (Reporting)

> **Hub de Domínio:** [reporting-domain](reporting-domain.md) | [dashboard-domain](dashboard-domain.md) | [system-overview](../concepts/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/reporting/` & `frontend/src/features/reporting/`

---

## Visão Geral do Domínio

O domínio de **Reporting** é responsável pela consolidação, análise, diagramação e exportação de dados operacionais e financeiros da plataforma de casamentos. Ele fornece tanto visualizações em tempo real (painéis agregados) quanto geração de documentos exportáveis sob demanda em **PDF** (via ReportLab aderente ao `DESIGN.md`) e **Excel** (via openpyxl com paleta *Prestige Purple*).

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/reporting/`)

- **Query Selectors (`selectors/`):**
  - `dashboard_selectors.py` (`dashboard_summary_selector`, `wedding_overview_selector`) — Agregação lazy de KPIs consolidados multi-tenant.
  - `report_selectors.py` (`wedding_report_data_selector`, `WeddingReportDataDTO`) — Compilação unificada de dados e métricas em DTO imutável para renderizadores.
  - `selectors/summaries/` — Sub-selectors financeiros, contratuais e de tarefas.
- **Renderizadores e Utilitários (`pdf_utils.py` & `excel_utils.py`):**
  - `pdf_utils.py` (`render_wedding_pdf`, `NumberedCanvas`, `get_pdf_palette`) — Diagramação completa em PDF A4 com paleta oficial do `DESIGN.md` (`#7C3AED`, `#F5F3FF`, `#1A1C1E`), cartões de KPI, tabelas zebradas e paginação em dois passos ("Página X de Y").
  - `excel_utils.py` (`render_wedding_excel`) — Geração de planilha multi-aba (.xlsx) com Resumo Executivo, Categorias, Parcelas, Contratos e Tarefas, bordas e formatação monetária automática.
- **Service Layer (`services.py`):**
  - `ReportGenerationService.export_wedding_report` — Orquestração de negócio e delegação aos selectors e renderizadores, devolvendo a tupla binária `(file_bytes, content_type, filename)`.
- **Endpoints (`api.py`):**
  - `GET /api/v1/reports/weddings/{uuid}/` (`reports_wedding_export`) — Download direto de relatórios em PDF ou Excel.
  - `GET /api/v1/dashboard/summary/` & `GET /api/v1/dashboard/wedding/{uuid}/` — Endpoints do dashboard executivo. Veja [openapi-schema](../../reference/api/openapi-schema.md).

### 2. Camada de Frontend (`frontend/src/features/reporting/`)

- **Componentes:**
  - `ExportReportDropdown.tsx` — Dropdown com opções diretas de exportação ("Relatório (PDF)" e "Planilha (Excel)") com estado de loading visual.
- **Hooks Customizados:**
  - `useExportReport.ts` — Orquestra downloads imediatos via Blob e exibe feedback via toasts da biblioteca Sonner.
- **Integração na Visão do Casamento:**
  - `WeddingOverview.tsx` (`frontend/src/features/weddings/components/WeddingOverview.tsx`) — Botão de exportação integrado ao cabeçalho da visão geral do casamento.

---

## Domínios Relacionados

- [dashboard-domain](dashboard-domain.md) — Painel analítico de métricas da assessoria.
- [weddings-domain](weddings-domain.md) — Gestão do ciclo de vida dos casamentos.
- [finances-domain](finances-domain.md) — Dados de orçamento, categorias e parcelamento.
- [scheduler-domain](scheduler-domain.md) — Tarefas e compromissos operacionais.
- [logistics-domain](logistics-domain.md) — Contratos e fornecedores.
- [core-domain](core-domain.md) — Infraestrutura e serviços transversais.

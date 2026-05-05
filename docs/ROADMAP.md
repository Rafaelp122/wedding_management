# 🗺️ Roadmap de Balanceamento — Wedding Management System

**Objetivo:** Corrigir o desbalanceamento entre backend (8 CRUDs completos) e frontend (apenas 2 fluxos ponta a ponta), implementar automações cross-módulo definidas nos casos de uso e completar funcionalidades essenciais do MVP.

---

## 1. Diagnóstico

O sistema tem uma fundação arquitetural sólida (multitenancy, service layer, tolerância zero, Orval), mas está desbalanceado:

| Camada | Entidades com CRUD exposto | Fluxos ponta a ponta |
|:---|:---|:---|
| Backend | Wedding, Budget, BudgetCategory, Expense, Installment, Contract, Item, Event, Task, Supplier | — |
| Frontend | Wedding, Supplier | **Apenas 2** |

**Além disso, o backend expõe CRUD genérico para entidades que não deveriam ter CRUD.** O caso mais grave é `Installment`: parcelas nunca são criadas manualmente (UC03 diz que são auto-geradas), nunca são deletadas (quebra Tolerância Zero), e "pagar" é uma ação dedicada, não um PATCH genérico. O mesmo vale para `Budget`: criado lazy com o casamento, não se cria nem deleta manualmente.

As automações cross-módulo — que são o diferencial do produto — não existem em nenhuma camada: geração automática de parcelas, marcação OVERDUE, templates de cronograma, bridge Documento→Despesa, sistema de alertas.

**Este roadmap foca exclusivamente nas lacunas.** O que já funciona (CRUD de casamentos e fornecedores, multitenancy, auth JWT, base de modelos) não é repetido aqui.

---

### 1.1 Entidades que Realmente Precisam de CRUD

Nem toda entidade do domínio precisa de Create, Read, Update e Delete. O backend atual expõe CRUD completo para 10 entidades, mas apenas 6 delas justificam CRUD quando cruzadas com os casos de uso:

| Entidade | CREATE | READ | UPDATE | DELETE | Justificativa |
|:---|:---|:---|:---|:---|:---|
| **Wedding** | Sim | Sim | Sim | Sim | UC01 fluxo completo |
| **Supplier** | Sim | Sim | Sim | Sim | UC05 fluxo completo |
| **Budget** | — | Sim | Sim | — | Criado lazy via `GET /for-wedding/{uuid}/`. UC02 só edita `total_estimated`. Não se cria nem deleta manualmente |
| **BudgetCategory** | Sim | Sim | Sim | Sim | UC02 completo: criar, editar, excluir (com proteção de despesas vinculadas) |
| **Expense** | Sim | Sim | Sim | Sim | UC03 completo. O CREATE também orquestra parcelas |
| **Installment** | — | Sim | Parcial | — | **Auto-gerado** no UC03. Nunca criado manualmente. UC04: "Pagar" (ação dedicada), "Ajustar data/valor" (parcelas futuras). DELETE não existe em nenhum UC e quebra Tolerância Zero |
| **Contract** | Sim | Sim | Sim | Sim | UC07: upload, visualizar, editar metadados, remover rascunhos |
| **Item** | Sim | Sim | Sim | Sim | UC06: criar, listar, transitar status, remover |
| **Event** | Sim | Sim | Sim | Sim | UC08: criar manual. Eventos auto PAYMENT são read-only |
| **Task** | Sim | Sim | Sim | Sim | Checklist: criar, listar, editar, toggle, remover |

**Dos 10 CRUDs no backend atual, 4 têm endpoints de escrita que nunca deveriam ser expostos ao frontend:**

| Entidade | Endpoint a remover/tornar interno | Motivo |
|:---|:---|:---|
| **Budget** | `POST /budgets/`, `DELETE /budgets/{uuid}/` | Budget é criado lazy com o casamento. Não se cria nem deleta manualmente |
| **Installment** | `POST /installments/`, `DELETE /installments/{uuid}/` | Parcelas são auto-geradas (UC03), nunca criadas avulsas. DELETE quebra Tolerância Zero |
| **Installment** | `PATCH /installments/{uuid}/` (genérico) | Substituir por endpoints de ação: `POST /{uuid}/pay/` e `PATCH /{uuid}/adjust/` |

**Ações dedicadas que substituem CRUD genérico:**

| Ao invés de... | Usar... | Tipo |
|:---|:---|:---|
| `PATCH /installments/{uuid}` | `POST /installments/{uuid}/pay/` | Comando |
| `PATCH /installments/{uuid}` | `PATCH /installments/{uuid}/adjust/` | Ação específica |
| `POST /installments` | `POST /expenses` com `num_installments` | Criação orquestrada |
| `POST /budgets` | `GET /budgets/for-wedding/{uuid}/` | Lazy-create (já existe) |

---

## 2. Matriz de Prioridades

| Sprint | UC | Nome | Gap Crítico | Esforço Est. |
|:---|:---|:---|:---|:---|
| 1 | UC03 | Despesas | Sem create/edit no frontend, sem auto-installments | 3d |
| 1 | UC04 | Parcelas | Sem "Pagar", sem OVERDUE automático, sem BR-F06 | 3d |
| 2 | UC10 | Dashboard | 50% mock/hardcoded, métricas falsas | 2d |
| 2 | UC02 | Categorias | Read-only no frontend, sem CRUD | 1d |
| 3 | UC06 | Itens | Read-only no frontend, sem troca de status | 1.5d |
| 3 | UC07 | Documentos | Read-only, sem bridge Documento→Despesa, nomes não resolvidos | 3d |
| 4 | UC08 | Cronograma | Read-only, sem calendário visual, sem templates, sem eventos PAYMENT auto | 3d |
| 5 | UC09 | Alertas | Inexistente (backend + frontend) | 4d |
| 5 | UC11 | Relatórios | Inexistente | 3d |
| 6 | — | Non-Func | Rate limiting, BR-F02, BR-F04, backups | 2d |

---

## 3. Roadmap por Sprint

### Sprint 1 — Fluxos Financeiros Essenciais (MVP Core)

**Objetivo:** Viabilizar o fluxo completo de criar despesa → gerar parcelas → pagar parcelas, com Tolerância Zero e OVERDUE. Também limpar endpoints CRUD desnecessários expostos pelo backend (ver seção 1.1).

#### Backend

- [x] **Serviço `auto_generate_installments`** — função que recebe `expense`, `num_parcelas`, `first_due_date` e cria N parcelas com ajuste da última parcela (Tolerância Zero, BR-F01). Chamada dentro de `ExpenseService.create()` quando `num_installments > 0`.
  - **Ref:** UC03 fluxo principal, BR-F01
  - **Arquivo:** `backend/apps/finances/services/installment_service.py`

- [x] **Comando `mark_overdue_installments`** — varredura diária (Django management command) que marca como `OVERDUE` toda parcela com `due_date < today` e `status = PENDING`.
  - **Ref:** BR-F05, UC04 fluxo alternativo "Parcela Vencida"
  - **Arquivo:** `backend/apps/finances/management/commands/mark_overdue_installments.py`

- [x] **`InstallmentService.mark_as_paid()`** — método dedicado para marcar como pago (não PATCH genérico) que:
  1. Bloqueia alteração se `status = PAID` (BR-F06)
  2. Define `status = PAID`, `paid_date = today`
  3. Revalida Tolerância Zero na expense pai
  - **Ref:** BR-F06, UC04 fluxo principal
  - **Arquivo:** `backend/apps/finances/services/installment_service.py`

- [x] **Endpoint `POST /installments/{uuid}/mark-as-paid/`** — endpoint de ação dedicado (não PATCH genérico), chama `InstallmentService.mark_as_paid()`.
  - **Arquivo:** `backend/apps/finances/api/installments.py`

- [x] **Endpoint `PATCH /installments/{uuid}/adjust/`** — endpoint de ajuste de data/valor para parcelas futuras (não pagas). Valida que `due_date` não pode ser anterior à parcela anterior (UC04).
  - **Ref:** UC04 fluxo alternativo "Ajustar Parcela"
  - **Arquivo:** `backend/apps/finances/api/installments.py`

- [x] **Schemas de entrada** — adicionar `num_installments` e `first_due_date` ao `ExpenseIn` para permitir criação com parcelamento.
  - **Arquivo:** `backend/apps/finances/schemas.py`

- [x] **Remover endpoints CRUD desnecessários** (ver seção 1.1):
  - `POST /budgets/` e `DELETE /budgets/{uuid}/` — Budget é lazy-create, nunca criado/deletado manualmente
  - `POST /installments/` e `DELETE /installments/{uuid}/` — parcelas são auto-geradas; DELETE quebra Tolerância Zero
  - `PATCH /installments/{uuid}/` genérico — substituído por `POST .../mark-as-paid/` e `PATCH .../adjust/`
  - Manter apenas `GET /installments/` (list) e `GET /installments/{uuid}/` (read)
  - **Arquivo:** `backend/apps/finances/api/budgets.py`, `backend/apps/finances/api/installments.py`

- [x] **Atualizar `openapi.json` e regenerar Orval** — após remover endpoints, rodar `./manage.py export_openapi` e `npx orval` para que o frontend perca os hooks de CRUD removidos.

#### Frontend

- [x] **Dialog `CreateExpenseDialog`** — formulário com: nome, descrição (opcional), categoria (select), contrato (select, opcional), valor estimado, valor realizado, número de parcelas (min 1), vencimento da 1ª parcela. Ao submeter, chama `POST /expenses` com `num_installments`.
  - **Ref:** UC03 fluxo principal
  - **Arquivo:** `frontend/src/features/weddings/components/CreateExpenseDialog.tsx`

- [x] **Dialog `EditExpenseDialog`** — edição de despesa existente, respeitando bloqueios (parcelas pagas). Permite alterar nome, descrição, contrato, valores e número de parcelas (remanejamento).
  - **Arquivo:** `frontend/src/features/weddings/components/EditExpenseDialog.tsx`

- [x] **Botão "Marcar como Pago" na lista de parcelas** — em `WeddingUpcomingInstallments`, cada parcela pendente ganha um botão que chama `POST /installments/{uuid}/mark-as-paid/`. Toast de confirmação e refetch.
  - **Ref:** UC04 fluxo principal
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingUpcomingInstallments.tsx`

- [x] **Filtro `wedding_id` nas parcelas** — adicionar o parâmetro `wedding_id` à chamada de API em vez do filtro client-side com `limit: 5` hardcoded.
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingUpcomingInstallments.tsx`

- [x] **Indicador visual de OVERDUE** — parcelas com status `OVERDUE` renderizadas com badge vermelho e ícone de alerta.
  - **Ref:** UC04 fluxo alternativo

#### Extras implementados (além do escopo original do Sprint 1)

- [x] **Modelo `Expense`** — adicionado campo `name` (obrigatório); `description` alterado para `TextField` (opcional). Migration com data migration para copiar dados existentes.
  - **Ref:** BR-F10
  - **Arquivos:** `backend/apps/finances/models/expense.py`, `backend/apps/finances/migrations/0003_*.py`

- [x] **`ExpenseOut` enriquecido** — schema retorna `category_name`, `contract_description`, `status` (derivado: `PENDING`/`PARTIALLY_PAID`/`SETTLED`), `installments_count`, `paid_installments_count`, `total_paid`, `total_pending`. Tudo via annotation no queryset para evitar N+1.
  - **Arquivos:** `backend/apps/finances/schemas.py`, `backend/apps/finances/services/expense_service.py`

- [x] **Mínimo de 1 parcela** — `ExpenseService.create()` força `num_installments=1` se não informado; `first_due_date` padrão = hoje. Regra de negócio: toda despesa tem ao menos 1 parcela (BR-F07).
  - **Arquivo:** `backend/apps/finances/services/expense_service.py`

- [x] **`InstallmentService.redistribute()`** — remaneja parcelas (deleta e regera) se nenhuma estiver `PAID`. Bloqueia com erro caso haja parcelas marcadas como pagas (BR-F08).
  - **Arquivo:** `backend/apps/finances/services/installment_service.py`

- [x] **`ExpenseService.update()`** — se `num_installments` for enviado e diferente do atual, chama `redistribute()`. Função auxiliar `_handle_redistribute()` extraída para manter complexidade baixa.
  - **Arquivo:** `backend/apps/finances/services/expense_service.py`

- [x] **Filtro `expense_id` nas parcelas** — `GET /installments/?expense_id={uuid}` para buscar parcelas de uma despesa específica.
  - **Arquivos:** `backend/apps/finances/api/installments.py`, `backend/apps/finances/services/installment_service.py`

- [x] **`DeleteExpenseDialog`** — confirmação com nome da despesa, alerta de cascata (parcelas removidas).
  - **Arquivo:** `frontend/src/features/weddings/components/DeleteExpenseDialog.tsx`

- [x] **`ExpenseDetailDialog`** — modal completo com barra de progresso, tabela de parcelas com "Marcar como Pago", status da despesa, remanejamento inline de parcelas.
  - **Arquivo:** `frontend/src/features/weddings/components/ExpenseDetailDialog.tsx`

- [x] **Menu ⋮ (dropdown)** — ações Editar/Excluir na tabela de despesas via `DropdownMenu` (três pontinhos).
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingExpensesTable.tsx`

- [x] **Aba Finanças unificada** — cards de resumo + tabela de despesas com ações na mesma view, sem sub-tabs.
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingFinancesView.tsx`

- [x] **Input `selectAll` no focus** — campos numéricos dos dialogs selecionam todo o texto ao receber foco (se valor = 0), facilitando digitação.
  - **Arquivos:** `CreateExpenseDialog.tsx`, `EditExpenseDialog.tsx`

---

### Sprint 2 — Dashboard Real + Categorias (UC10 + UC02)

**Objetivo:** Dashboard global com dados reais (remover mocks) e CRUD de categorias de orçamento no frontend.

#### Backend

- [ ] **Endpoint de métricas agregadas do dashboard** — `GET /dashboard/summary/` retornando:
  - `active_weddings`: count de weddings com status `IN_PROGRESS`
  - `total_revenue`: soma de `total_estimated` dos budgets ativos
  - `pending_installments_7d`: soma dos valores de parcelas PENDING com vencimento em ≤ 7 dias
  - `events_this_week`: count de eventos nos próximos 7 dias
  - `total_guests`: soma de `expected_guests` dos casamentos ativos
  - **Ref:** UC10 fluxo principal
  - **Arquivo:** `backend/apps/weddings/services/dashboard_service.py` (novo)

- [ ] **Router de dashboard** — expor o endpoint acima. Prefixo `/api/v1/dashboard/`.
  - **Arquivo:** `backend/apps/weddings/api/dashboard.py` (novo)

#### Frontend

- [ ] **Hook `useDashboardSummary`** — consumir o novo endpoint agregado.
  - **Arquivo:** `frontend/src/features/dashboard/hooks/useDashboardSummary.ts`

- [ ] **Remover mocks do `StatsCards`** — substituir `"2.450"` (convidados hardcoded) e `totalRevenue ?? "R$ 0"` por dados reais do hook.
  - **Arquivo:** `frontend/src/features/dashboard/components/StatsCards.tsx`

- [ ] **`UpcomingAppointments` com dados reais** — substituir array mock por chamada `useSchedulerEventsList` com filtro de próximos 7 dias. Botão "Ver agenda completa" deve linkar para `/scheduler`.
  - **Ref:** UC10
  - **Arquivo:** `frontend/src/features/dashboard/components/UpcomingAppointments.tsx`

- [ ] **"Parcelas a Vencer (7d)" no dashboard** — card ou seção no dashboard mostrando parcelas dos próximos 7 dias com valores. Clicável, leva ao financeiro do casamento.
  - **Arquivo:** `frontend/src/features/dashboard/components/UpcomingInstallments.tsx` (novo)

- [ ] **Crédito de `WeddingMonthlyChart`** — ok, já funcional.

- [ ] **Dialog `CreateBudgetCategoryDialog`** — formulário com nome, valor orçado, descrição. Vinculado ao budget do casamento.
  - **Ref:** UC02
  - **Arquivo:** `frontend/src/features/weddings/components/CreateBudgetCategoryDialog.tsx`

- [ ] **Dialog `EditBudgetCategoryDialog`** — edição de categoria com alerta se valor novo < total já gasto (BR-F04 visual).
  - **Ref:** UC02 fluxo alternativo "Editar Categoria"
  - **Arquivo:** `frontend/src/features/weddings/components/EditBudgetCategoryDialog.tsx`

- [ ] **Dialog `DeleteBudgetCategoryDialog`** — confirmação com aviso se houver despesas vinculadas.
  - **Ref:** UC02 fluxo alternativo "Excluir Categoria"
  - **Arquivo:** `frontend/src/features/weddings/components/DeleteBudgetCategoryDialog.tsx`

- [ ] **Consertar botões mortos:**
  - `WeddingFinancesRecentExpenses`: botão "Adicionar Despesa" → abrir `CreateExpenseDialog`
  - `WeddingFinancesGroupsSummary`: botão "Ver Todas Categorias" → navegar ou expandir lista
  - `WeddingOverview`: links "Ver planejamento" / "Ver finanças" → navegação por tab

---

### Sprint 3 — Logística + Bridge Documento→Despesa (UC06 + UC07)

**Objetivo:** CRUD de itens, upload de documentos, e automação Documento→Despesa.

#### Backend

- [ ] **Endpoint `POST /expenses/from-document/{document_uuid}/`** — recebe UUID de um Contract, retorna payload pré-preenchido para criação de Expense:
  ```json
  {
    "description": "<contract.description>",
    "actual_amount": "<contract.total_amount>",
    "supplier_uuid": "<contract.supplier.uuid>",
    "category_uuid": null,
    "num_installments": null,
    "first_due_date": null
  }
  ```
  - **Ref:** UC07 fluxo alternativo "Gerar Despesa a partir de Documento"
  - **Arquivo:** `backend/apps/finances/api/expenses.py`

- [ ] **Validação BR-F02** — `Expense.clean()`: se `contract` não for nulo, `actual_amount` deve ser igual a `contract.total_amount`. `BusinessRuleViolation` se diferente.
  - **Ref:** BR-F02
  - **Arquivo:** `backend/apps/finances/models/expense.py`

- [ ] **Presigned URL para upload (opcional)** — se R2 estiver disponível, migrar `Contract.pdf_file` de `FileField` local para presigned URL (ADR-004). Caso contrário, manter `FileField` funcional.
  - **Ref:** ADR-004, UC07

#### Frontend

- [ ] **Dialog `CreateItemDialog`** — formulário com: nome, descrição, quantidade, contrato (select, opcional), status de aquisição.
  - **Ref:** UC06 fluxo principal
  - **Arquivo:** `frontend/src/features/weddings/components/CreateItemDialog.tsx`

- [ ] **Ação de troca de status do item** — dropdown ou botões para transitar `PENDING → IN_PROGRESS → DONE`.
  - **Ref:** UC06 fluxo alternativo "Atualizar Status"
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingItemsTable.tsx`

- [ ] **Resolver nomes de fornecedores** — em `WeddingVendorsTable`, buscar nomes de suppliers via `useLogisticsSuppliersList` em vez de mostrar UUIDs brutos.
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingVendorsTable.tsx`

- [ ] **Upload de PDF no frontend** — dialog ou área de drop para upload de contrato PDF.
  - **Ref:** UC07 fluxo principal
  - **Arquivo:** `frontend/src/features/weddings/components/ContractUploadDialog.tsx`

- [ ] **Botão "Gerar Despesa" no documento** — na visualização de um contrato, botão que chama `POST /expenses/from-document/{uuid}/` e abre `CreateExpenseDialog` pré-preenchido.
  - **Ref:** UC07 fluxo alternativo, automação cross-módulo
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingVendorsTable.tsx` (ação inline)

- [ ] **Disclaimer legal** — texto "Este sistema não substitui consultoria jurídica..." exibido antes do upload de documento.
  - **Ref:** UC07

---

### Sprint 4 — Cronograma Visual + Templates (UC08)

**Objetivo:** Substituir tabela por calendário visual, habilitar CRUD de eventos, templates na criação de casamento, e eventos PAYMENT automáticos.

#### Backend

- [ ] **Templates de cronograma** — 3 templates (Religioso 12m, Praia 6m, Civil+Buffet 3m) como constantes ou fixtures. Cada template é uma lista de eventos com `title`, `event_type`, `offset_days` (dias antes do casamento).
  - **Ref:** UC01 fluxo principal
  - **Arquivo:** `backend/apps/scheduler/services/templates.py` (novo)

- [ ] **`WeddingService.create()` com template** — se `template` for informado no payload de criação do casamento, popular eventos automaticamente ajustando `start_time = wedding_date - offset_days`.
  - **Ref:** UC01 fluxo principal, automação cross-módulo
  - **Arquivo:** `backend/apps/weddings/services/wedding_service.py`

- [ ] **Auto-geração de eventos PAYMENT** — ao criar uma parcela (ou em lote diário), criar/atualizar evento de tipo `PAYMENT` no scheduler com `start_time = installment.due_date` e `title = "Pagamento: {expense.description} - Parcela {n}"`. Evento é read-only no calendário (BR-S01).
  - **Ref:** BR-S01
  - **Arquivo:** `backend/apps/finances/services/installment_service.py` + `backend/apps/scheduler/services/events.py`

- [ ] **Recorrência de eventos** — campo `recurrence_rule` (RF3339 ou escolhas: NONE/WEEKLY/BIWEEKLY/MONTHLY) no modelo `Event`. Lógica de expansão na listagem ou no create.
  - **Ref:** UC08 fluxo alternativo "Evento Recorrente"
  - **Arquivo:** `backend/apps/scheduler/models/event.py`

#### Frontend

- [ ] **Componente de calendário visual** — substituir `SchedulerEventsTable` e `WeddingTimelineTable` por um calendário mensal/semanal (usando biblioteca como `react-big-calendar` ou componente customizado com grid de dias). Eventos coloridos por `wedding` e `event_type`.
  - **Ref:** UC08 fluxo principal
  - **Arquivo:** `frontend/src/features/scheduler/components/SchedulerCalendar.tsx` (novo)

- [ ] **Dialog `CreateEventDialog`** — formulário com: título, data/hora, tipo, descrição, lembrete, recorrência.
  - **Ref:** UC08
  - **Arquivo:** `frontend/src/features/scheduler/components/CreateEventDialog.tsx`

- [ ] **Dialog `EditEventDialog`** — bloqueado para eventos de tipo `PAYMENT` gerados automaticamente (BR-S01).
  - **Arquivo:** `frontend/src/features/scheduler/components/EditEventDialog.tsx`

- [ ] **Seletor de template no `CreateWeddingDialog`** — dropdown com os 3 templates + "Começar do zero". Ao selecionar template, campo adicional é enviado no payload.
  - **Ref:** UC01 fluxo principal
  - **Arquivo:** `frontend/src/features/weddings/components/CreateWeddingDialog.tsx`

---

### Sprint 5 — Alertas + Relatórios (UC09 + UC11)

**Objetivo:** Sistema de notificações in-app + email, exportação de relatórios PDF e Excel.

#### Backend

- [ ] **Modelo `Notification`** — campos: `user` (FK), `title`, `message`, `type` (OVERDUE_INSTALLMENT / UPCOMING_INSTALLMENT / EXPIRING_DOCUMENT), `is_read`, `link` (URL para navegação), `created_at`.
  - **Ref:** UC09
  - **Arquivo:** `backend/apps/scheduler/models/notification.py` (novo) ou novo app `notifications`

- [ ] **Serviço `NotificationService`** — métodos: `create_notification()`, `mark_read()`, `list_unread(user)`, `unread_count(user)`.
  - **Arquivo:** `backend/apps/scheduler/services/notification_service.py`

- [ ] **API de notificações** — `GET /notifications/` (list), `GET /notifications/unread-count/`, `PATCH /notifications/{uuid}/read/`.
  - **Arquivo:** `backend/apps/scheduler/api/notifications.py`

- [ ] **Disparo de notificações** — no comando `mark_overdue_installments` (Sprint 1), também criar `Notification` para cada parcela marcada OVERDUE. Para parcelas a vencer em ≤ 7 dias, criar notificação de lembrete.
  - **Ref:** UC09 fluxo principal e alternativo

- [ ] **Envio de email** — integração com serviço de email (SendGrid/Mailgun) para resumo diário de vencimentos.
  - **Ref:** UC09 canais de notificação
  - **Arquivo:** `backend/apps/scheduler/services/email_service.py`

- [ ] **Endpoint de relatório financeiro** — `GET /weddings/{uuid}/report/?format=pdf|excel` que gera PDF (via WeasyPrint/xhtml2pdf) ou Excel (via openpyxl) com dados financeiros do casamento.
  - **Ref:** UC11
  - **Arquivo:** `backend/apps/weddings/services/report_service.py` (novo)

#### Frontend

- [ ] **Badge de notificações na sidebar** — contador de `unread_count` no ícone de sino, atualizado via polling ou query refetch.
  - **Ref:** UC09
  - **Arquivo:** `frontend/src/components/app-sidebar/AppSidebar.tsx`

- [ ] **Dropdown/Página de notificações** — lista de notificações com título, mensagem, tempo relativo, indicador de lida/não-lida. Clique marca como lida e navega para o link.
  - **Arquivo:** `frontend/src/features/notifications/components/NotificationsDropdown.tsx` (novo)

- [ ] **Botão "Exportar Relatório"** — no dashboard do casamento (Aba Geral), botão dropdown com opções "PDF (Resumo para Cliente)" e "Excel (Controle Interno)". Chama endpoint e faz download.
  - **Ref:** UC11
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingOverview.tsx`

---

### Sprint 6 — Polish & Non-Functional

**Objetivo:** Fechar validações de negócio pendentes e requisitos não-funcionais.

#### Backend

- [ ] **Validação BR-F04** — `BudgetCategory.clean()`: warning (não bloqueante) se `total_spent > allocated_budget`. Pode ser log ou flag no modelo.
  - **Arquivo:** `backend/apps/finances/models/budget_category.py`

- [ ] **Rate limiting** — aplicar middleware de rate limit (ex: `django-ratelimit` ou via Cloud Run) nos endpoints de auth e mutação.
  - **Ref:** RNF02
  - **Arquivo:** `backend/config/settings.py`

- [ ] **Modelo `Wedding.status`** — adicionar status `CREATED` (default) e transição `CREATED → IN_PROGRESS` ao criar primeiro orçamento/despesa.
  - **Ref:** UC01 diagrama de status
  - **Arquivo:** `backend/apps/weddings/models.py`

#### Infra

- [ ] **Backup diário** — configurar backup automatizado do Neon PostgreSQL com retenção de 7 dias.
  - **Ref:** RNF03

- [ ] **Verificação de acessibilidade** — auditoria com axe-core ou Lighthouse nos fluxos principais.

#### Frontend

- [ ] **Corrigir texto hardcoded** — `WeddingFinancesSummaryCards`: substituir "12% maior que a media" e "Dentro do planejado" por valores calculados com base nos dados reais.
  - **Arquivo:** `frontend/src/features/weddings/components/WeddingFinancesSummaryCards.tsx`

---

## 4. Checklist por Módulo

### `backend/apps/weddings/`

- [ ] `services/dashboard_service.py`: endpoint de métricas agregadas (Sprint 2)
- [ ] `api/dashboard.py`: router de dashboard (Sprint 2)
- [ ] `services/wedding_service.py`: suporte a `template` na criação (Sprint 4)
- [ ] `services/report_service.py`: geração de PDF e Excel (Sprint 5)
- [ ] `models.py`: adicionar status `CREATED` (Sprint 6)

### `backend/apps/finances/`

- [x] `services/installment_service.py`: `auto_generate_installments()`, `mark_as_paid()`, `adjust()`, `redistribute()` (Sprint 1)
- [x] `management/commands/mark_overdue_installments.py`: comando diário (Sprint 1)
- [x] `api/installments.py`: endpoints `POST /{uuid}/mark-as-paid/`, `PATCH /{uuid}/adjust/`; remover POST/DELETE/PATCH genérico; + filtro `expense_id` (Sprint 1)
- [x] `api/budgets.py`: remover `POST /` e `DELETE /{uuid}/` (Sprint 1)
- [x] `schemas.py`: campos `num_installments`, `first_due_date`; `ExpenseOut` enriquecido com `name`, `category_name`, `contract_description`, `status`, `installments_count`, `paid_installments_count`, `total_paid`, `total_pending` (Sprint 1)
- [x] `models/expense.py`: campo `name` obrigatório, `description` opcional (Sprint 1)
- [x] `services/expense_service.py`: `create()` força min 1 parcela; `update()` com redistribute via `_handle_redistribute()` (Sprint 1)
- [ ] `api/expenses.py`: endpoint `POST /from-document/{uuid}/` (Sprint 3)
- [ ] `models/expense.py`: validação BR-F02 (Sprint 3)
- [ ] `models/budget_category.py`: validação BR-F04 (Sprint 6)

### `backend/apps/logistics/`

- [ ] Upload presigned URL (R2) ou manter FileField funcional (Sprint 3)

### `backend/apps/scheduler/`

- [ ] `services/templates.py`: 3 templates de cronograma (Sprint 4)
- [ ] `services/event_service.py`: auto-geração de eventos PAYMENT (Sprint 4)
- [ ] `models/event.py`: campo `recurrence_rule` (Sprint 4)
- [ ] `models/notification.py`: modelo Notification (Sprint 5)
- [ ] `services/notification_service.py`: CRUD de notificações (Sprint 5)
- [ ] `api/notifications.py`: endpoints de notificação (Sprint 5)
- [ ] `services/email_service.py`: envio de emails (Sprint 5)

### `frontend/src/features/weddings/`

- [x] `components/CreateExpenseDialog.tsx` — formulário com name, description, categoria, contrato, valores, parcelas (Sprint 1)
- [x] `components/EditExpenseDialog.tsx` — edição de despesa + remanejamento de parcelas (Sprint 1)
- [x] `components/DeleteExpenseDialog.tsx` — confirmação com nome da despesa (Sprint 1, extra)
- [x] `components/ExpenseDetailDialog.tsx` — modal com parcelas, progresso, mark-as-paid, remanejar (Sprint 1, extra)
- [x] `components/WeddingUpcomingInstallments.tsx`: botão "Marcar como Pago" + filtro wedding_id + indicador OVERDUE (Sprint 1)
- [x] `components/WeddingExpensesTable.tsx`: colunas nome/categoria/parcelas/status + menu ⋮ (Editar/Excluir) + clique → modal (Sprint 1, extra)
- [x] `components/WeddingDetailTabs.tsx`: sub-tabs Finanças (Resumo / Despesas) (Sprint 1, extra)
- [x] `components/WeddingFinancesRecentExpenses.tsx`: mostra name + categoria + parcelas + status + clique → modal (Sprint 1, extra)
- [ ] `components/CreateBudgetCategoryDialog.tsx` (Sprint 2)
- [ ] `components/EditBudgetCategoryDialog.tsx` (Sprint 2)
- [ ] `components/DeleteBudgetCategoryDialog.tsx` (Sprint 2)
- [ ] `components/CreateItemDialog.tsx` (Sprint 3)
- [ ] `components/ContractUploadDialog.tsx` (Sprint 3)
- [ ] `components/WeddingVendorsTable.tsx`: resolver nomes + botão "Gerar Despesa" (Sprint 3)
- [ ] `components/WeddingItemsTable.tsx`: troca de status (Sprint 3)
- [ ] `components/CreateWeddingDialog.tsx`: seletor de template (Sprint 4)
- [ ] `components/WeddingOverview.tsx`: botão "Exportar Relatório", links "Ver planejamento/finanças" funcionais (Sprint 2, Sprint 5)
- [ ] `components/WeddingFinancesSummaryCards.tsx`: remover texto hardcoded (Sprint 6)
- [ ] `components/WeddingFinancesRecentExpenses.tsx`: botão "Adicionar Despesa" funcional (Sprint 2)
- [ ] `components/WeddingFinancesGroupsSummary.tsx`: botão "Ver Todas Categorias" funcional (Sprint 2)

### `frontend/src/features/dashboard/`

- [ ] `hooks/useDashboardSummary.ts` (Sprint 2)
- [ ] `components/StatsCards.tsx`: dados reais (Sprint 2)
- [ ] `components/UpcomingAppointments.tsx`: dados reais (Sprint 2)
- [ ] `components/UpcomingInstallments.tsx`: parcelas a vencer (Sprint 2)

### `frontend/src/features/scheduler/`

- [ ] `components/SchedulerCalendar.tsx`: calendário visual (Sprint 4)
- [ ] `components/CreateEventDialog.tsx` (Sprint 4)
- [ ] `components/EditEventDialog.tsx` (Sprint 4)

### `frontend/src/features/notifications/` (novo)

- [ ] `components/NotificationsDropdown.tsx` (Sprint 5)

---

## 5. Dependências

```
Sprint 1 (Financeiro)
  ├── auto_generate_installments ──► Sprint 3 (Documento→Despesa pode usar)
  ├── mark_overdue_installments ──► Sprint 5 (Notificações de OVERDUE dependem disso)
  └── pay() + BR-F06 ────────────► (independente)

Sprint 2 (Dashboard + Categorias)
  ├── endpoint /dashboard/summary ──► (independente)
  └── BudgetCategory dialogs ──────► Sprint 3 (Itens usam categoria)

Sprint 3 (Logística + Bridge)
  ├── CreateItemDialog ────────────► (independente)
  ├── Documento→Despesa ──────────► usa ExpenseService (Sprint 1)
  └── resolve supplier names ─────► (independente)

Sprint 4 (Cronograma)
  ├── calendário visual ───────────► usa eventos CRUD (precisa existir)
  ├── templates ───────────────────► usa WeddingService + EventService
  └── eventos PAYMENT auto ───────► usa InstallmentService (Sprint 1)

Sprint 5 (Alertas + Relatórios)
  ├── notificações ───────────────► depende de mark_overdue (Sprint 1)
  ├── email ──────────────────────► depende de mark_overdue (Sprint 1)
  └── relatórios ─────────────────► usa dados financeiros (Sprint 1-2)

Sprint 6 (Polish)
  └── (independente, fecha arestas)
```

**Regra de bloqueio:** Um sprint só depende de tasks do sprint anterior, nunca de sprints futuros. Tasks dentro do mesmo sprint podem ser paralelizadas.

---

## 6. Referências

- [Casos de Uso](use-cases/index.md)
- [Requisitos Funcionais](REQUIREMENTS.md)
- [Regras de Negócio](BUSINESS_RULES.md)
- [Arquitetura](ARCHITECTURE.md)
- [ADR-004 (Presigned URLs)](ADR/004-presigned-urls.md)
- [ADR-010 (Tolerância Zero)](ADR/010-tolerance-zero.md)
- [ADR-012 (Orval Contract-Driven)](ADR/012-orval-contract-driven-frontend.md)

---

**Versão:** 1.2 (Sprint 1 concluído com extras documentados)
**Criado em:** 3 de maio de 2026
**Atualizado em:** 4 de maio de 2026
**Responsável:** Rafael

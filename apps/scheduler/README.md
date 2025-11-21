# App: Scheduler

O app `scheduler` gerencia o calendário de eventos relacionados aos casamentos. Permite criar, visualizar, editar e deletar compromissos como reuniões, pagamentos, provas e outros eventos importantes do planejamento.

---

## Status Atual

**Versão:** 2.0 (Refatorado com Lean Testing + ModalContextMixin)  
**Testes:** 61 passando  
**Cobertura:** models, forms, views, mixins, querysets, API

---

## Responsabilidades

-   **Gerenciamento de Eventos:** CRUD completo de eventos de calendário
-   **Visualização Temporal:** Exibição de eventos em formato de calendário
-   **Filtros e Busca:** Filtrar eventos por tipo, status e busca textual
-   **API REST:** Endpoint JSON para integração com frontend (FullCalendar)
-   **Validação de Horários:** Garante que horário de fim seja após início

---

## Arquitetura

### Padrões Aplicados
- **Single Responsibility Principle (SRP):** Cada mixin tem uma responsabilidade
- **Separation of Concerns:** Lógica separada em mixins granulares
- **DRY:** Reutilização de mixins do core (ModalContextMixin)
- **Lean Testing:** Testes focados em comportamento crítico

---

## Estrutura de Arquivos

### Arquivos Python

-   **`models.py`:** Modelo `Event` para eventos de calendário
    - Campos: title, description, event_type, start_time, end_time, status
    - FK para Wedding (cada evento pertence a um casamento)
    - Choices para tipo (reunião, pagamento, prova, tarefa, outro)
    - Choices para status (pendente, confirmado, cancelado, concluído)
    - Validações no save() (horário fim > início)

-   **`querysets.py`:** QuerySet personalizado com filtros
    - `by_wedding(wedding)` - Filtra por casamento
    - `by_date_range(start, end)` - Filtra por período
    - `upcoming()` - Eventos futuros ordenados por data
    - `apply_search(q)` - Busca por título/descrição
    - `apply_sort(sort_option)` - Ordenação customizada

-   **`forms.py`:** Formulário `EventForm` com validações
    - Validação: end_time > start_time
    - Widget DateTimeInput com formato brasileiro
    - Placeholders e ícones
    - Logging de validações falhadas

-   **`mixins.py`:** Arquitetura granular com 8 mixins
    - **Segurança:**
      - `EventOwnershipMixin` - Garante que user só acessa seus eventos
    - **Layout:**
      - `EventFormLayoutMixin` - Define layout do formulário
      - `EventModalContextMixin` - Contexto de modais (DEPRECIADO)
    - **Query:**
      - `EventQuerysetMixin` - Lógica de filtros e busca
    - **Paginação:**
      - `EventPaginationContextMixin` - Paginação de eventos
    - **HTMX:**
      - `EventHtmxResponseMixin` - Respostas HTMX customizadas
    - **Form:**
      - `EventFormMixin` - Lógica de form_valid/invalid
    - **Composição:**
      - `EventListActionsMixin` - Facade (agrupa funcionalidades)

-   **`views.py`:** Class-Based Views com mixins do core
    - `EventCalendarView` - Calendário principal
    - `EventCreateView` - Criação com modal (usa ModalContextMixin)
    - `EventUpdateView` - Edição com modal (usa ModalContextMixin)
    - `EventDeleteView` - Exclusão com confirmação
    - `EventDetailView` - Detalhes do evento

-   **`api_views.py`:** API REST para FullCalendar
    - `EventListAPIView` - JSON com eventos do calendário
    - Filtros por wedding_id
    - Formato compatível com FullCalendar.js

-   **`urls.py`:** Rotas RESTful + API
    - `/<wedding_id>/calendar/` - Calendário
    - `/<wedding_id>/events/create/` - Criar
    - `/events/<pk>/edit/` - Editar
    - `/events/<pk>/delete/` - Deletar
    - `/events/<pk>/` - Detalhe
    - `/api/events/` - API JSON

-   **`admin.py`:** Interface administrativa
    - Campos visíveis: id, título, tipo, data início, wedding
    - Busca por título
    - Filtros por tipo, status, wedding

### Testes (`tests/`)

- **`test_models.py` (10 testes):**
  - Validação de horários (fim > início)
  - Representação em string
  - Choices de tipo e status
  - Cascade de deleção

- **`test_querysets.py` (6 testes):**
  - Filtros por casamento e período
  - Eventos futuros
  - Busca e ordenação

- **`test_forms.py` (11 testes):**
  - Validação de horários inválidos
  - Data/hora no passado
  - Widgets customizados
  - Logging de erros

- **`test_mixins.py` (8 testes):**
  - **Segurança:** Isolamento por usuário/wedding
  - **HTMX:** Respostas corretas
  - **Form:** Relações de formulário
  - Removidos: 17 testes de config, UI, implementação

- **`test_views.py` (14 testes):**
  - Calendário: renderização, filtros
  - Create: modal, validação, segurança
  - Update: edição, validação
  - Delete: confirmação, exclusão
  - Detail: dados corretos
  - Segurança: isolamento de dados

- **`test_api_views.py` (2 testes):**
  - API retorna JSON correto
  - Filtros por wedding

- **`test_urls.py` (10 testes):**
  - Resolução de todas as URLs
  - Parâmetros corretos

### Templates (`templates/scheduler/`)

-   **`calendar.html`:** Página principal com FullCalendar.js
-   **`event_detail.html`:** Detalhes de um evento
-   **`partials/`:** Fragmentos HTMX
    -   `_event_form.html` - Formulário de evento
    -   `_event_list.html` - Lista de eventos

### Arquivos Estáticos (`static/scheduler/`)

-   **`js/`**:
    -   `calendar.js` - Integração com FullCalendar.js
    -   `events.js` - Manipulação de eventos

---

## Segurança

- **Autenticação:** LoginRequiredMixin em todas as views
- **Autorização:** EventOwnershipMixin garante isolamento
- **Validação:** Horários válidos, data futura
- **Logging:** Tentativas de acesso não autorizado registradas
- **API:** Filtra eventos por planner do usuário

---

## Performance

- **Queries otimizadas:** `select_related('wedding__planner')`
- **API eficiente:** Serialização direta para JSON
- **Filtros no banco:** Queries otimizadas com annotate
- **Índices:** Considerar adicionar (wedding + start_time)

---

## Melhorias Recentes (v2.0)

### Refatoração de Mixins:
- Uso de `ModalContextMixin` do core (DRY)
- Redução de 25→8 testes em mixins (68% redução)
- Eliminação de testes de implementação
- Foco em segurança e comportamento crítico

### Padrões Aplicados:
- EventOwnershipMixin para segurança em 4 cenários
- EventHtmxResponseMixin para respostas consistentes
- EventFormMixin para lógica de formulário centralizada

---

## Próximos Passos

### Sugerido:
1. Adicionar índices compostos (wedding + start_time)
2. Melhorar admin.py (mais campos, date_hierarchy)
3. Adicionar recurring events (eventos recorrentes)
4. Notificações de lembrete (X dias antes do evento)

---

## Lições Aprendidas

**Filosofia de Testes:**
- **TESTA:** Segurança (isolamento de dados), validações, edge cases
- **NÃO TESTA:** Config estática (model = Event), detalhes de UI

**Arquitetura:**
- Mixins granulares facilitam manutenção
- Reutilização de core mixins evita duplicação
- Separação de API views mantém código limpo

---

## Integrações

- **FullCalendar.js:** Biblioteca JavaScript para visualização de calendário
- **API REST:** Endpoint JSON para integração frontend
- **HTMX:** Atualizações dinâmicas sem page reload

---

**Última Atualização:** 21 de novembro de 2025  
**Refatoração:** Lean Testing + ModalContextMixin do core

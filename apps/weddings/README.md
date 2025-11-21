# App: Weddings

O app `weddings` é o núcleo da aplicação, responsável por gerenciar a entidade principal do sistema: o Casamento (`Wedding`). Ele lida com a criação, visualização, listagem e todos os detalhes associados a um casamento.

---

## Status Atual

**Versão:** 2.0 (Refatorado com Lean Testing + ModalContextMixin)  
**Testes:** 109 passando  
**Cobertura:** models, forms, views, mixins, querysets

---

## Responsabilidades

-   **Gerenciamento de Casamentos:** Define o modelo `Wedding` e fornece as interfaces para que os usuários possam criar e gerenciar seus casamentos.
-   **Visualização de Detalhes:** Apresenta uma página de detalhes completa para cada casamento, que serve como um painel central para acessar outras funcionalidades relacionadas (Orçamento, Contratos, etc.).
-   **Listagem de Eventos:** Exibe todos os casamentos associados a um usuário com filtros e busca.

---

## Arquitetura

### Padrões Aplicados
- **Single Responsibility Principle (SRP):** Cada mixin tem uma responsabilidade clara
- **Separation of Concerns:** Lógica separada em mixins granulares
- **DRY:** Reutilização de mixins do core
- **Lean Testing:** Testes focados em comportamento, não implementação

---

## Estrutura de Arquivos

### Arquivos Python

-   **`models.py`:** Define o `Wedding`, modelo de dados central que armazena informações como nome dos noivos, data e local.
    - Validações customizadas (data futura, orçamento positivo)
    - Property `days_until_wedding` calculada
    - Choices para status (PLANNING, IN_PROGRESS, COMPLETED, CANCELLED)

-   **`querysets.py`:** QuerySet personalizado com métodos de filtragem
    - `by_status(status)` - Filtra por status do casamento
    - `apply_search(q)` - Busca por nome dos noivos
    - `apply_sort(sort_option)` - Ordenação (data, orçamento, nome)
    - `with_counts()` - Anota contagens de itens e contratos

-   **`forms.py`:** Formulário com validações de negócio
    - Validação de data (não pode ser passada)
    - Validação de orçamento (positivo)
    - Placeholders e widgets customizados
    - Logging de tentativas inválidas

-   **`mixins.py`:** Arquitetura granular com 6 mixins
    - `PlannerOwnershipMixin` - Segurança (filtra por planner)
    - `WeddingQuerysetMixin` - Lógica de query (filtros, busca, sort)
    - `WeddingPaginationContextMixin` - Paginação (12 por página)
    - `WeddingHtmxListResponseMixin` - Respostas HTMX
    - `WeddingFormLayoutMixin` - Layout de formulário
    - `WeddingListActionsMixin` - Facade (agrupa funcionalidades)

-   **`views.py`:** Class-Based Views com composição de mixins
    - `WeddingListView` - Lista paginada com busca/filtros
    - `WeddingCreateView` - Criação com modal
    - `WeddingUpdateView` - Edição com modal
    - `WeddingDeleteView` - Exclusão com confirmação
    - `WeddingDetailView` - Painel de detalhes
    - `UpdateWeddingStatusView` - Mudança de status via HTMX

-   **`urls.py`:** Rotas RESTful
    - `/` - Lista
    - `/create/` - Criar
    - `/<pk>/` - Detalhe
    - `/<pk>/edit/` - Editar
    - `/<pk>/delete/` - Deletar
    - `/<pk>/update-status/` - Atualizar status

-   **`admin.py`:** Interface administrativa
    - Campos visíveis: id, noivos, data, local, orçamento, status
    - Busca por nome dos noivos
    - Filtros por status e planner
    - readonly_fields para campos calculados

### Testes (`tests/`)

- **`test_models.py` (9 testes):**
  - Validações de data e orçamento
  - Property `days_until_wedding`
  - Representação em string
  - Cascade de deleção

- **`test_querysets.py` (8 testes):**
  - Filtragem por status
  - Busca por nome
  - Ordenação (data, orçamento, nome)
  - Anotação de contagens

- **`test_forms.py` (10 testes):**
  - Validação de data passada
  - Validação de orçamento negativo
  - Widgets e placeholders
  - Logging de erros

- **`test_mixins.py` (8 testes - REFATORADO):**
  - **Segurança:** Isolamento de dados por usuário
  - **Filtros:** Busca e status
  - **Paginação:** Anotações
  - Removidos: testes de config, UI, implementação

- **`test_views.py` (64 testes):**
  - Lista: paginação, busca, filtros, HTMX
  - Create: modal, validação, resposta HTMX
  - Update: edição, validação, segurança
  - Delete: confirmação, exclusão, segurança
  - Detail: renderização, dados corretos
  - Status: mudança válida/inválida, segurança

- **`test_urls.py` (6 testes):**
  - Resolução de URLs
  - Parâmetros corretos

### Templates (`templates/weddings/`)

-   **`list.html`:** Página principal de listagem
-   **`detail.html`:** Painel com abas (Orçamento, Contratos, Itens, Calendário)
-   **`partials/`:** Fragmentos HTMX reutilizáveis
    -   `_wedding_list_content.html` - Lista de cards
    -   `_wedding_card.html` - Card individual
    -   `_create_wedding_form.html` - Formulário de criação

### Arquivos Estáticos (`static/weddings/`)

-   **`css/`**:
    -   `list.css` - Estilos da listagem
    -   `detail.css` - Estilos dos detalhes
-   **`js/`**:
    -   `clickable_cards.js` - Cards clicáveis
    -   `detail_tabs.js` - Navegação por abas

---

## Segurança

- **Autenticação:** LoginRequiredMixin em todas as views
- **Autorização:** Queries filtradas por `planner` (isolamento de dados)
- **Validação:** Data futura, orçamento positivo
- **Logging:** Tentativas de acesso não autorizado registradas

---

## Performance

- **Queries otimizadas:** `select_related`, `prefetch_related`
- **Anotações no banco:** Contagens via `annotate()`
- **Paginação:** 12 casamentos por página
- **Índices:** Considerar adicionar no futuro (wedding + status)

---

## Próximos Passos

### Sugerido:
1. Adicionar índices compostos no model (performance)
2. Melhorar admin.py (mais campos, filtros)
3. Considerar soft delete (manter histórico)

---

## Lições Aprendidas

**Filosofia de Testes:**
- **TESTA:** Segurança, lógica de negócio, edge cases
- **NÃO TESTA:** Config estática, detalhes de UI, implementação

**Arquitetura:**
- Mixins granulares facilitam composição
- Facade pattern agrupa funcionalidades relacionadas
- Reutilização de mixins do core evita duplicação

---

**Última Atualização:** 21 de novembro de 2025  
**Refatoração:** Lean Testing (38→16 testes em mixins)

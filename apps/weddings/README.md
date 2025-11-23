# App: Weddings

O app `weddings` é o núcleo da aplicação, responsável por gerenciar a entidade principal do sistema: o Casamento (`Wedding`). **A partir da versão 3.0, o app possui duas interfaces distintas: Web (HTMX) e API (REST)**, permitindo tanto uso tradicional via navegador quanto integrações programáticas.

---

## Status Atual

**Versão:** 3.0 (Arquitetura Híbrida: Web + API)  
**Testes:** 60 passando (53 web + 7 API)  
**Cobertura:** models, forms, views, mixins, querysets, serializers, permissions  
**Interfaces:** Web (Django + HTMX) + API (Django REST Framework)

---

## Responsabilidades

-   **Gerenciamento de Casamentos:** Define o modelo `Wedding` e fornece as interfaces para que os usuários possam criar e gerenciar seus casamentos.
-   **Interface Web (HTMX):** Interface tradicional com Django templates e HTMX para interações dinâmicas.
-   **Interface API (REST):** API RESTful para integrações externas, apps mobile e webhooks.
-   **Visualização de Detalhes:** Apresenta uma página de detalhes completa para cada casamento, que serve como um painel central para acessar outras funcionalidades relacionadas (Orçamento, Contratos, etc.).
-   **Listagem de Eventos:** Exibe todos os casamentos associados a um usuário com filtros e busca.

---

## Arquitetura

### Padrões Aplicados
- **Single Responsibility Principle (SRP):** Cada mixin tem uma responsabilidade clara
- **Separation of Concerns:** Lógica separada em mixins granulares (web) e ViewSets (API)
- **DRY:** Reutilização de mixins do core e modelos compartilhados
- **Lean Testing:** Testes focados em comportamento, não implementação
- **Hybrid Architecture:** Interfaces separadas (web/ e api/) compartilhando models e querysets

### Estrutura de Interfaces

```
apps/weddings/
├── models.py              # Compartilhado (Web + API)
├── querysets.py           # Compartilhado (Web + API)
├── admin.py               # Compartilhado (Admin Django)
├── constants.py           # Compartilhado (Configurações)
│
├── web/                   # Interface Web (Django + HTMX)
│   ├── forms.py          # Formulários Django
│   ├── views.py          # Class-Based Views
│   ├── mixins.py         # Mixins granulares
│   └── urls.py           # Rotas web
│
├── api/                   # Interface API (DRF)
│   ├── serializers.py    # Serializers REST
│   ├── views.py          # ViewSets DRF
│   ├── permissions.py    # Permissões customizadas
│   └── urls.py           # Rotas API
│
└── tests/
    ├── test_models.py        # Testes de modelos
    ├── test_querysets.py     # Testes de querysets
    ├── web/                  # Testes da interface web
    │   ├── test_forms.py
    │   ├── test_views.py
    │   ├── test_mixins.py
    │   └── test_urls.py
    └── api/                  # Testes da interface API
        └── test_serializers.py
```

---

## Estrutura de Arquivos

### Arquivos Compartilhados

-   **`models.py`:** Define o `Wedding`, modelo de dados central que armazena informações como nome dos noivos, data e local.
    - Validações customizadas (data futura, orçamento positivo)
    - Property `days_until_wedding` calculada
    - Choices para status (IN_PROGRESS, COMPLETED, CANCELLED)

-   **`querysets.py`:** QuerySet personalizado com métodos de filtragem
    - `by_status(status)` - Filtra por status do casamento
    - `apply_search(q)` - Busca por nome dos noivos
    - `apply_sort(sort_option)` - Ordenação (data, orçamento, nome)
    - `with_counts_and_progress()` - Anota contagens de itens e contratos
    - `with_effective_status()` - Calcula status efetivo baseado na data

-   **`constants.py`:** Centraliza constantes (paginação, IDs HTMX, templates)

### Interface Web (`web/`)

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

### Interface API (`api/`)

-   **`serializers.py`:** Serializers REST com 3 níveis de detalhe
    - **`WeddingSerializer`:** CRUD (create, update) com validações
        * Valida orçamento positivo
        * Valida data não-passada
        * Campos editáveis: groom_name, bride_name, date, location, budget, status
    - **`WeddingListSerializer`:** Listagem otimizada
        * Campos: id, couple_name, date, location, status, planner_name
        * SerializerMethodField: couple_name formatado
    - **`WeddingDetailSerializer`:** Detalhes completos
        * Todos os campos + items_count, contracts_count
        * Inclui planner_email para contato

-   **`views.py`:** ViewSet com endpoints CRUD completos
    - **`WeddingViewSet` (ModelViewSet):**
        * `GET /api/v1/weddings/` - Lista casamentos do usuário
        * `POST /api/v1/weddings/` - Cria novo casamento
        * `GET /api/v1/weddings/{id}/` - Detalhes do casamento
        * `PUT /api/v1/weddings/{id}/` - Atualiza completo
        * `PATCH /api/v1/weddings/{id}/` - Atualiza parcial
        * `DELETE /api/v1/weddings/{id}/` - Deleta casamento
        * `PATCH /api/v1/weddings/{id}/update-status/` - Atualiza apenas status
    - Filtros via query params: `?status=IN_PROGRESS`, `?q=John`, `?sort=date`
    - Logging completo de todas as operações
    - Usa querysets customizados (with_counts, with_effective_status)

-   **`permissions.py`:** Permissões customizadas
    - **`IsWeddingOwner`:** Garante que apenas o planner dono pode acessar
        * Validação em nível de objeto
        * Mensagens de erro customizadas

-   **`urls.py`:** Rotas da API com DRF Router
    - Registra WeddingViewSet com basename='wedding'
    - URLs automáticas do Router
    - Namespace: `weddings_api`

### Testes (`tests/`)

#### Interface Web (`tests/web/`)

- **`test_models.py` (2 testes):**
  - Criação de wedding
  - Representação em string

- **`test_querysets.py` (2 testes):**
  - Filtragem por status
  - Busca por nome

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

- **`test_views.py` (24 testes):**
  - Lista: paginação, busca, filtros, HTMX
  - Create: modal, validação, resposta HTMX
  - Update: edição, validação, segurança
  - Delete: confirmação, exclusão, segurança
  - Detail: renderização, dados corretos
  - Status: mudança válida/inválida, segurança

- **`test_urls.py` (6 testes):**
  - Resolução de URLs
  - Parâmetros corretos

- **`test_admin.py` (1 teste):**
  - Registro no admin

#### Interface API (`tests/api/`)

- **`test_serializers.py` (7 testes - NOVO):**
  - **WeddingSerializer:**
    * Validação de dados válidos
    * Rejeição de orçamento negativo
    * Rejeição de data passada
  - **WeddingListSerializer:**
    * Campos esperados na resposta
    * Formatação de couple_name
  - **WeddingDetailSerializer:**
    * Campos detalhados na resposta
    * Inclusão de planner_email

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

### Interface Web
- **Autenticação:** LoginRequiredMixin em todas as views
- **Autorização:** Queries filtradas por `planner` (isolamento de dados)
- **Validação:** Data futura, orçamento positivo
- **Logging:** Tentativas de acesso não autorizado registradas

### Interface API
- **Autenticação:** SessionAuthentication (pode adicionar TokenAuthentication)
- **Permissões:** IsAuthenticated + IsWeddingOwner (object-level)
- **Validação:** Mesmas regras de negócio (serializers)
- **Logging:** Todas as operações CRUD registradas

---

## Performance

- **Queries otimizadas:** `select_related`, `prefetch_related`
- **Anotações no banco:** Contagens via `annotate()`
- **Paginação:** 10 items por página (API), 6 items por página (Web)
- **Serializers diferenciados:** List vs Detail para economizar queries

---

## Melhorias Recentes

### v3.0 - Arquitetura Híbrida (Web + API) 🚀

**Data:** 21/11/2025

**Motivação:**
- Portfolio: Demonstrar conhecimento de APIs REST
- TCC: Comparação entre paradigmas (HTMX vs API)
- Escalabilidade: Preparar para apps mobile e integrações

**Mudanças Estruturais:**
1. **Separação de Interfaces:**
   - Criados diretórios `web/` e `api/`
   - Models e querysets compartilhados (raiz)
   - Testes organizados por interface

2. **Nova Interface API:**
   - Django REST Framework instalado e configurado
   - 4 arquivos criados: serializers.py, views.py, permissions.py, urls.py
   - 7 testes de serializers criados
   - ViewSet completo com CRUD + custom action (update-status)

3. **Imports e Compatibilidade:**
   - `__init__.py` com lazy imports (`__getattr__`)
   - Re-exports mantêm compatibilidade com código antigo
   - URLs principais atualizadas (web + api/v1)

4. **Configurações:**
   - `rest_framework` adicionado ao INSTALLED_APPS
   - Configurações DRF no settings.py (auth, permissions, pagination)

**Arquivos Modificados:**
- `wedding_management/settings.py` - Adicionado DRF
- `wedding_management/urls.py` - Rotas API v1
- `apps/weddings/__init__.py` - Lazy imports
- `apps/weddings/web/mixins.py` - Imports relativos corrigidos
- `apps/weddings/tests/web/*` - Imports atualizados

**Arquivos Criados:**
- `apps/weddings/api/serializers.py` (3 serializers)
- `apps/weddings/api/views.py` (1 ViewSet)
- `apps/weddings/api/permissions.py` (1 permission)
- `apps/weddings/api/urls.py` (router DRF)
- `apps/weddings/tests/api/test_serializers.py` (7 testes)

**Estatísticas:**
- Testes antes: 53 (apenas web)
- Testes depois: 60 (53 web + 7 API)
- Todos passando ✅
- 0 breaking changes (compatibilidade mantida)

**Endpoints API Disponíveis:**
```
GET    /api/v1/weddings/              - Lista casamentos
POST   /api/v1/weddings/              - Cria casamento
GET    /api/v1/weddings/{id}/         - Detalhes
PUT    /api/v1/weddings/{id}/         - Atualiza completo
PATCH  /api/v1/weddings/{id}/         - Atualiza parcial
DELETE /api/v1/weddings/{id}/         - Deleta
PATCH  /api/v1/weddings/{id}/update-status/ - Atualiza status
```

### v2.0 - Lean Testing + ModalContextMixin
- **Paginação:** 12 casamentos por página
- **Índices:** Considerar adicionar no futuro (wedding + status)

---

## Próximos Passos

### Sugerido:
1. Adicionar índices compostos no model (performance)
2. Melhorar admin.py (mais campos, filtros)
3. Considerar soft delete (manter histórico)

---

**Última Atualização:** 21 de novembro de 2025  

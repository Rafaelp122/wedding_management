# App: Items

O app `items` gerencia os itens do orçamento de cada casamento. Permite criar, visualizar, editar e deletar itens de orçamento com categorias, quantidades, preços e fornecedores. Também cria automaticamente contratos associados a cada item.

---

## Status Atual

**Versão:** 3.0 (Refatorado + Índices + Admin Melhorado + ModalContextMixin)  
**Testes:** 57 passando (incluindo teste de transação atômica)  
**Cobertura:** models, forms, views, mixins, querysets

---

## Responsabilidades

-   **Gerenciamento de Itens:** CRUD completo de itens de orçamento
-   **Cálculos Financeiros:** Total por item, total gasto, gastos por categoria
-   **Categorização:** 7 categorias (Local, Buffet, Decoração, etc)
-   **Status:** Rastreamento de progresso (Pendente, Em Andamento, Concluído)
-   **Contratos:** Criação automática de contrato para cada item
-   **Fornecedores:** Registro de fornecedores por item

---

## Arquitetura

### Padrões Aplicados
- **Single Responsibility Principle (SRP):** Cada mixin tem uma responsabilidade
- **Separation of Concerns:** Lógica separada em mixins granulares
- **DRY:** Reutilização de mixins do core (ModalContextMixin)
- **Lean Testing:** Testes focados em comportamento crítico
- **Atomic Transactions:** Garantia de integridade (Item + Contract)

---

## Estrutura de Arquivos

### Arquivos Python

-   **`models.py`:** Modelo `Item` para itens de orçamento
    - **Campos:** name, description, quantity, unit_price, supplier, category, status
    - **FK:** Wedding (cada item pertence a um casamento)
    - **Choices:** 7 categorias, 3 status
    - **Validações:** MinValueValidator(0.00) para preço
    - **Property:** `total_cost` (quantity × unit_price)
    - **Meta (v3.0):**
      - `verbose_name`, `verbose_name_plural`
      - `ordering = ["-created_at"]`
      - `related_name = "items"`
      - **3 índices compostos** para performance:
        - `(wedding, category)` - Filtros de lista
        - `(wedding, status)` - Filtros de status
        - `(-created_at)` - Ordenação por data

-   **`querysets.py`:** QuerySet personalizado com agregações
    - `total_spent()` - Soma total gasto (cálculo no banco)
    - `category_expenses()` - Gastos agrupados por categoria
    - `apply_search(q)` - Busca por nome (istartswith)
    - `apply_sort(sort_option)` - Ordenação via whitelist
    - **Performance:** Usa `ExpressionWrapper` e `F()` para cálculos no SQL

-   **`forms.py`:** Formulário `ItemForm` com validações
    - **Validações:**
      - Quantity > 0 (com logging)
      - Price >= 0 (com logging)
    - **Widgets:**
      - min="1" para quantity
      - min="0" step="0.01" para unit_price
      - rows=3 para description
    - **UX:** Placeholders dinâmicos via helper

-   **`mixins.py`:** Arquitetura granular com 8 mixins
    - **Segurança:**
      - `ItemWeddingContextMixin` - Gatekeeper multicamadas
        - Valida autenticação antes de qualquer query
        - Dois caminhos de carregamento (via wedding_id ou pk)
        - Select_related para evitar N+1
        - Logging de tentativas não autorizadas
      - `ItemPlannerSecurityMixin` - Filtro adicional (get_queryset)
    
    - **Layout:**
      - `ItemFormLayoutMixin` - Define layout do formulário
        - Dicionário de classes CSS por campo
        - Ícones FontAwesome por campo
        - Assume `self.wedding` no contexto
    
    - **Query:**
      - `ItemQuerysetMixin` - Monta queryset base
        - Filtra por wedding automaticamente
        - Aplica search e sort via QuerySet methods
        - Parâmetros explícitos (não pega request.GET)
    
    - **Paginação:**
      - `ItemPaginationContextMixin` - Paginação completa
        - 6 itens por página
        - Elided page range (...1 2 [3] 4 5...)
        - Preserva filtros (search, category, sort)
        - Logging de debug
    
    - **HTMX:**
      - `ItemHtmxListResponseMixin` - Respostas HTMX
        - Extrai params do header HX-Current-Url
        - Injeta variáveis de paginação
        - Helper `render_item_list_response()`
    
    - **Composição:**
      - `ItemListActionsMixin` - Agrupa funcionalidades
        - Herda QuerysetMixin + HtmxResponseMixin
        - Padrão Facade

-   **`views.py`:** Class-Based Views com mixins do core
    - **`ItemListView`:** Lista com dual-mode rendering
      - F5/primeiro acesso: aba completa
      - HTMX filtro/paginação: só o container
      - HTMX troca de aba: aba completa
      - Diferencia pelo HX-Target
    
    - **`AddItemView`:** Criação com transação atômica (v3.0)
      - Usa `ModalContextMixin` do core
      - `transaction.atomic()` garante Item + Contract juntos
      - Teste de rollback validado
      - Logging completo
    
    - **`EditItemView`:** Edição com modal
      - Usa `ModalContextMixin` do core
      - Simples e direto
    
    - **`UpdateItemStatusView`:** Mudança de status
      - Validação de status via whitelist
      - Logging antes/depois (auditoria)
    
    - **`ItemDeleteView`:** Exclusão com confirmação
      - Modal de confirmação
      - Captura repr ANTES de deletar
      - Logging completo

-   **`urls.py`:** Rotas RESTful
    - `/<wedding_id>/items/partial/` - Lista
    - `/<wedding_id>/items/add/` - Criar
    - `/edit-item/<pk>/` - Editar
    - `/delete-item/<pk>/` - Deletar
    - `/update-status/<pk>/` - Atualizar status

-   **`admin.py`:** Interface administrativa (v3.0 - Melhorada)
    - **Campos visíveis:** id, name, category, status, quantity, unit_price, total_cost_display, supplier, wedding
    - **Busca:** name, description, supplier
    - **Filtros:** category, status, wedding
    - **Readonly:** total_cost_display, created_at, updated_at
    - **UX:** 25 itens por página, date_hierarchy
    - **Formatação:** Total em R$ com separador de milhares

### Testes (`tests/`)

- **`test_models.py` (5 testes):**
  - Property total_cost
  - Representação em string
  - Validação de quantity positiva
  - Validação de unit_price não negativo
  - Cascade de deleção

- **`test_querysets.py` (7 testes):**
  - Cálculo total_spent
  - Empty queryset retorna 0
  - Agregação por categoria
  - Busca por nome
  - Ordenação customizada
  - Respeito a filter chaining
  - Ordenação por status

- **`test_forms.py` (9 testes):**
  - Form válido com dados corretos
  - Quantity zero/negativa inválida
  - Price negativo inválido
  - Widgets attributes (min, step, rows)
  - Logging de erros de validação
  - Integração: form.save() cria no banco

- **`test_mixins.py` (13 testes):**
  - **Segurança (5 testes):**
    - Load por wedding_id sucesso
    - Load por wedding_id 404 (usuário errado)
    - Load por pk sucesso
    - Load por pk 403 (planner errado)
    - Load por pk 404 (item inexistente)
  - **Query (3 testes):**
    - Filtra por wedding
    - Filtra por categoria
    - Busca integrada
  - **Paginação (2 testes):**
    - Divide em páginas
    - Preserva variáveis de contexto
  - **HTMX (2 testes):**
    - Bridge de parâmetros
    - Triggers customizados
  - **Composição (1 teste):**
    - Herança correta do Facade

- **`test_views.py` (17 testes + 1 novo):**
  - **ItemListView (5 testes):**
    - Full page load
    - HTMX partial load
    - Outro usuário não acessa
    - Integração com search
    - Integração com sort
  - **AddItemView (4 testes):**
    - GET renderiza modal
    - POST válido cria Item + Contract
    - POST inválido retorna erros
    - **NOVO (v3.0):** Teste de rollback de transação
  - **UpdateItemStatusView (3 testes):**
    - POST atualiza status
    - GET não permitido (405)
    - Status inválido retorna 400
  - **EditItemView (3 testes):**
    - GET renderiza modal preenchido
    - POST válido atualiza
    - POST inválido retorna erros
  - **ItemDeleteView (2 testes):**
    - GET renderiza confirmação
    - POST deleta item
  - **Segurança (2 testes):**
    - Não pode adicionar em wedding de outro user
    - Usuário anônimo redirecionado para login

- **`test_urls.py` (5 testes):**
  - Resolução de todas as URLs

### Templates (`templates/items/`)

-   **`item_list.html`:** Aba de itens com filtros
-   **`partials/`:** Fragmentos HTMX
    -   `_list_and_pagination.html` - Lista + paginação
    -   `_item_card.html` - Card de item individual

---

## Segurança

- **Autenticação:** LoginRequiredMixin em todas as views
- **Autorização:** ItemWeddingContextMixin - segurança multicamadas
  - Checa autenticação antes de queries
  - Valida ownership em 2 caminhos
  - Select_related previne N+1
  - Logging de tentativas não autorizadas
- **Validação:** Quantity > 0, Price >= 0
- **Transação Atômica (v3.0):** Item + Contract criados juntos
- **Códigos HTTP corretos:** 400, 403, 404

---

## Performance (v3.0)

- **3 índices compostos no banco:**
  - `(wedding, category)` - Filtros de lista
  - `(wedding, status)` - Filtros de status
  - `(-created_at)` - Ordenação por data
- **Queries otimizadas:** `select_related('wedding__planner')`
- **Cálculos no banco:** `total_spent()` usa SQL aggregate
- **Busca com índice:** `istartswith` pode usar índice (PostgreSQL)
- **Paginação:** 6 itens por página

---

## Melhorias Recentes (v3.0)

### 1. Transação Atômica:
- `transaction.atomic()` em AddItemView
- Garante integridade: Item + Contract juntos ou nenhum
- Teste de rollback validado

### 2. Índices de Performance:
- 3 índices compostos criados
- Migration aplicada

### 3. Admin Melhorado:
- 9 campos visíveis (vs 6 antes)
- Busca em 3 campos (vs 1 antes)
- Total formatado em R$
- Date hierarchy
- Campos readonly protegidos

### 4. Refatoração com ModalContextMixin:
- Uso de mixin genérico do core
- Eliminadas ~20 linhas duplicadas
- DRY: modal context em 1 lugar só

### 5. related_name no FK:
- `wedding.items.all()` agora funciona
- Queries reversas facilitadas

---

## Próximos Passos (Futuro)

### Considerando:
1. **Supplier como model separado** (aguardando decisão da equipe)
   - Normalização de dados
   - Autocomplete de fornecedores
   - Relatórios por fornecedor
2. **Busca full-text em description**
3. **Soft delete** (manter histórico)
4. **Remover null=True de wedding FK** (+ data migration)

---

## Integrações

- **apps.contracts:** Criação automática de Contract para cada Item
- **apps.weddings:** FK para Wedding (cada item pertence a um casamento)
- **apps.core.mixins:** Reutiliza ModalContextMixin, BaseHtmxResponseMixin

---

**Última Atualização:** 21 de novembro de 2025  
**Versão:** 3.0 - Transação Atômica + Índices + Admin + ModalContextMixin

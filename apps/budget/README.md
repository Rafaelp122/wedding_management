# App: Budget

O app `budget` fornece visualização consolidada do orçamento de cada casamento. Exibe gastos totais, saldo disponível e distribuição de despesas por categoria em uma interface visual com gradientes coloridos.

---

## Status Atual

**Versão:** 1.0  
**Testes:** 6 passando  
**Cobertura:** views, urls, cálculos financeiros, segurança  
**Tipo:** Read-Only View (não cria entidades próprias)

---

## Responsabilidades

-   **Consolidação Financeira:** Agrega dados de `Item` para exibir visão geral do orçamento
-   **Cálculos Automáticos:** Total gasto, saldo disponível, percentuais
-   **Distribuição por Categoria:** Gastos agrupados e ordenados por valor (maior → menor)
-   **Visualização:** Interface com gradientes coloridos para cada categoria
-   **Segurança:** Acesso restrito ao planner dono do casamento

---

## Arquitetura

### Padrões Aplicados
- **Read-Only Pattern:** Não possui models próprios, apenas agrega dados
- **Security First:** Validação de ownership antes de qualquer query
- **DRY:** Reutiliza querysets de `Item` (total_spent, category_expenses)
- **Performance:** Cálculos feitos no banco via annotate/aggregate

### Filosofia
Este app é **lean by design**: não cria tabelas, não tem CRUD, não tem forms. Apenas **lê e exibe** dados já existentes de forma consolidada.

---

## Estrutura de Arquivos

### Arquivos Python

-   **`models.py`:** Vazio (não possui models próprios)

-   **`views.py`:** Uma única view otimizada
    - **`BudgetPartialView` (TemplateView + LoginRequiredMixin):**
        - **Input:** `wedding_id` via URL
        - **Segurança:** `get_object_or_404` garante ownership
        - **Cálculos:**
            - `total_budget` - Orçamento do casamento (Wedding.budget)
            - `current_spent` - Soma total gasta (Item.total_spent())
            - `available_balance` - Saldo (budget - spent)
        - **Distribuição:**
            - Chama `Item.category_expenses()` (já ordenado por gasto DESC)
            - Mapeia códigos para nomes legíveis (DECOR → "Decoração")
            - Atribui gradiente visual de `GRADIENTS` (cores rotacionadas)
        - **Output:** Contexto completo para template

-   **`urls.py`:** Rota única
    - `partial/<int:wedding_id>/` - Visualização do orçamento
    - Namespace: `budget`
    - Name: `partial_budget`

### Testes (`tests/`)

- **`test_views.py` (5 testes):**
  - **`test_financial_calculations`:** Valida cálculos de budget, spent, balance
  - **`test_category_distribution_logic`:** Verifica agrupamento, nomes e ordenação
  - **`test_empty_state_calculations`:** Casamento sem itens não quebra (spent=0)
  - **`test_security_access_control`:** Anônimo → 302, Hacker → 404
  - **`test_over_budget_calculation`:** Saldo negativo quando gasto > orçamento

- **`test_urls.py` (1 teste):**
  - Resolução correta da URL `partial_budget`

### Templates (`templates/budget/`)

-   **`budget_overview.html`:** Template principal
    - Cards de resumo financeiro (orçamento, gasto, saldo)
    - Lista de categorias com:
        - Barra de progresso com gradiente
        - Nome da categoria
        - Valor gasto formatado

---

## Fluxo de Dados

```
Wedding.budget (10.000)
         ↓
    [Items do Wedding]
    - Buffet: R$ 5.000
    - Decoração: R$ 2.000
    - Outros: R$ 500
         ↓
  [Item.total_spent()] → 7.500
         ↓
  [Cálculos na View]
  - current_spent: 7.500
  - available_balance: 2.500
  - distributed_expenses: [
      {category: "Buffet", value: 5000, gradient: "..."},
      {category: "Decoração", value: 2000, gradient: "..."},
      {category: "Outros", value: 500, gradient: "..."}
    ]
         ↓
  [Template Renderizado]
```

---

## Segurança

- **Autenticação:** `LoginRequiredMixin` obrigatório
- **Autorização:** `get_object_or_404(Wedding, planner=request.user)`
- **Isolamento:** Usuário só vê orçamento de seus próprios casamentos
- **Validação:** 404 se casamento não existir ou pertencer a outro usuário

---

## Performance

- **Zero queries N+1:** Usa `select_related` e `prefetch_related` onde necessário
- **Cálculos no banco:** `total_spent()` e `category_expenses()` usam SQL aggregate
- **Cache potencial:** View é stateless, pode adicionar cache no futuro
- **Lazy evaluation:** QuerySets só são executados no template

---

## Dependências

### Apps Relacionados:
- **`apps.items`:** Fonte de dados (Item.total_spent, Item.category_expenses)
- **`apps.weddings`:** Validação de ownership (Wedding.planner)
- **`apps.core.constants`:** `GRADIENTS` para visualização colorida

### Models Utilizados:
- `Wedding` - Para validação de ownership e budget total
- `Item` - Para cálculos de gastos e distribuição

---

## Exemplos de Uso

### 1. Visualizar Orçamento no Template:
```django
<!-- Em wedding_detail.html -->
<div hx-get="{% url 'budget:partial_budget' wedding.id %}" 
     hx-target="#budget-content" 
     hx-trigger="load">
  <!-- Conteúdo carregado via HTMX -->
</div>
```

### 2. Acessar via URL Direta:
```python
# URL: /budget/partial/123/
# Resposta: HTML renderizado com dados do wedding_id=123
```

---

## Limitações Conhecidas

1. **Não possui CRUD:** App é read-only por design
2. **Não possui models:** Depende 100% de `Item` e `Wedding`
3. **Não possui API:** Apenas interface web/HTMX
4. **Gradientes fixos:** Número limitado de cores (rotaciona se >7 categorias)

---

## Melhorias Futuras (Considerando)

### Curto Prazo:
1. **Gráficos interativos:** Chart.js ou similar para visualização
2. **Export PDF:** Gerar relatório de orçamento em PDF
3. **Comparação temporal:** Histórico de gastos ao longo do tempo

### Longo Prazo:
1. **API REST:** Endpoint JSON para integrações
2. **Budget alerts:** Notificar quando próximo do limite
3. **Projeções:** Estimar gastos futuros baseado em padrões

---

## Testes

### Executar testes do app:
```bash
# Via pytest (recomendado)
pytest apps/budget/tests/ -v

# Via Django test runner
python manage.py test apps.budget
```

**Status Atual:** ✅ 6/6 testes passando

### Cobertura de Testes:
- ✅ Cálculos financeiros (budget, spent, balance)
- ✅ Distribuição por categoria (agrupamento, ordenação)
- ✅ Estado vazio (sem itens)
- ✅ Orçamento estourado (saldo negativo)
- ✅ Segurança (anônimo, ownership)
- ✅ Resolução de URLs

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** 1.0 - Read-Only Budget Overview

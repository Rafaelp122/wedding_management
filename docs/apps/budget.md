# Budget - Documentação Técnica Completa

Visualização consolidada do orçamento com distribuição por categorias e gradientes coloridos.

**Versão:** 1.0  
**Status:** ✅ 6 testes passando  
**Tipo:** Read-Only View (não possui models próprios)  

---

## Índice

- [Visão Geral](#visão-geral)
- [Filosofia de Design](#filosofia-de-design)
- [Arquitetura](#arquitetura)
- [Views](#views)
- [Fluxo de Dados](#fluxo-de-dados)
- [Segurança](#segurança)
- [Performance](#performance)
- [Testes](#testes)

---

## Visão Geral

O app `budget` fornece **visualização consolidada do orçamento** de cada casamento. É um app **lean by design**: não possui models, não tem CRUD, não tem forms. Apenas **lê e exibe** dados já existentes.

### Responsabilidades

-   **Consolidação Financeira:** Agrega dados de `Item` para visão geral
-   **Cálculos Automáticos:** Total gasto, saldo disponível, percentuais
-   **Distribuição por Categoria:** Gastos agrupados e ordenados (maior → menor)
-   **Visualização:** Interface com gradientes coloridos
-   **Segurança:** Acesso restrito ao planner dono do casamento

---

## Filosofia de Design

### Read-Only Pattern

```
┌─────────────────────────────────┐
│   Budget App (Read-Only)        │
│                                   │
│   [NO MODELS]                    │
│   [NO FORMS]                     │
│   [NO CRUD]                      │
│                                   │
│   APENAS:                        │
│   • Lê dados de Item             │
│   • Calcula totais               │
│   • Renderiza visualização       │
└─────────────────────────────────┘
```

**Benefícios:**
- ✅ Simplicidade: Menos código, menos bugs
- ✅ Performance: Sem tabelas adicionais
- ✅ Manutenção: Sem migrations, sem schemas
- ✅ Testabilidade: Testes focados em cálculos e segurança

---

## Arquitetura

### Estrutura de Arquivos

```
apps/budget/
├── models.py          # Vazio (não possui models)
├── views.py           # 1 única view (BudgetPartialView)
├── urls.py            # 1 única rota
└── tests/
    ├── test_views.py  # 5 testes (cálculos, segurança)
    └── test_urls.py   # 1 teste (resolução de rota)
```

### Padrões Aplicados

- **Read-Only Pattern:** Nenhuma escrita no banco
- **Security First:** Validação de ownership antes de qualquer query
- **DRY:** Reutiliza querysets de `Item` (total_spent, category_expenses)
- **Performance:** Todos os cálculos feitos no banco via annotate/aggregate

---

## Views

### BudgetPartialView

**Única view do app:**

```python
class BudgetPartialView(LoginRequiredMixin, TemplateView):
    template_name = "budget/budget_overview.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Validar ownership
        wedding_id = self.kwargs["wedding_id"]
        wedding = get_object_or_404(
            Wedding.objects.select_related("planner"),
            id=wedding_id,
            planner=self.request.user  # Segurança
        )
        
        # 2. Cálculos financeiros
        total_budget = wedding.budget  # Ex: 10.000
        current_spent = Item.objects.filter(wedding=wedding).total_spent()  # Ex: 7.500
        available_balance = total_budget - current_spent  # Ex: 2.500
        
        # 3. Distribuição por categoria
        category_expenses = Item.objects.filter(wedding=wedding).category_expenses()
        # Resultado: [
        #   {'category': 'BUFFET', 'total': Decimal('5000.00')},
        #   {'category': 'DECOR', 'total': Decimal('2000.00')},
        #   {'category': 'OTHER', 'total': Decimal('500.00')}
        # ]
        
        # 4. Mapear códigos para nomes legíveis
        distributed_expenses = []
        for i, expense in enumerate(category_expenses):
            distributed_expenses.append({
                "category": CATEGORY_DISPLAY_NAMES.get(expense["category"], "Outros"),
                "value": expense["total"],
                "gradient": GRADIENTS[i % len(GRADIENTS)],  # Rotaciona cores
            })
        
        context.update({
            "wedding": wedding,
            "total_budget": total_budget,
            "current_spent": current_spent,
            "available_balance": available_balance,
            "distributed_expenses": distributed_expenses,
        })
        
        return context
```

**Constantes:**

```python
CATEGORY_DISPLAY_NAMES = {
    "VENUE": "Local",
    "BUFFET": "Buffet",
    "DECOR": "Decoração",
    "PHOTO": "Fotografia",
    "MUSIC": "Música",
    "DRESS": "Vestimenta",
    "OTHER": "Outros",
}

GRADIENTS = [
    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
    "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
]
```

---

## Fluxo de Dados

```
┌─────────────────────────────────┐
│   Wedding.budget = 10.000       │
└───────────┬─────────────────────┘
            │
            ↓
┌─────────────────────────────────┐
│   Items do Wedding:             │
│   • Buffet: R$ 5.000            │
│   • Decoração: R$ 2.000         │
│   • Outros: R$ 500              │
└───────────┬─────────────────────┘
            │
            ↓
┌─────────────────────────────────┐
│   Item.total_spent()            │
│   = 7.500 (SQL aggregate)       │
└───────────┬─────────────────────┘
            │
            ↓
┌─────────────────────────────────┐
│   Cálculos na View:             │
│   • current_spent: 7.500        │
│   • available_balance: 2.500    │
│   • distributed_expenses: [     │
│       {category: "Buffet",      │
│        value: 5000,             │
│        gradient: "..."},        │
│       ...                       │
│     ]                           │
└───────────┬─────────────────────┘
            │
            ↓
┌─────────────────────────────────┐
│   Template Renderizado          │
│   (Cards + Barras de Progresso) │
└─────────────────────────────────┘
```

---

## Segurança

### Validação de Ownership

```python
wedding = get_object_or_404(
    Wedding.objects.select_related("planner"),
    id=wedding_id,
    planner=self.request.user  # 🔒 Segurança
)
```

**Proteções:**
1. **Autenticação:** `LoginRequiredMixin` obrigatório
2. **Autorização:** `get_object_or_404` com `planner=request.user`
3. **Isolamento:** Usuário só vê orçamento de seus próprios casamentos
4. **Validação:** 404 se casamento não existir ou pertencer a outro usuário

**Testes de Segurança:**

```python
def test_security_access_control(self):
    """Anônimo → 302, Hacker → 404"""
    # Anônimo
    self.client.logout()
    response = self.client.get(self.url)
    assert response.status_code == 302  # Redirect para login
    
    # Hacker (outro usuário)
    hacker = User.objects.create_user(username="hacker", password="123")
    self.client.force_login(hacker)
    response = self.client.get(self.url)
    assert response.status_code == 404  # Wedding não encontrado
```

---

## Performance

### Otimizações

**1. Cálculos no Banco:**

```python
# ✅ Bom: SQL aggregate (1 query)
current_spent = Item.objects.filter(wedding=wedding).total_spent()

# ❌ Ruim: Python loop (N queries)
current_spent = sum(item.total_cost for item in items)
```

**2. Select Related:**

```python
# ✅ Bom: 1 query
wedding = Wedding.objects.select_related("planner").get(pk=1)

# ❌ Ruim: 2 queries
wedding = Wedding.objects.get(pk=1)
planner = wedding.planner  # Query adicional
```

**3. QuerySets Reutilizados:**

```python
# Reutiliza lógica de apps.items
Item.objects.total_spent()           # Do ItemQuerySet
Item.objects.category_expenses()     # Do ItemQuerySet
```

**4. Cache Potencial:**

```python
# Futuro: adicionar cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache por 5 minutos
class BudgetPartialView(TemplateView):
    pass
```

---

## Testes

### Estrutura (6 testes)

**test_views.py (5 testes):**

1. **`test_financial_calculations`**
   ```python
   # Valida: budget, spent, balance
   assert response.context["total_budget"] == Decimal("10000.00")
   assert response.context["current_spent"] == Decimal("7500.00")
   assert response.context["available_balance"] == Decimal("2500.00")
   ```

2. **`test_category_distribution_logic`**
   ```python
   # Verifica: agrupamento, nomes, ordenação
   expenses = response.context["distributed_expenses"]
   assert len(expenses) == 3
   assert expenses[0]["category"] == "Buffet"  # Maior valor primeiro
   assert expenses[0]["value"] == Decimal("5000.00")
   ```

3. **`test_empty_state_calculations`**
   ```python
   # Casamento sem itens não quebra
   assert response.context["current_spent"] == Decimal("0.00")
   assert response.context["available_balance"] == Decimal("10000.00")
   ```

4. **`test_over_budget_calculation`**
   ```python
   # Saldo negativo quando gasto > orçamento
   assert response.context["available_balance"] < 0
   ```

5. **`test_security_access_control`**
   ```python
   # Anônimo → 302, Hacker → 404
   ```

**test_urls.py (1 teste):**

6. **`test_partial_budget_url_resolves`**
   ```python
   # Resolução correta da URL
   ```

### Executar Testes

```bash
# Via pytest
pytest apps/budget/tests/ -v

# Via Django
python manage.py test apps.budget

# Com cobertura
pytest apps/budget --cov=apps.budget --cov-report=html
```

**Status:** ✅ 6/6 passando

---

## Dependências

### Apps Relacionados

- **`apps.items`:** Fonte de dados (Item.total_spent, Item.category_expenses)
- **`apps.weddings`:** Validação de ownership (Wedding.planner)
- **`apps.core.constants`:** `GRADIENTS` para visualização colorida

### Models Utilizados

- `Wedding` - Para validação de ownership e budget total
- `Item` - Para cálculos de gastos e distribuição

---

## Exemplos de Uso

### 1. Visualizar no Template (HTMX)

```html
<!-- Em wedding_detail.html -->
<div hx-get="{% url 'budget:partial_budget' wedding.id %}" 
     hx-target="#budget-content" 
     hx-trigger="load">
  <p>Carregando orçamento...</p>
</div>
```

### 2. Acessar via URL Direta

```
GET /budget/partial/123/
→ Resposta: HTML renderizado com dados do wedding_id=123
```

### 3. Integrar em Dashboard

```python
# Em outra view
budget_url = reverse("budget:partial_budget", args=[wedding.id])
```

---

## Limitações Conhecidas

1. **Não possui CRUD:** App é read-only por design
2. **Não possui models:** Depende 100% de `Item` e `Wedding`
3. **Não possui API:** Apenas interface web/HTMX
4. **Gradientes fixos:** Número limitado de cores (7), rotaciona se mais categorias

---

## Melhorias Futuras

### Curto Prazo

1. **Gráficos interativos:**
   - Chart.js ou ApexCharts
   - Pizza/barra para distribuição

2. **Export PDF:**
   - Gerar relatório de orçamento
   - xhtml2pdf ou WeasyPrint

3. **Comparação temporal:**
   - Histórico de gastos ao longo do tempo
   - Linha do tempo de despesas

### Longo Prazo

1. **API REST:**
   - Endpoint JSON para integrações
   - Formato: `GET /api/v1/budgets/{wedding_id}/`

2. **Budget alerts:**
   - Notificar quando próximo do limite (ex: 90%)
   - E-mail ou notificação in-app

3. **Projeções:**
   - Estimar gastos futuros baseado em padrões
   - Machine Learning para previsões

4. **Multi-moeda:**
   - Suporte a outras moedas além de R$
   - Conversão automática

---

## Templates

### budget_overview.html

```html
<div class="budget-cards">
  <!-- Card: Orçamento Total -->
  <div class="card">
    <h3>Orçamento Total</h3>
    <p class="value">R$ {{ total_budget|floatformat:2 }}</p>
  </div>
  
  <!-- Card: Gasto Atual -->
  <div class="card">
    <h3>Gasto Atual</h3>
    <p class="value">R$ {{ current_spent|floatformat:2 }}</p>
  </div>
  
  <!-- Card: Saldo Disponível -->
  <div class="card {% if available_balance < 0 %}over-budget{% endif %}">
    <h3>Saldo Disponível</h3>
    <p class="value">R$ {{ available_balance|floatformat:2 }}</p>
  </div>
</div>

<!-- Distribuição por Categoria -->
<div class="category-distribution">
  <h2>Distribuição por Categoria</h2>
  {% for expense in distributed_expenses %}
  <div class="category-item">
    <div class="category-bar" 
         style="background: {{ expense.gradient }}; width: {{ expense.percentage }}%;">
    </div>
    <p>{{ expense.category }}: R$ {{ expense.value|floatformat:2 }}</p>
  </div>
  {% endfor %}
</div>
```

---

## Rotas

### urls.py

```python
from django.urls import path
from apps.budget.views import BudgetPartialView

app_name = "budget"

urlpatterns = [
    path("partial/<int:wedding_id>/", BudgetPartialView.as_view(), name="partial_budget"),
]
```

**URL completa:**
```
/budget/partial/123/
```

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** 1.0 - Read-Only Budget Overview

# Items - Documentação Técnica Completa

Sistema de gerenciamento de itens de orçamento com transações atômicas e índices de performance.

**Versão:** 3.0  
**Status:** ✅ 57 testes passando  
**Cobertura:** models, forms, views, mixins, querysets  

---

## Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Models & QuerySets](#models--querysets)
- [Forms](#forms)
- [Mixins](#mixins)
- [Views](#views)
- [Segurança](#segurança)
- [Performance](#performance)
- [Testes](#testes)
- [Integrações](#integrações)

---

## Visão Geral

O app `items` gerencia os **itens do orçamento** de cada casamento. Cada item representa um produto ou serviço contratado, com informações de quantidade, preço, fornecedor e categoria.

### Responsabilidades

-   **CRUD Completo:** Criar, visualizar, editar e deletar itens
-   **Cálculos Financeiros:** Total por item, total gasto, gastos por categoria
-   **Categorização:** 7 categorias (Local, Buffet, Decoração, Fotografia, Música, Vestimenta, Outros)
-   **Status:** Rastreamento de progresso (Pendente, Em Andamento, Concluído)
-   **Contratos:** Criação automática de contrato para cada item (transação atômica)
-   **Fornecedores:** Registro de fornecedores por item

---

## Arquitetura

### Padrões Aplicados

- **Single Responsibility Principle (SRP):** Cada mixin tem uma única responsabilidade
- **Separation of Concerns:** Lógica separada em mixins granulares (8 mixins)
- **DRY:** Reutilização de mixins do core (`ModalContextMixin`)
- **Lean Testing:** Testes focados em comportamento crítico
- **Atomic Transactions:** Garantia de integridade (Item + Contract criados juntos)
- **Performance First:** 3 índices compostos para queries otimizadas

### Filosofia

> "Um item só existe se tiver um contrato associado. Se falhar, rollback total."

Essa regra garante integridade de dados e evita estados inconsistentes.

---

## Models & QuerySets

### Item Model

**Campos principais:**

```python
class Item(BaseModel):
    # Relações
    wedding = ForeignKey(Wedding, on_delete=CASCADE, related_name="items")
    
    # Dados do item
    name = CharField(max_length=200)
    description = TextField(blank=True)
    quantity = PositiveIntegerField(default=1)
    unit_price = DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    supplier = CharField(max_length=200, blank=True)
    
    # Categorização
    category = CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = CharField(max_length=50, choices=STATUS_CHOICES, default="PENDING")
```

**Categorias disponíveis:**
- `VENUE` - Local
- `BUFFET` - Buffet
- `DECOR` - Decoração
- `PHOTO` - Fotografia
- `MUSIC` - Música
- `DRESS` - Vestimenta
- `OTHER` - Outros

**Status disponíveis:**
- `PENDING` - Pendente
- `IN_PROGRESS` - Em andamento
- `COMPLETED` - Concluído

**Property:**

```python
@property
def total_cost(self):
    """Custo total do item (quantity × unit_price)"""
    return self.quantity * self.unit_price
```

**Meta (v3.0 - Performance):**

```python
class Meta:
    ordering = ["-created_at"]
    verbose_name = "Item de Orçamento"
    verbose_name_plural = "Itens de Orçamento"
    
    # 3 índices compostos para performance
    indexes = [
        Index(fields=["wedding", "category"]),  # Filtros de lista
        Index(fields=["wedding", "status"]),    # Filtros de status
        Index(fields=["-created_at"]),          # Ordenação por data
    ]
```

### ItemQuerySet

**Métodos disponíveis:**

```python
Item.objects
    .total_spent()               # Soma total gasto (SQL aggregate)
    .category_expenses()         # Gastos por categoria (agrupado)
    .apply_search(q)             # Busca por nome (istartswith)
    .apply_sort(option)          # Ordenação via whitelist
```

**Implementação:**

```python
def total_spent(self):
    """Calcula total gasto usando SQL aggregate"""
    from django.db.models import F, DecimalField, Sum
    from django.db.models.functions import Coalesce
    
    total = self.annotate(
        total_cost=ExpressionWrapper(
            F("quantity") * F("unit_price"),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    ).aggregate(
        total=Coalesce(Sum("total_cost"), Decimal("0.00"))
    )
    return total["total"]

def category_expenses(self):
    """Retorna gastos agrupados por categoria, ordenados DESC"""
    return self.values("category").annotate(
        total=Sum(F("quantity") * F("unit_price"))
    ).order_by("-total")
```

---

## Forms

### ItemForm

**Validações de negócio:**

```python
class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description", "quantity", "unit_price", "supplier", "category", "status"]
        widgets = {
            "quantity": NumberInput(attrs={"min": "1"}),
            "unit_price": NumberInput(attrs={"min": "0", "step": "0.01"}),
            "description": Textarea(attrs={"rows": 3}),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity and quantity <= 0:
            logger.warning(f"Tentativa de quantity inválida: {quantity}")
            raise ValidationError("Quantidade deve ser maior que zero")
        return quantity
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get("unit_price")
        if unit_price and unit_price < 0:
            logger.warning(f"Tentativa de preço negativo: {unit_price}")
            raise ValidationError("Preço não pode ser negativo")
        return unit_price
```

**UX:**
- Placeholders dinâmicos via helper
- Ícones FontAwesome por campo
- Classes CSS customizadas

---

## Mixins

### Arquitetura Granular (8 Mixins)

**1. ItemWeddingContextMixin** - Gatekeeper de segurança multicamadas

```python
class ItemWeddingContextMixin:
    """
    Valida autenticação e ownership ANTES de qualquer query.
    Dois caminhos de carregamento: wedding_id ou pk.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        
        # Caminho 1: Via wedding_id
        if "wedding_id" in kwargs:
            self.wedding = get_object_or_404(
                Wedding.objects.select_related("planner"),
                id=kwargs["wedding_id"],
                planner=request.user
            )
        
        # Caminho 2: Via pk (item_id)
        elif "pk" in kwargs:
            item = get_object_or_404(
                Item.objects.select_related("wedding__planner"),
                pk=kwargs["pk"]
            )
            if item.wedding.planner != request.user:
                logger.warning(f"Acesso não autorizado: {request.user} tentou acessar item #{item.pk}")
                raise PermissionDenied("Você não tem permissão para acessar este item")
            self.wedding = item.wedding
        
        return super().dispatch(request, *args, **kwargs)
```

**2. ItemPlannerSecurityMixin** - Filtro adicional no queryset

```python
class ItemPlannerSecurityMixin:
    def get_queryset(self):
        return Item.objects.filter(wedding__planner=self.request.user)
```

**3. ItemFormLayoutMixin** - Define layout do formulário

```python
class ItemFormLayoutMixin:
    def get_form_layout_config(self):
        return {
            "css_classes": {
                "name": "form-control",
                "quantity": "form-control",
                "unit_price": "form-control",
                # ...
            },
            "icons": {
                "name": "fa-tag",
                "quantity": "fa-hashtag",
                "unit_price": "fa-dollar-sign",
                # ...
            }
        }
```

**4. ItemQuerysetMixin** - Monta queryset com filtros

```python
class ItemQuerysetMixin:
    def build_queryset(self, search=None, category=None, sort=None):
        qs = Item.objects.filter(wedding=self.wedding)
        if search:
            qs = qs.apply_search(search)
        if category:
            qs = qs.filter(category=category)
        if sort:
            qs = qs.apply_sort(sort)
        return qs
```

**5. ItemPaginationContextMixin** - Paginação completa

```python
class ItemPaginationContextMixin:
    def paginate_items(self, queryset):
        paginator = Paginator(queryset, 6)  # 6 itens por página
        page_obj = paginator.get_page(self.request.GET.get("page"))
        
        # Elided page range (...1 2 [3] 4 5...)
        page_range = paginator.get_elided_page_range(
            page_obj.number,
            on_each_side=2,
            on_ends=1
        )
        
        return {
            "page_obj": page_obj,
            "page_range": page_range,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
        }
```

**6. ItemHtmxListResponseMixin** - Respostas HTMX

```python
class ItemHtmxListResponseMixin:
    def render_item_list_response(self, context):
        hx_current_url = self.request.headers.get("HX-Current-Url", "")
        # Extrai params do header
        # Injeta variáveis de paginação
        return render(self.request, "items/partials/_list_and_pagination.html", context)
```

**7. ItemListActionsMixin** - Facade (agrupa funcionalidades)

```python
class ItemListActionsMixin(
    ItemQuerysetMixin,
    ItemHtmxListResponseMixin
):
    """Padrão Facade: agrupa QuerysetMixin + HtmxResponseMixin"""
    pass
```

---

## Views

### ItemListView - Lista com dual-mode rendering

```python
class ItemListView(
    LoginRequiredMixin,
    ItemWeddingContextMixin,
    ItemPaginationContextMixin,
    ItemListActionsMixin,
    TemplateView
):
    def get(self, request, wedding_id):
        hx_target = request.headers.get("HX-Target", "")
        
        # Build queryset com filtros
        queryset = self.build_queryset(
            search=request.GET.get("q"),
            category=request.GET.get("category"),
            sort=request.GET.get("sort", "name")
        )
        
        # Paginar
        context = self.paginate_items(queryset)
        context["wedding"] = self.wedding
        
        # Dual-mode rendering
        if hx_target == "items-container":
            # HTMX filtro/paginação: só o container
            return self.render_item_list_response(context)
        else:
            # F5/primeiro acesso: aba completa
            return render(request, "items/item_list.html", context)
```

### AddItemView - Criação com transação atômica (v3.0)

```python
from django.db import transaction

class AddItemView(
    LoginRequiredMixin,
    ItemWeddingContextMixin,
    ModalContextMixin,  # Do core
    CreateView
):
    form_class = ItemForm
    template_name = "items/partials/_item_form.html"
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # 1. Salva o item
                self.object = form.save(commit=False)
                self.object.wedding = self.wedding
                self.object.save()
                
                logger.info(f"Item criado: {self.object}")
                
                # 2. Cria o contrato associado
                from apps.contracts.models import Contract
                contract = Contract.objects.create(
                    item=self.object,
                    status="WAITING_PLANNER"
                )
                
                logger.info(f"Contrato criado: {contract}")
                
                return HttpResponse(status=200, headers={"HX-Trigger": "itemAdded"})
        
        except Exception as e:
            logger.error(f"Erro ao criar item: {e}")
            return self.form_invalid(form)
```

**Teste de Rollback:**

```python
def test_add_item_rollback_on_contract_creation_failure(self):
    """Se contrato falhar, item NÃO deve ser criado"""
    with patch("apps.contracts.models.Contract.objects.create") as mock_create:
        mock_create.side_effect = Exception("Simulated error")
        
        response = self.client.post(url, data)
        
        # Item NÃO foi criado
        assert Item.objects.count() == 0
```

### UpdateItemStatusView - Mudança de status

```python
class UpdateItemStatusView(
    LoginRequiredMixin,
    ItemWeddingContextMixin,
    UpdateView
):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        new_status = request.POST.get("status")
        
        if new_status not in ["PENDING", "IN_PROGRESS", "COMPLETED"]:
            return JsonResponse({"error": "Status inválido"}, status=400)
        
        old_status = item.status
        item.status = new_status
        item.save()
        
        logger.info(f"Status atualizado: {item} ({old_status} → {new_status})")
        return JsonResponse({"status": "success"})
```

### EditItemView - Edição com modal

### ItemDeleteView - Exclusão com confirmação

---

## Segurança

### Multicamadas de Proteção

1. **LoginRequiredMixin** - Autenticação obrigatória
2. **ItemWeddingContextMixin** - Validação de ownership em 2 caminhos
3. **Select_related** - Previne N+1 e garante integridade
4. **Logging** - Auditoria de tentativas não autorizadas
5. **Transação Atômica** - Integridade de dados (Item + Contract)
6. **Códigos HTTP corretos** - 400, 403, 404

### Fluxo de Validação

```
Request
  ↓
LoginRequiredMixin → Autenticado?
  ↓ (sim)
ItemWeddingContextMixin → Dono do wedding?
  ↓ (sim)
View → Processa
  ↓
Response
```

---

## Performance

### Otimizações (v3.0)

**1. Índices Compostos:**

```python
indexes = [
    Index(fields=["wedding", "category"]),  # Filtros de lista
    Index(fields=["wedding", "status"]),    # Filtros de status
    Index(fields=["-created_at"]),          # Ordenação por data
]
```

**Benefícios:**
- Queries 10-100x mais rápidas (dependendo do volume)
- Suporta filtros combinados (wedding + category)
- Suporta ordenação por data

**2. Queries Otimizadas:**

```python
# Com select_related (1 query)
Item.objects.select_related("wedding__planner")

# Sem select_related (N+1 queries)
Item.objects.all()  # ❌ Evitar
```

**3. Cálculos no Banco:**

```python
# ✅ Bom: SQL aggregate
total = Item.objects.total_spent()

# ❌ Ruim: Python loop
total = sum(item.total_cost for item in Item.objects.all())
```

**4. Paginação:**
- 6 itens por página (reduz transferência de dados)
- Elided page range (UX otimizada)

---

## Testes

### Estrutura (57 testes)

- **`test_models.py` (5):** Property, validações, cascade
- **`test_querysets.py` (7):** Aggregates, busca, ordenação
- **`test_forms.py` (9):** Validações, widgets, logging
- **`test_mixins.py` (13):** Segurança (5), query (3), paginação (2), HTMX (2), composição (1)
- **`test_views.py` (18):** CRUD completo, segurança, transação atômica
- **`test_urls.py` (5):** Resolução de rotas

### Executar Testes

```bash
# Todos os testes
pytest apps/items -v

# Apenas models
pytest apps/items/tests/test_models.py -v

# Com cobertura
pytest apps/items --cov=apps.items --cov-report=html
```

**Status:** ✅ 57/57 passando

---

## Integrações

### apps.contracts

**Criação Automática de Contract:**

```python
with transaction.atomic():
    item = Item.objects.create(...)
    contract = Contract.objects.create(item=item)
```

**Cascade Delete:**
- Item deletado → Contract deletado automaticamente

### apps.weddings

**FK Relationship:**

```python
wedding = Wedding.objects.get(pk=1)
items = wedding.items.all()  # related_name="items"
```

### apps.core.mixins

**Reutilização de ModalContextMixin:**

```python
class AddItemView(
    ModalContextMixin,  # Do core
    CreateView
):
    pass
```

---

## Próximos Passos

### Considerando:

1. **Supplier como model separado:**
   - Normalização de dados
   - Autocomplete de fornecedores
   - Relatórios por fornecedor

2. **Busca full-text em description:**
   - Melhor UX para descrições longas

3. **Soft delete:**
   - Manter histórico de itens deletados

4. **Remover null=True de wedding FK:**
   - Data migration para garantir integridade

---

**Última Atualização:** 21 de novembro de 2025  
**Versão:** 3.0 - Transação Atômica + Índices + Admin + ModalContextMixin

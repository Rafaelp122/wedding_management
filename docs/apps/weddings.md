# Weddings - Documentação Técnica Completa

Sistema de gerenciamento de casamentos com arquitetura híbrida (Web + API).

**Versão:** 3.0  
**Status:** ✅ 60 testes passando (53 web + 7 API)  
**Arquitetura:** Híbrida - Django + HTMX + Django REST Framework  

---

## Índice

- [Visão Geral](#visão-geral)
- [Arquitetura Híbrida](#arquitetura-híbrida)
- [Models & QuerySets](#models--querysets)
- [Interface Web](#interface-web)
- [Interface API](#interface-api)
- [Segurança](#segurança)
- [Performance](#performance)
- [Testes](#testes)
- [Migração v2→v3](#migração-v2v3)

---

## Visão Geral

O app `weddings` é o **núcleo da aplicação**, responsável por gerenciar a entidade principal do sistema: o Casamento (`Wedding`).

### Responsabilidades

-   **Gerenciamento de Casamentos:** CRUD completo de casamentos
-   **Interface Web (HTMX):** Interações dinâmicas com Django templates
-   **Interface API (REST):** Endpoints RESTful para integrações externas
-   **Visualização de Detalhes:** Painel central com abas (Orçamento, Contratos, Itens, Calendário)
-   **Listagem com Filtros:** Busca, filtros por status e ordenação

---

## Arquitetura Híbrida

### Filosofia

A **v3.0** introduziu uma **arquitetura híbrida** que separa completamente Web e API em módulos independentes, mas compartilha models e querysets.

**Motivação:**
- **Portfolio:** Demonstrar conhecimento de APIs REST
- **Projeto Integrador:** Comparação entre paradigmas (HTMX vs API)
- **Escalabilidade:** Preparar para apps mobile e integrações

### Estrutura de Pastas

```
apps/weddings/
├── __init__.py            # Lazy imports para compatibilidade
├── models.py              # Compartilhado (Web + API)
├── querysets.py           # Compartilhado (Web + API)
├── admin.py               # Admin Django
├── constants.py           # Configurações globais
│
├── web/                   # Interface Web (Django + HTMX)
│   ├── forms.py          # Formulários Django
│   ├── views.py          # Class-Based Views
│   ├── mixins.py         # Mixins granulares (6)
│   └── urls.py           # Rotas web
│
├── api/                   # Interface API (DRF)
│   ├── serializers.py    # Serializers REST (3)
│   ├── views.py          # ViewSets DRF (1)
│   ├── permissions.py    # Permissões customizadas (1)
│   └── urls.py           # Rotas API
│
└── tests/
    ├── test_models.py     # Testes de models
    ├── test_querysets.py  # Testes de querysets
    ├── web/               # Testes da interface web (53 testes)
    │   ├── test_forms.py
    │   ├── test_views.py
    │   ├── test_mixins.py
    │   └── test_urls.py
    └── api/               # Testes da interface API (7 testes)
        └── test_serializers.py
```

### Padrões de Design

1. **Separation of Concerns** - Web e API isolados
2. **Single Responsibility Principle** - Cada mixin tem uma responsabilidade
3. **DRY** - Models e querysets compartilhados
4. **Facade Pattern** - `WeddingListActionsMixin` agrupa funcionalidades
5. **Mixin Pattern** - Composição de funcionalidades via herança

---

## Models & QuerySets

### Wedding Model

**Campos principais:**

```python
class Wedding(BaseModel):
    groom_name = CharField(max_length=100)
    bride_name = CharField(max_length=100)
    date = DateField()
    location = CharField(max_length=200)
    budget = DecimalField(max_digits=10, decimal_places=2)
    status = CharField(choices=STATUS_CHOICES)
    planner = ForeignKey(User, on_delete=CASCADE)
```

**Status disponíveis:**
- `IN_PROGRESS` - Em andamento
- `COMPLETED` - Concluído
- `CANCELLED` - Cancelado

**Properties:**

```python
@property
def days_until_wedding(self):
    """Calcula dias restantes até o casamento"""
    return (self.date - date.today()).days

@property
def couple_name(self):
    """Nome formatado do casal"""
    return f"{self.groom_name} & {self.bride_name}"
```

**Validações:**

```python
def clean(self):
    if self.date and self.date < date.today():
        raise ValidationError("Data não pode ser no passado")
    if self.budget and self.budget < 0:
        raise ValidationError("Orçamento deve ser positivo")
```

### WeddingQuerySet

**Métodos disponíveis:**

```python
Wedding.objects
    .by_status(status)              # Filtra por status
    .apply_search(q)                # Busca por nome dos noivos
    .apply_sort(option)             # Ordenação (date, budget, name)
    .with_counts_and_progress()     # Anota contagens de itens/contratos
    .with_effective_status()        # Calcula status baseado na data
```

**Exemplo:**

```python
# Casamentos em andamento com contagens
weddings = (
    Wedding.objects
    .filter(planner=request.user)
    .by_status("IN_PROGRESS")
    .with_counts_and_progress()
    .apply_sort("date")
)
```

---

## Interface Web

### Forms

**WeddingForm** - Formulário com validações de negócio:

```python
class WeddingForm(ModelForm):
    def clean_date(self):
        date = self.cleaned_data['date']
        if date < date.today():
            logger.warning(f"Tentativa de data passada: {date}")
            raise ValidationError("Data não pode ser no passado")
        return date
    
    def clean_budget(self):
        budget = self.cleaned_data['budget']
        if budget < 0:
            logger.warning(f"Tentativa de orçamento negativo: {budget}")
            raise ValidationError("Orçamento deve ser positivo")
        return budget
```

### Mixins (Arquitetura Granular)

**1. PlannerOwnershipMixin** - Segurança e isolamento

```python
class PlannerOwnershipMixin:
    def get_queryset(self):
        return Wedding.objects.filter(planner=self.request.user)
```

**2. WeddingQuerysetMixin** - Lógica de query

```python
class WeddingQuerysetMixin:
    def build_queryset(self, search=None, status=None, sort=None):
        qs = self.get_queryset()
        if search:
            qs = qs.apply_search(search)
        if status:
            qs = qs.by_status(status)
        if sort:
            qs = qs.apply_sort(sort)
        return qs
```

**3. WeddingPaginationContextMixin** - Paginação

```python
class WeddingPaginationContextMixin:
    def paginate_and_annotate(self, queryset):
        paginator = Paginator(queryset, 12)  # 12 por página
        # ... lógica de paginação
        return paginated_queryset
```

**4. WeddingHtmxListResponseMixin** - Respostas HTMX

```python
class WeddingHtmxListResponseMixin:
    def render_list_response(self, context):
        if self.is_htmx_request():
            return render(self.request, "partials/_wedding_list.html", context)
        return render(self.request, "weddings/list.html", context)
```

**5. WeddingFormLayoutMixin** - Layout de formulário

```python
class WeddingFormLayoutMixin:
    def get_form_layout_config(self):
        return {
            "modal_id": "weddingModal",
            "form_id": "weddingForm",
            "title": "Novo Casamento"
        }
```

**6. WeddingListActionsMixin** - Facade (agrupa todos)

```python
class WeddingListActionsMixin(
    WeddingQuerysetMixin,
    WeddingPaginationContextMixin,
    WeddingHtmxListResponseMixin
):
    """Facade que combina funcionalidades"""
    pass
```

### Views

**WeddingListView** - Lista paginada com filtros

```python
class WeddingListView(
    LoginRequiredMixin,
    PlannerOwnershipMixin,
    WeddingListActionsMixin,
    ListView
):
    def get(self, request):
        search = request.GET.get("q")
        status = request.GET.get("status")
        sort = request.GET.get("sort", "date")
        
        queryset = self.build_queryset(search, status, sort)
        context = self.paginate_and_annotate(queryset)
        
        return self.render_list_response(context)
```

**WeddingCreateView** - Criação com modal

```python
class WeddingCreateView(
    LoginRequiredMixin,
    WeddingFormLayoutMixin,
    CreateView
):
    form_class = WeddingForm
    template_name = "weddings/partials/_create_form.html"
    
    def form_valid(self, form):
        form.instance.planner = self.request.user
        return super().form_valid(form)
```

**WeddingUpdateView** - Edição com modal

**WeddingDeleteView** - Exclusão com confirmação

**WeddingDetailView** - Painel de detalhes com abas

**UpdateWeddingStatusView** - Mudança de status via HTMX

### Rotas Web

```python
urlpatterns = [
    path("", WeddingListView.as_view(), name="list"),
    path("create/", WeddingCreateView.as_view(), name="create"),
    path("<int:pk>/", WeddingDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", WeddingUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", WeddingDeleteView.as_view(), name="delete"),
    path("<int:pk>/update-status/", UpdateWeddingStatusView.as_view(), name="update_status"),
]
```

---

## Interface API

### Serializers

**1. WeddingSerializer** - CRUD (create, update)

```python
class WeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wedding
        fields = [
            "id", "groom_name", "bride_name", "date",
            "location", "budget", "status", "created_at"
        ]
        read_only_fields = ["id", "created_at"]
    
    def validate_budget(self, value):
        if value < 0:
            raise ValidationError("Orçamento deve ser positivo")
        return value
    
    def validate_date(self, value):
        if value < date.today():
            raise ValidationError("Data não pode ser no passado")
        return value
```

**2. WeddingListSerializer** - Listagem otimizada

```python
class WeddingListSerializer(serializers.ModelSerializer):
    couple_name = serializers.SerializerMethodField()
    planner_name = serializers.CharField(source="planner.username")
    
    class Meta:
        model = Wedding
        fields = ["id", "couple_name", "date", "location", "status", "planner_name"]
    
    def get_couple_name(self, obj):
        return f"{obj.groom_name} & {obj.bride_name}"
```

**3. WeddingDetailSerializer** - Detalhes completos

```python
class WeddingDetailSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField(read_only=True)
    contracts_count = serializers.IntegerField(read_only=True)
    planner_email = serializers.EmailField(source="planner.email")
    
    class Meta:
        model = Wedding
        fields = "__all__"
```

### ViewSets

**WeddingViewSet** - CRUD completo + custom action

```python
class WeddingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsWeddingOwner]
    
    def get_queryset(self):
        return Wedding.objects.filter(planner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == "list":
            return WeddingListSerializer
        elif self.action == "retrieve":
            return WeddingDetailSerializer
        return WeddingSerializer
    
    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        """Endpoint: PATCH /api/v1/weddings/{id}/update-status/"""
        wedding = self.get_object()
        status = request.data.get("status")
        
        if status not in ["IN_PROGRESS", "COMPLETED", "CANCELLED"]:
            return Response({"error": "Status inválido"}, status=400)
        
        wedding.status = status
        wedding.save()
        
        logger.info(f"Status atualizado: {wedding} → {status}")
        return Response({"status": "success"})
```

### Permissões Customizadas

**IsWeddingOwner** - Garante ownership

```python
class IsWeddingOwner(permissions.BasePermission):
    message = "Você não tem permissão para acessar este casamento"
    
    def has_object_permission(self, request, view, obj):
        return obj.planner == request.user
```

### Endpoints API

```
GET    /api/v1/weddings/              - Lista casamentos
POST   /api/v1/weddings/              - Cria casamento
GET    /api/v1/weddings/{id}/         - Detalhes
PUT    /api/v1/weddings/{id}/         - Atualiza completo
PATCH  /api/v1/weddings/{id}/         - Atualiza parcial
DELETE /api/v1/weddings/{id}/         - Deleta
PATCH  /api/v1/weddings/{id}/update-status/ - Atualiza status
```

**Filtros via Query Params:**
- `?status=IN_PROGRESS` - Filtrar por status
- `?q=John` - Buscar por nome
- `?sort=date` - Ordenar (date, budget, name)

**Exemplo de Requisição:**

```bash
# Criar casamento
curl -X POST http://localhost:8000/api/v1/weddings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "groom_name": "João",
    "bride_name": "Maria",
    "date": "2025-12-31",
    "location": "Salão de Festas",
    "budget": 50000.00,
    "status": "IN_PROGRESS"
  }'
```

---

## Segurança

### Interface Web
- **Autenticação:** `LoginRequiredMixin` em todas as views
- **Autorização:** Queries filtradas por `planner` (isolamento de dados)
- **Validação:** Data futura, orçamento positivo
- **Logging:** Tentativas inválidas registradas

### Interface API
- **Autenticação:** `SessionAuthentication` (pode adicionar `TokenAuthentication`)
- **Permissões:** `IsAuthenticated` + `IsWeddingOwner` (object-level)
- **Validação:** Mesmas regras de negócio (serializers)
- **Logging:** Todas as operações CRUD registradas

---

## Performance

- **Queries otimizadas:** `select_related`, `prefetch_related`
- **Anotações no banco:** Contagens via `annotate()`
- **Paginação:** 10 items/página (API), 12 items/página (Web)
- **Serializers diferenciados:** List vs Detail
- **Índices futuros:** Considerar adicionar em `(planner, status)`

---

## Testes

### Estrutura (60 testes total)

**Interface Web (53 testes):**
- `test_models.py` (2) - Criação, string representation
- `test_querysets.py` (2) - Filtros por status, busca
- `test_forms.py` (10) - Validações, widgets, logging
- `test_mixins.py` (8) - Segurança, filtros, paginação
- `test_views.py` (24) - CRUD completo, HTMX, segurança
- `test_urls.py` (6) - Resolução de rotas
- `test_admin.py` (1) - Registro no admin

**Interface API (7 testes):**
- `test_serializers.py` (7) - Validações, campos, formatação

### Executar Testes

```bash
# Todos os testes
pytest apps/weddings -v

# Apenas web
pytest apps/weddings/tests/web -v

# Apenas API
pytest apps/weddings/tests/api -v

# Com cobertura
pytest apps/weddings --cov=apps.weddings --cov-report=html
```

**Status:** ✅ 60/60 passando

---

## Migração v2→v3

### Mudanças Estruturais

**1. Separação de Interfaces:**
- Movido: `forms.py`, `views.py`, `mixins.py`, `urls.py` → `web/`
- Criado: `api/serializers.py`, `api/views.py`, `api/permissions.py`, `api/urls.py`
- Mantido: `models.py`, `querysets.py`, `admin.py` (raiz)

**2. Lazy Imports (`__init__.py`):**

```python
def __getattr__(name):
    """Lazy imports para manter compatibilidade"""
    if name in ["WeddingForm"]:
        from apps.weddings.web.forms import WeddingForm
        return WeddingForm
    # ... outros imports
    raise AttributeError(f"module 'apps.weddings' has no attribute '{name}'")
```

**3. Atualização de Imports:**

Antes:
```python
from apps.weddings.forms import WeddingForm
```

Depois (ambos funcionam):
```python
from apps.weddings.web.forms import WeddingForm  # Explícito
from apps.weddings import WeddingForm            # Lazy import
```

**4. URLs Atualizadas:**

```python
# wedding_management/urls.py
urlpatterns = [
    path("", include("apps.weddings.web.urls")),  # Interface web
    path("api/v1/", include("apps.weddings.api.urls")),  # Interface API
]
```

**5. Configurações DRF:**

```python
# settings.py
INSTALLED_APPS += ["rest_framework"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
```

### Breaking Changes

**Nenhum!** A migração foi projetada para **zero breaking changes**:
- Lazy imports mantêm compatibilidade
- Código antigo continua funcionando
- Testes passam sem modificações (exceto imports)

---

## Próximos Passos

### Sugerido:
1. **TokenAuthentication** para API (JWT ou DRF Tokens)
2. **Throttling** para limitar rate de requisições
3. **Índices compostos** no banco: `(planner, status)`
4. **Cache** de lista de casamentos (Redis)
5. **Soft delete** (manter histórico)

---

**Última Atualização:** 21 de novembro de 2025  
**Versão:** 3.0 - Arquitetura Híbrida (Web + API)

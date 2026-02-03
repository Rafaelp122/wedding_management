# 🏗️ Arquitetura e Padrões de Código

## Estrutura de Apps Django

Cada app segue responsabilidades específicas baseadas nos [Requisitos Funcionais](REQUIREMENTS.md):

```
apps/
├── weddings/       # RF01, RF02 (Multitenancy + Permissões)
│   └── models.py   # Wedding, Budget
├── budget/         # RF03-RF06 (Categorias + Financeiro)
│   └── models.py   # BudgetCategory, Installment
├── items/          # RF07-RF09 (Logística + Fornecedores)
│   └── models.py   # Item, Vendor
├── contracts/      # RF10-RF13 (Gestão Jurídica)
│   └── models.py   # Contract
└── scheduler/      # RF14-RF15 (Cronograma + Notificações)
    └── models.py   # Event, Notification
```

---

## Padrões de Código

### Service Layer Pattern

**Regra:** Toda lógica de negócio deve estar em `services/`, nunca nas Views.

**Estrutura:**

```python
# apps/items/services.py
class ItemService:
    @staticmethod
    def create_with_installments(data: dict, user) -> Item:
        """
        RF04: Valida que soma das parcelas = custo real
        """
        installments = data.pop('installments', [])
        total = sum(i['amount'] for i in installments)

        if total != data['actual_cost']:
            raise ValidationError(
                f"Soma das parcelas ({total}) != custo real ({data['actual_cost']})"
            )

        # RF01: Multitenancy - item pertence ao planner
        item = Item.objects.create(**data, planner=user)

        for inst_data in installments:
            Installment.objects.create(item=item, **inst_data)

        return item
```

**Uso na View:**

```python
# apps/items/views.py
class ItemCreateView(APIView):
    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Service Layer lida com a lógica
        item = ItemService.create_with_installments(
            serializer.validated_data,
            user=request.user
        )

        return Response(ItemSerializer(item).data, status=201)
```

---

### Validações de Integridade

**RF06.1:** Prevenir cross-contamination entre casamentos

```python
# apps/items/models.py
class Item(models.Model):
    budget_category = models.ForeignKey(BudgetCategory)
    budget = models.ForeignKey(Budget)

    def clean(self):
        # Validar que categoria pertence ao mesmo casamento
        if self.budget_category.budget.wedding_id != self.budget.wedding_id:
            raise ValidationError(
                "Categoria não pertence ao mesmo casamento do Budget"
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Força validação
        super().save(*args, **kwargs)
```

---

### Soft Delete (RNF04)

**Aplicado em:** `Wedding`, `BudgetCategory`, `Item`, `Contract`, `Vendor`

```python
# apps/core/models.py
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7)  # RNF05
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Inclui deletados

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()  # Deleção permanente

    class Meta:
        abstract = True
```

**Exceções (imutáveis):** `AuditLog`, `Installment` (quando status=PAID)

---

### Multitenancy (RF01)

**Padrão:** Filtrar automaticamente por `planner` (usuário logado)

```python
# apps/weddings/views.py
class WeddingListView(generics.ListAPIView):
    serializer_class = WeddingSerializer

    def get_queryset(self):
        # RF01: Isolar dados por planner
        return Wedding.objects.filter(planner=self.request.user)
```

**Middleware de segurança:**

```python
# apps/core/middleware.py
class MultitenancyMiddleware:
    def __call__(self, request):
        # Garantir que views sempre filtram por user
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.planner_id = request.user.id
        return self.get_response(request)
```

---

## Tarefas Assíncronas (Celery)

### RF05: Atualização de Parcelas Vencidas

```python
# apps/budget/tasks.py
from celery import shared_task
from django.utils import timezone

@shared_task(bind=True, max_retries=3)
def update_overdue_installments(self):
    """
    Roda diariamente às 00:00 UTC
    Atualiza parcelas vencidas para status OVERDUE
    """
    try:
        overdue_count = Installment.objects.filter(
            due_date__lt=timezone.now().date(),
            status='PENDING',
            is_deleted=False
        ).update(status='OVERDUE')

        logger.info(f"[Celery] {overdue_count} parcelas marcadas como OVERDUE")
        return overdue_count

    except Exception as exc:
        # Retry com backoff exponencial: 1min, 5min, 15min
        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries)
        )
```

**Configuração:**

```python
# config/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-overdue-installments': {
        'task': 'apps.budget.tasks.update_overdue_installments',
        'schedule': crontab(hour=0, minute=0),  # 00:00 UTC
    },
}
```

---

## Gerenciamento de Dependências

### pyproject.toml + uv.lock

**Por que UV?** 10-100x mais rápido que pip, escrito em Rust.

```bash
# Adicionar pacote
make back-install pkg=requests

# Atualizar lockfile após editar pyproject.toml
make reqs

# Rebuild container
make build
```

**Estrutura:**

```toml
[project]
dependencies = [
    "django>=5.2.9,<5.3",
    "djangorestframework>=3.16.1,<3.17",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.4",
    "ruff>=0.7.4",
]
```

---

## Multi-Stage Docker Builds

**4 Stages:** base → builder → development → production

### Otimizações Implementadas

1. **Cache mount do BuildKit:**
   - Apt-get não redownload pacotes
   - Economiza ~40s

2. **UV com cache:**
   - Wheels reutilizados
   - Economiza ~8s

3. **Separação de stages:**
   - Development: código via volume (hot reload)
   - Production: código copiado (imagem standalone)

**Performance:**

- Com cache: ~10-15s
- Sem cache: ~77s

---

## Testes

### Estrutura

```python
# apps/items/tests/test_services.py
import pytest
from apps.items.services import ItemService

@pytest.mark.django_db
class TestItemService:
    def test_create_with_valid_installments(self, user, budget):
        data = {
            'actual_cost': 1000,
            'installments': [
                {'amount': 500, 'due_date': '2026-03-01'},
                {'amount': 500, 'due_date': '2026-04-01'},
            ]
        }

        item = ItemService.create_with_installments(data, user)
        assert item.actual_cost == 1000
        assert item.installments.count() == 2

    def test_reject_invalid_installments(self, user):
        """RF04: Soma das parcelas deve ser igual ao custo"""
        data = {
            'actual_cost': 1000,
            'installments': [{'amount': 600}, {'amount': 600}]  # Soma = 1200
        }

        with pytest.raises(ValidationError):
            ItemService.create_with_installments(data, user)
```

**Comandos:**

```bash
make test            # Todos os testes
make test-cov        # Com cobertura
pytest apps/items/   # App específico
```

---

## Decisões Técnicas

### UUID7 ao invés de UUID4

**Motivo:** Mantém ordenação temporal (útil em queries e merges de bases)

```python
from uuid_extensions import uuid7

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7)
```

### Email como USERNAME_FIELD

```python
# apps/users/models.py
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'  # Login via email
```

### Service Layer ao invés de Fat Models

**Motivo:** Facilita testes unitários e reutilização de lógica entre views/tasks.

---

## Referências

- [Requisitos do Sistema](REQUIREMENTS.md)
- [Guia de Configuração](ENVIRONMENT.md)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django Best Practices](https://docs.djangoproject.com/en/5.2/misc/design-philosophies/)

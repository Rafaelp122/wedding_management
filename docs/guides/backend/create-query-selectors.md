# Como Criar Custom QuerySets e Query Selectors

> **Módulo:** [query-selectors-spec](../../reference/architecture-standards/query-selectors-spec.md) | [query-selectors-pattern](../../architecture/concepts/query-selectors-pattern.md)
> **Relacionados:** [run-pytest-suite](run-pytest-suite.md) | [use-core-services](use-core-services.md)

---

## Objetivo

Este guia prático ensina passo a passo como implementar **Custom QuerySets** e **Query Selectors** para um novo modelo ou domínio no backend Django Ninja.

---

## Passo a Passo

### Passo 1: Criar o Custom QuerySet em `managers.py`

Defina a classe do QuerySet herdando de `TenantQuerySet` e adicione métodos de anotação e filtros reutilizáveis:

```python
# apps/meu_dominio/managers.py
from apps.tenants.managers import TenantQuerySet

class ItemQuerySet(TenantQuerySet["Item"]):
    """QuerySet customizado para Item com métodos encadeáveis."""

    def active(self) -> "ItemQuerySet":
        """Filtra apenas itens ativos."""
        return self.filter(is_active=True)

    def by_status(self, status: str) -> "ItemQuerySet":
        """Filtra itens pelo status."""
        return self.filter(status=status)
```

---

### Passo 2: Conectar o Manager no Modelo

No arquivo de modelo correspondente, configure o manager padrão utilizando `.as_manager()`:

```python
# apps/meu_dominio/models/item.py
from apps.meu_dominio.managers import ItemQuerySet
from apps.tenants.models import TenantModel

class Item(TenantModel):
    ...
    objects = ItemQuerySet.as_manager()
```

---

### Passo 3: Criar os Selectors em `selectors/`

Crie o arquivo de seletores com funções de listagem (retornando o QuerySet) e busca pontual:

```python
# apps/meu_dominio/selectors/item_selectors.py
from typing import cast
from uuid import UUID
from django.core.exceptions import ValidationError
from apps.core.exceptions import ObjectNotFoundError
from apps.meu_dominio.managers import ItemQuerySet
from apps.meu_dominio.models import Item
from apps.tenants.models import Company


def item_list_selector(
    *, company: Company, status: str | None = None
) -> ItemQuerySet:
    """Retorna o QuerySet encadeável de itens do tenant."""
    qs = cast(ItemQuerySet, Item.objects.for_tenant(company))
    if status:
        qs = qs.by_status(status)
    return qs


def item_get_selector(*, company: Company, uuid: UUID | str) -> Item:
    """Busca um item específico do tenant ou levanta 404."""
    try:
        return item_list_selector(company=company).get(uuid=uuid)
    except (Item.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(
            detail="Item não encontrado ou acesso negado."
        ) from e
```

Exporte as funções no `apps/meu_dominio/selectors/__init__.py`:

```python
# apps/meu_dominio/selectors/__init__.py
from .item_selectors import item_get_selector, item_list_selector

__all__ = ["item_get_selector", "item_list_selector"]
```

---

### Passo 4: Consumir os Selectors no Router (`api.py`) e Padrão Read-After-Write

No router do Django Ninja, utilize os selectors não apenas para responder rotas `GET`, mas também no padrão canônico **Read-After-Write**:
1. Para rotas `GET`: Chame o selector diretamente.
2. Para rotas `POST` (Criação): Delegue ao serviço e reidrate o recurso chamando `*_get_selector` com o `uuid` do objeto persistido.
3. Para rotas `PATCH`/`PUT` (Atualização): Carregue a instância com o selector, execute o serviço e retorne a instância reidratada novamente via `*_get_selector`.

```python
# apps/meu_dominio/api/items.py
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.meu_dominio.models import Item
from apps.meu_dominio.schemas import ItemIn, ItemOut, ItemPatchIn
from apps.meu_dominio.selectors import item_get_selector, item_list_selector
from apps.meu_dominio.services import ItemService
from apps.users.types import AuthRequest

items_router = Router(tags=["MeuDominio"])


@items_router.get("/", response=list[ItemOut], operation_id="meudominio_items_list")
@paginate
def list_items(request: AuthRequest):
    return item_list_selector(company=request.user.company)


@items_router.get(
    "/{uuid:uuid}/",
    response={200: ItemOut, **READ_ERROR_RESPONSES},
    operation_id="meudominio_items_read",
)
def get_item(request: AuthRequest, uuid: UUID4) -> Item:
    return item_get_selector(company=request.user.company, uuid=uuid)


@items_router.post(
    "/",
    response={201: ItemOut, **MUTATION_ERROR_RESPONSES},
    operation_id="meudominio_items_create",
)
def create_item(request: AuthRequest, payload: ItemIn) -> tuple[int, Item]:
    company = request.user.company
    item = ItemService.create(company=company, payload=payload)
    return 201, item_get_selector(company=company, uuid=item.uuid)


@items_router.patch(
    "/{uuid:uuid}/",
    response={200: ItemOut, **MUTATION_ERROR_RESPONSES},
    operation_id="meudominio_items_update",
)
def update_item(request: AuthRequest, uuid: UUID4, payload: ItemPatchIn) -> Item:
    company = request.user.company
    instance = item_get_selector(company=company, uuid=uuid)
    ItemService.update(company=company, instance=instance, payload=payload)
    return item_get_selector(company=company, uuid=uuid)
```

> [!TIP]
> **Por que Read-After-Write?** O retorno direto de um método de serviço contém instâncias com estado bruto de memória. Re-executar o selector garante que campos calculados no SQL, anotações de agregados e relacionamentos `select_related`/`prefetch_related` sejam hidratos com integridade absoluta antes da resposta HTTP.


---

### Passo 5: Criar os Testes em `tests/test_selectors.py`

Valide o isolamento multi-tenant e os métodos encadeáveis:

```python
# apps/meu_dominio/tests/test_selectors.py
import pytest
from apps.meu_dominio.selectors import item_get_selector, item_list_selector

@pytest.mark.django_db
class TestItemSelectors:
    def test_list_selector_tenant_isolation(self, user, other_company_user):
        # Cria registros usando factories e valida o isolamento do tenant
        ...
```

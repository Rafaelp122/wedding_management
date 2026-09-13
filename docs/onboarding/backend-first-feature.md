# Tutorial: Criando sua Primeira Feature no Backend (Django Ninja)

> **Tipo:** Tutorial (Onboarding)
> **Relacionados:** [ADR-030: Rich Domain Model](../architecture/adr/030-rich-domain-model-service-layer.md) · [ADR-011: BaseModel save() com full_clean()](../architecture/adr/011-basemodel-save-full-clean.md) · [Padrão Service Layer](../architecture/concepts/service-layer-pattern.md) · [Padrão Query Selectors](../architecture/concepts/query-selectors-pattern.md) · [Como Criar Query Selectors](../guides/backend/create-query-selectors.md) · [Estruturar e Modularizar Modelos Ricos](../guides/backend/structure-and-modularize-rich-models.md) · [Executar Suíte Pytest](../guides/backend/run-pytest-suite.md)

---

## 1. Visão Geral & O Fluxo Arquitetural

No **Wedding Management System**, o desenvolvimento de funcionalidades no backend segue rigorosamente a **ADR-030** e o padrão **CQRS-lite**:

1. **Nível 1 (Borda / Schemas):** Schemas Pydantic v2 sanitizam a entrada (`str_strip_whitespace=True`) e definem contratos DTO puros.
2. **Nível 2 (Domínio / Rich Models):** Entidades herdam de `TenantModel` e mixins, encapsulam suas regras em métodos semânticos e validam invariantes locais em `clean()`.
3. **Nível 3 (Orquestração / Service Layer):** Mutam o banco sob `@transaction.atomic`, resolvem dependências com `resolve_tenant_resource` e executam `instance.save(update_fields=[...])`.
4. **Projeção de Leitura (Query Selectors):** Consultas `GET` e reidratação pós-mutação utilizam funções puras em `selectors/` baseadas em `objects.for_tenant(company)`.
5. **Transporte HTTP (Routers):** Endpoints Django Ninja injetam `request.user.company`, delegam para a Service Layer e retornam via **Read-After-Write**.
6. **Frontend Sync:** Um único comando (`just sync-api`) gera automaticamente a tipagem TypeScript, esquemas Zod e hooks TanStack Query.

Neste tutorial, você construirá uma feature completa de anotações de casamento (**`Note`**), do modelo ao contrato gerado.

---

## 2. Passo a Passo de Implementação

### Passo 1: Definir o Modelo Rico (`models/note.py`)

Crie o modelo herdando de `TenantModel` (para isolamento multi-tenant automático via `company`) e `WeddingOwnedMixin` (para vinculação com o casamento):

```python
# apps/weddings/models/note.py
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.tenants.models import TenantModel
from apps.weddings.managers import NoteQuerySet


class Note(TenantModel, WeddingOwnedMixin):
    """Anotação associada a um casamento do tenant."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)

    objects = NoteQuerySet.as_manager()

    class Meta:
        verbose_name = "Anotação"
        verbose_name_plural = "Anotações"
        ordering = ["-is_pinned", "-created_at"]

    def clean(self) -> None:
        """Invariantes de domínio locais."""
        super().clean()
        if len(self.title.strip()) < 3:
            raise ValidationError({"title": "O título da anotação deve ter no mínimo 3 caracteres."})

    def toggle_pin(self) -> None:
        """Comportamento de domínio semântico."""
        self.is_pinned = not self.is_pinned
```

> [!NOTE]
> Conforme a **ADR-011**, `TenantModel` herda de `BaseModel`, que dispara `self.full_clean()` automaticamente antes de qualquer `save()`. Não é necessário chamar `full_clean()` manualmente nos serviços.

---

### Passo 2: Definir os Schemas Pydantic v2 (`schemas/notes.py`)

Defina os DTOs de entrada (`NoteIn`, `NotePatchIn`) e projeção de saída (`NoteOut`):

```python
# apps/weddings/schemas/notes.py
import datetime
from ninja import Field, Schema
from pydantic import UUID4


class NoteIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    wedding_uuid: UUID4
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=1)
    is_pinned: bool = False


class NotePatchIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    title: str | None = Field(None, min_length=3, max_length=255)
    content: str | None = Field(None, min_length=1)
    is_pinned: bool | None = None


class NoteOut(Schema):
    uuid: UUID4
    wedding_uuid: UUID4 = Field(..., alias="wedding.uuid")
    title: str
    content: str
    is_pinned: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
```

---

### Passo 3: Implementar a Service Layer (`services/note_service.py`)

A Service Layer orquestra o caso de uso, delimita a transação atômica e garante o isolamento multi-tenant:

```python
# apps/weddings/services/note_service.py
import structlog
from django.db import transaction

from apps.core.shortcuts import resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.tenants.models import Company
from apps.weddings.models import Note, Wedding
from apps.weddings.schemas.notes import NoteIn, NotePatchIn

logger = structlog.get_logger(__name__)


class NoteService:
    """Orquestrador de mutações e casos de uso de Anotações."""

    @classmethod
    @transaction.atomic
    def create(cls, *, company: Company, payload: NoteIn) -> Note:
        """Cria uma nova anotação vinculada ao casamento do tenant.

        Args:
            company: Tenant proprietário.
            payload: Dados sanitizados de entrada.

        Returns:
            Instância persistida da anotação.
        """
        # Resolve e valida que o casamento pertence à mesma empresa (prevenção de IDOR)
        wedding = resolve_tenant_resource(
            Wedding,
            company=company,
            resource_input=payload.wedding_uuid,
            detail="Casamento não encontrado ou acesso negado.",
        )

        note = Note(
            company=company,
            wedding=wedding,
            title=payload.title,
            content=payload.content,
            is_pinned=payload.is_pinned,
        )
        note.save()

        logger.info(
            "note_created",
            company_id=str(company.id),
            wedding_id=str(wedding.id),
            note_uuid=str(note.uuid),
        )
        return note

    @classmethod
    @transaction.atomic
    def update(
        cls,
        *,
        company: Company,
        instance: Note,
        payload: NotePatchIn,
    ) -> Note:
        """Atualiza campos pontuais com mutação cirúrgica.

        Args:
            company: Tenant proprietário.
            instance: Instância pré-carregada pelo selector.
            payload: Campos a atualizar.

        Returns:
            Instância atualizada.
        """
        validate_tenant_ownership(company, instance)

        update_fields: list[str] = ["updated_at"]
        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(instance, field, value)
            update_fields.append(field)

        instance.save(update_fields=update_fields)
        return instance
```

---

### Passo 4: Implementar Query Selectors (`selectors/note_selectors.py`)

Toda leitura deve residir em `selectors/`, mantendo queries otimizadas e encapsuladas:

```python
# apps/weddings/selectors/note_selectors.py
from typing import cast
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from apps.core.exceptions import ObjectNotFoundError
from apps.tenants.models import Company
from apps.weddings.models import Note


def note_list_selector(
    *,
    company: Company,
    wedding_uuid: UUID | str | None = None,
) -> QuerySet[Note]:
    """Retorna QuerySet lazy de anotações do tenant."""
    qs = Note.objects.for_tenant(company).select_related("wedding")
    if wedding_uuid:
        qs = qs.filter(wedding__uuid=wedding_uuid)
    return qs


def note_get_selector(*, company: Company, uuid: UUID | str) -> Note:
    """Busca anotação específica do tenant com reidratação segura."""
    try:
        return note_list_selector(company=company).get(uuid=uuid)
    except (Note.DoesNotExist, ValueError, ValidationError) as exc:
        raise ObjectNotFoundError(
            detail="Anotação não encontrada ou acesso negado."
        ) from exc
```

---

### Passo 5: Expor os Endpoints com Read-After-Write (`api.py`)

No router do Django Ninja, implemente o padrão canônico **Read-After-Write**: mutações delegam ao service e reidratam via selector antes de responder.

```python
# apps/weddings/api.py (ou router dedicado)
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.users.types import AuthRequest
from apps.weddings.models import Note
from apps.weddings.schemas.notes import NoteIn, NoteOut, NotePatchIn
from apps.weddings.selectors.note_selectors import note_get_selector, note_list_selector
from apps.weddings.services.note_service import NoteService

notes_router = Router(tags=["Notes"])


@notes_router.get(
    "/",
    response=list[NoteOut],
    operation_id="notes_list",
)
@paginate
def list_notes(request: AuthRequest, wedding_uuid: UUID4 | None = None):
    """Lista anotações com paginação e filtro por casamento."""
    return note_list_selector(company=request.user.company, wedding_uuid=wedding_uuid)


@notes_router.get(
    "/{uuid:uuid}/",
    response={200: NoteOut, **READ_ERROR_RESPONSES},
    operation_id="notes_read",
)
def get_note(request: AuthRequest, uuid: UUID4) -> Note:
    """Lê uma anotação específica pelo identificador público."""
    return note_get_selector(company=request.user.company, uuid=uuid)


@notes_router.post(
    "/",
    response={201: NoteOut, **MUTATION_ERROR_RESPONSES},
    operation_id="notes_create",
)
def create_note(request: AuthRequest, payload: NoteIn) -> tuple[int, Note]:
    """Cria anotação e reidrata via Read-After-Write."""
    company = request.user.company
    note = NoteService.create(company=company, payload=payload)
    return 201, note_get_selector(company=company, uuid=note.uuid)


@notes_router.patch(
    "/{uuid:uuid}/",
    response={200: NoteOut, **MUTATION_ERROR_RESPONSES},
    operation_id="notes_update",
)
def update_note(
    request: AuthRequest,
    uuid: UUID4,
    payload: NotePatchIn,
) -> Note:
    """Atualiza anotação cirurgicamente e reidrata via Read-After-Write."""
    company = request.user.company
    instance = note_get_selector(company=company, uuid=uuid)
    NoteService.update(company=company, instance=instance, payload=payload)
    return note_get_selector(company=company, uuid=uuid)
```

> [!TIP]
> **Por que Read-After-Write?** O retorno do `save()` do ORM contém instâncias com estado bruto de memória. Re-executar o `*_get_selector` garante que todos os campos virtuais, `select_related`, `prefetch_related` e anotações agregadas do SQL estejam preenchidos antes da serialização pelo Pydantic.

---

### Passo 6: Escrever Testes Unitários de Sucesso e Isolamento (`tests/`)

Use **sempre** factories de teste (`apps/*/tests/factories.py`) — o uso de `.objects.create()` é estritamente proibido pelas diretrizes do projeto:

```python
# apps/weddings/tests/notes/test_services.py
import pytest
from apps.core.exceptions import ObjectNotFoundError
from apps.weddings.schemas.notes import NoteIn
from apps.weddings.services.note_service import NoteService
from apps.weddings.tests.factories import CompanyFactory, WeddingFactory


@pytest.mark.django_db
class TestNoteService:
    def test_create_note_success(self):
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)
        payload = NoteIn(
            wedding_uuid=wedding.uuid,
            title="Lista de Fornecedores",
            content="Fotógrafo, Buffet e DJ contratados.",
        )

        note = NoteService.create(company=company, payload=payload)

        assert note.id is not None
        assert note.title == "Lista de Fornecedores"
        assert note.company == company
        assert note.wedding == wedding

    def test_create_note_cross_tenant_isolation_fails(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        wedding_b = WeddingFactory(company=company_b)

        payload = NoteIn(
            wedding_uuid=wedding_b.uuid,
            title="Anotação Inválida",
            content="Tentativa de associar ao casamento de outra empresa.",
        )

        with pytest.raises(ObjectNotFoundError):
            NoteService.create(company=company_a, payload=payload)
```

---

### Passo 7: Sincronizar com o Frontend (`just sync-api`)

Após expor as rotas no router, execute a sincronização completa do contrato para o ecossistema React:

```bash
just sync-api
```

Esse comando executa internamente:
1. `just openapi`: Exporta o esquema OpenAPI canônico atualizado (`backend/openapi.json`).
2. `just orval`: Gera automaticamente os hooks do TanStack Query (`useNotesCreate`, `useNotesList`, etc.), os tipos TypeScript (`NoteIn`, `NoteOut`) e os esquemas Zod em `frontend/src/api/generated/`.

No seu componente React 19, consuma imediatamente o hook tipado:

```tsx
import { useNotesList, useNotesCreate } from "@/api/generated/weddings/weddings";

export function WeddingNotes({ weddingUuid }: { weddingUuid: string }) {
  const { data: notes, isLoading } = useNotesList({ wedding_uuid: weddingUuid });
  const createMutation = useNotesCreate();

  if (isLoading) return <div>Carregando anotações...</div>;

  return (
    <div>
      {notes?.map((note) => (
        <div key={note.uuid}>
          <h4>{note.title}</h4>
          <p>{note.content}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 3. Checklist de Conclusão da Feature

- [ ] **Modelo:** Herdando de `TenantModel` com métodos semânticos e `clean()` sem dirty tracking.
- [ ] **Schemas:** Pydantic v2 com `model_config = {"extra": "ignore", "str_strip_whitespace": True}`.
- [ ] **Service:** `@transaction.atomic`, `resolve_tenant_resource` e `save(update_fields=[...])`.
- [ ] **Selector:** Filtro via `for_tenant(company)` e retorno de lazy QuerySet ou 404 tipado.
- [ ] **Router:** Endpoints com `operation_id` explícito e retorno em **Read-After-Write**.
- [ ] **Testes:** 100% de cobertura com factories (zero `.objects.create()`).
- [ ] **Contrato:** `just sync-api` executado e hooks gerados no frontend.

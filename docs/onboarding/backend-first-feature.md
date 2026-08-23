# Tutorial: Criando sua Primeira Feature no Backend (Django Ninja)

> **Objetivo:** Adicionar um novo endpoint e serviço no backend seguindo o padrão Service Layer, Multi-tenancy e Pydantic.

---

## Passo 1: Definir o Modelo em `models.py`

Crie ou edite o modelo em `backend/apps/<modulo>/models/`:

```python
from django.db import models
from apps.tenants.models import TenantModel
from apps.core.mixins import WeddingOwnedMixin

class Note(TenantModel, WeddingOwnedMixin):
    title = models.CharField(max_length=255)
    content = models.TextField()
```

---

## Passo 2: Implementar a Lógica na Service Layer (`services.py`)

```python
from apps.tenants.models import Company
from .models import Note

class NoteService:
    @staticmethod
    def create_note(company: Company, wedding_id: int, title: str, content: str) -> Note:
        note = Note(
            company=company,
            wedding_id=wedding_id,
            title=title,
            content=content,
        )
        note.full_clean()  # ADR-011: Validação pré-gravação
        note.save()
        return note
```

---

## Passo 3: Expor o Endpoint no Router (`api.py`)

```python
from ninja import Router
from apps.tenants.models import Company
from .services import NoteService
from .schemas import NoteSchema, NoteCreateSchema

router = Router(tags=["Notes"])

@router.post("/", response=NoteSchema, operation_id="notes_create")
def create_note(request, payload: NoteCreateSchema):
    company = request.user.company
    return NoteService.create_note(company=company, **payload.dict())
```

---

## Passo 4: Criar Testes de Unidade com Pytest

Crie um teste em `backend/apps/<modulo>/tests/test_services.py`:

```python
def test_create_note_success(db):
    company = CompanyFactory()
    wedding = WeddingFactory(company=company)
    note = NoteService.create_note(company=company, wedding_id=wedding.id, title="Teste", content="Conteúdo")
    assert note.id is not None
    assert note.company == company
```

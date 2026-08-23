# Especificação Técnica: Query Selectors & Custom QuerySets

> **Módulo:** [query-selectors-spec](query-selectors-spec.md) | [documentation-standards](documentation-standards.md)
> **Explicação:** [query-selectors-pattern](../../architecture/concepts/query-selectors-pattern.md) | [service-layer-pattern](../../architecture/concepts/service-layer-pattern.md)

---

## 1. Regras Estruturais e Nomenclatura

Todos os seletores de consulta no backend devem seguir o padrão estrito de nomenclatura e assinatura:

```text
apps/<domain>/
├── managers.py          # Subclasses de TenantQuerySet e TenantManager
├── selectors/           # Funções puras de consulta
│   ├── __init__.py      # Exportação pública de todos os seletores
│   ├── <entity>_selectors.py
└── services/            # Mutações e regras de escrita (Commands)
```

### Padrão de Nomenclatura de Funções
- **Listagens / QuerySets:** `<entity>_list_selector(*, company: Company, ...) -> <Entity>QuerySet`
- **Buscas Pontuais (Single Entity):** `<entity>_get_selector(*, company: Company, uuid: UUID | str) -> <Entity>`
- **Agregações & Resumos:** `<domain>_<metric>_selector(*, company: Company, ...) -> <Type>`

---

## 2. Assinaturas e Tipagem Estrita

1. **Parâmetros Nomeados (Keyword-Only):**
   Toda função seletora deve usar argumentos nomeados obrigatórios (`*`), com a `company: Company` como primeiro parâmetro:
   ```python
   def budget_list_selector(*, company: Company, wedding_id: UUID | str | None = None) -> BudgetQuerySet:
       ...
   ```
2. **Retorno de QuerySets Especializados:**
   As funções `*_list_selector` devem retornar explicitamente o tipo do Custom QuerySet correspondente (ex: `BudgetQuerySet`, `WeddingQuerySet`), garantindo tipagem forte no `mypy` e encadeamento em camadas superiores.
3. **Resolução de Não Encontrado (404):**
   As funções `*_get_selector` devem capturar `DoesNotExist`, `ValueError` e `ValidationError` ao resolver instâncias e lançar `ObjectNotFoundError` padronizado:
   ```python
   def budget_get_selector(*, company: Company, uuid: UUID | str) -> Budget:
       try:
           return budget_list_selector(company=company).get(uuid=uuid)
       except (Budget.DoesNotExist, ValueError, ValidationError) as e:
           raise ObjectNotFoundError(detail="Orçamento não encontrado ou acesso negado.") from e
   ```

---

## 3. Diretrizes para Custom QuerySets (`managers.py`)

1. **Herança Obrigatória:** Todo QuerySet de tenant deve herdar de `TenantQuerySet` (ou `TenantQuerySet[ModelT]`).
2. **Retorno de `self` Tipado:** Métodos de filtragem e anotação devem retornar a própria classe do QuerySet para encadeamento fluente:
   ```python
   class TaskQuerySet(TenantQuerySet["Task"]):
       def pending(self) -> "TaskQuerySet":
           return self.filter(is_completed=False)

       def urgent(self, today: date) -> "TaskQuerySet":
           return self.pending().filter(due_date__lte=today)
   ```
3. **Vinculação no Model:** Associar o manager especializado no modelo Django:
   ```python
   class Task(TenantModel, WeddingOwnedMixin):
       ...
       objects = TaskQuerySet.as_manager()
   ```

---

## 4. Guard-Rails e Proibições

- 🚫 **Proibido Mutações em Selectors:** É estritamente proibido chamar `.save()`, `.delete()`, `.create()`, `.update()` ou alterar estado de banco dentro de qualquer função em `selectors/`.
- 🚫 **Proibido Queries Brutas em Controllers:** Rotas no `api.py` não devem instanciar queries ORM diretamente. Rotas `GET` devem chamar `selectors`, e rotas de mutação devem delegar para `services`.
- 🚫 **Proibido Métodos de Leitura em Services:** Classes de serviço em `services/` não devem conter métodos estáticos de busca como `list()` ou `get()`.

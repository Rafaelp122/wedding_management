# ADR-011: `full_clean()` Centralizado no `BaseModel.save()`

**Status:** Aceito
**Data:** Março 2026
**Decisor:** Rafael
**Contexto:** Garantir que validações de negócio (`clean()`) nunca sejam bypassadas

---

## Contexto e Problema

O Django **não** chama `full_clean()` automaticamente no `save()`. Isso significa que validações definidas em `clean()` (regras de negócio, cross-field, cross-FK) só são executadas se alguém chamar `full_clean()` explicitamente antes de `save()`.

Antes desta decisão, o projeto tinha **duas abordagens coexistindo:**

| Models | Comportamento |
|---|---|
| BudgetCategory, Expense, Installment, Contract, Item | Sobrescreviam `save()` com `full_clean()` |
| Wedding, Event, Budget, Supplier | **Não** sobrescreviam — dependiam do Service chamar `full_clean()` |

Essa inconsistência era perigosa:
1. Um desenvolvedor olhava `BudgetCategory` e assumia que **todos** os models se auto-protegiam.
2. Os Services chamavam `full_clean()` → `save()`, e os models que sobrescreviam `save()` rodavam `full_clean()` **duas vezes** (double validation, queries duplicadas).
3. Qualquer caminho fora do Service (Django Admin, shell, management commands, scripts de migração) **não** tinha proteção para metade dos models.

---

## Decisão

Centralizar `full_clean()` no `BaseModel.save()` com escape hatch:

```python
class BaseModel(models.Model):
    def save(self, *args, skip_clean=False, **kwargs):
        if not skip_clean:
            self.full_clean()
        super().save(*args, **kwargs)
```

**Consequências:**

1. **Remover `save()` de todos os models individuais** — o `BaseModel` cuida.
2. **Remover `full_clean()` de todos os Services** — o `save()` já executa.
3. O parâmetro `skip_clean=False` permite pular a validação em cenários controlados.

---

## Quando usar `skip_clean=True`

| Cenário | Justificativa |
|---|---|
| **Bulk operations** (`bulk_create`, migrations de dados) | Performance — validação já foi feita em lote antes |
| **Fixtures de teste** | Speed — factories já constroem objetos válidos |
| **Management commands de seed** | Dados controlados, validação desnecessária |
| **Signals que atualizam campos calculados** | Evitar recursão infinita (signal → save → clean → signal) |

**NUNCA** usar `skip_clean=True` em:
- Services (camada de negócio)
- Views/ViewSets
- Qualquer caminho que aceite input do usuário

---

## Alternativas Consideradas

### 1. Manter `full_clean()` nos Services + `save()` nos Models

**Rejeitado.** Causa double validation (performance) e a inconsistência entre models que fazem e não fazem continua.

### 2. Manter `full_clean()` apenas nos Services

**Rejeitado.** O Admin, shell e management commands ficam desprotegidos. Defesa em profundidade é mais segura.

### 3. Usar `django-fullclean` ou `django-model-validation`

**Rejeitado.** Dependência externa para algo trivial (3 linhas de código). O `skip_clean` já resolve o escape hatch.

---

## Impacto

- **Services:** Removidas ~18 chamadas explícitas de `full_clean()`. Cada service agora faz apenas `instance.save()`.
- **Models:** Removidos 5 overrides de `save()` em models individuais.
- **Performance:** Eliminada a double validation no caminho da API.
- **Segurança:** Todos os 10 models agora validam automaticamente em qualquer caminho de persistência.
- **Testes:** 31/31 passando após as mudanças.

---

## Referências

- [Django docs: Validating objects](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects)
- ADR-006: Service Layer Pattern
- FULL_AUDIT.md: MODEL-001 e MODEL-002

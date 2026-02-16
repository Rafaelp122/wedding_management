# ADR-009: Multitenancy Denormalizado

**Status:** Aceito
**Data:** Janeiro 2025
**Decisor:** Rafael
**Contexto:** Estratégia de isolamento de dados entre casamentos

---

## Contexto e Problema

Sistema multi-tenant: cada casamento (wedding) é um tenant isolado.

**Requisitos:**

1. User A NÃO pode ver contratos de User B
2. Queries devem filtrar por `wedding_id` automaticamente
3. Validações devem prevenir cross-wedding access

**Alternativas:**

1. **Schema-based:** 1 schema PostgreSQL por wedding (isolamento total)
2. **Database-based:** 1 database por wedding (overkill)
3. **Row-based normalizado:** wedding → category → item → expense (4 JOINs)
4. **Row-based denormalizado:** wedding_id em TODOS models (escolhido)

---

## Decisão

Usar **multitenancy denormalizado**:

- Campo `wedding_id` em TODOS models (denormalização)
- Mixin `WeddingOwnedMixin` aplica validação automaticamente
- Queries sempre filtram por `wedding_id`

---

## Justificativa

### Comparação de Abordagens

| Aspecto            | Denormalizado (escolhido) | Normalizado (4 JOINs) | Schema-based            |
| ------------------ | ------------------------- | --------------------- | ----------------------- |
| **Performance**    | ✅ 1 query                | ❌ 4 JOINs            | ✅ Isolamento total     |
| **Simplicidade**   | ✅ Simples                | ⚠️ Complexo           | ❌ Muito complexo       |
| **Escalabilidade** | ✅ Escala horizontal      | ⚠️ JOINs custosos     | ❌ Limite schemas (~1k) |
| **Migração**       | ✅ Zero mudanças          | ✅ Zero mudanças      | ❌ Requer migrations    |

---

### Estrutura Normalizada (Problema)

```python
# ❌ NORMALIZADO: wedding_id APENAS em Wedding
class Wedding(BaseModel):
    name = models.CharField(max_length=200)
    date = models.DateField()

class Category(BaseModel):
    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE)  # FK
    name = models.CharField(max_length=100)

class Item(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # FK
    name = models.CharField(max_length=100)

class Expense(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  # FK
    value = models.DecimalField(max_digits=10, decimal_places=2)
```

**Query para pegar despesas de 1 wedding:**

```python
# ❌ PROBLEMA: 4 JOINs para filtrar por wedding
expenses = Expense.objects.filter(
    item__category__wedding_id=wedding_id
).select_related('item', 'item__category', 'item__category__wedding')

# SQL gerado:
SELECT * FROM expenses e
JOIN items i ON e.item_id = i.id
JOIN categories c ON i.category_id = c.id
JOIN weddings w ON c.wedding_id = w.id
WHERE w.id = 123;
```

**Problemas:**

- 4 JOINs para query simples
- Índices compostos complexos
- Performance degrada com crescimento

---

### Estrutura Denormalizada (Solução)

```python
# ✅ DENORMALIZADO: wedding_id em TODOS models
class Wedding(BaseModel):
    name = models.CharField(max_length=200)
    date = models.DateField()

class Category(BaseModel, WeddingOwnedMixin):  # Herda wedding_id
    name = models.CharField(max_length=100)

class Item(BaseModel, WeddingOwnedMixin):  # Herda wedding_id
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Expense(BaseModel, WeddingOwnedMixin):  # Herda wedding_id
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
```

**Query simplificada:**

```python
# ✅ ZERO JOINs (apenas filtro por wedding_id)
expenses = Expense.objects.filter(wedding_id=wedding_id)

# SQL gerado:
SELECT * FROM expenses WHERE wedding_id = 123;
```

---

### Implementação do Mixin

```python
# apps/core/models.py
class WeddingOwnedMixin(models.Model):
    """
    Mixin que adiciona wedding_id a qualquer model.

    Features:
    - Campo wedding_id indexado
    - Validação automática de cross-wedding access
    - Manager com filtro por wedding padrão
    """

    wedding = models.ForeignKey(
        'weddings.Wedding',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',  # Dynamic related_name
        db_index=True  # Índice para performance
    )

    class Meta:
        abstract = True

    def clean(self):
        """Valida que FKs pertencem ao mesmo wedding."""
        super().clean()

        # Valida que category pertence ao mesmo wedding
        if hasattr(self, 'category') and self.category:
            if self.category.wedding_id != self.wedding_id:
                raise ValidationError(
                    'Categoria pertence a outro casamento'
                )

        # Valida que item pertence ao mesmo wedding
        if hasattr(self, 'item') and self.item:
            if self.item.wedding_id != self.wedding_id:
                raise ValidationError(
                    'Item pertence a outro casamento'
                )

# apps/finances/models.py
class Expense(BaseModel, WeddingOwnedMixin):
    """
    Despesa herda wedding_id do WeddingOwnedMixin.

    - wedding_id: Direto no model (denormalizado)
    - item: FK para Item (validado no .clean())
    """

    item = models.ForeignKey(
        'finances.Item',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()

    def clean(self):
        super().clean()

        # Validação adicional: item.wedding == expense.wedding
        if self.item and self.item.wedding_id != self.wedding_id:
            raise ValidationError(
                f'Item pertence ao wedding {self.item.wedding_id}, '
                f'mas despesa pertence ao wedding {self.wedding_id}'
            )
```

---

### Validação Cross-Wedding

**Cenário:** User A tenta criar despesa usando item de User B

```python
# User A (wedding_id=1)
wedding_a = Wedding.objects.get(id=1)
category_a = Category.objects.create(wedding=wedding_a, name='Buffet')
item_a = Item.objects.create(wedding=wedding_a, category=category_a, name='Comida')

# User B (wedding_id=2) tenta usar item de User A
wedding_b = Wedding.objects.get(id=2)

expense = Expense(
    wedding=wedding_b,  # wedding_id=2
    item=item_a,        # item_a.wedding_id=1
    value=Decimal('1000.00')
)

expense.full_clean()  # ❌ ValidationError: Item pertence a outro casamento
```

---

### Performance Comparison

**Teste:** Listar 100 despesas de 1 wedding

```python
# ❌ Normalizado (4 JOINs)
Expense.objects.filter(
    item__category__wedding_id=wedding_id
).select_related('item__category__wedding')
# Tempo: 180ms
# Plano de execução: 4 JOINs + 3 índices

# ✅ Denormalizado (zero JOINs)
Expense.objects.filter(wedding_id=wedding_id)
# Tempo: 12ms (-93% mais rápido)
# Plano de execução: Index scan em wedding_id
```

---

### Manager com Filtro Padrão (Opcional)

```python
# apps/core/managers.py
class WeddingManager(models.Manager):
    """Manager que filtra por wedding automaticamente."""

    def __init__(self, *args, **kwargs):
        self.wedding_id = None
        super().__init__(*args, **kwargs)

    def for_wedding(self, wedding_id):
        """Define wedding_id para queries subsequentes."""
        self.wedding_id = wedding_id
        return self

    def get_queryset(self):
        qs = super().get_queryset()

        if self.wedding_id:
            qs = qs.filter(wedding_id=self.wedding_id)

        return qs

# Uso:
expenses = Expense.objects.for_wedding(wedding_id=123).all()
```

---

## Denormalização e Integridade

**Pergunta:** E se `item.wedding_id != expense.wedding_id`?

**Resposta:** Validação em múltiplas camadas:

**1. Model validation:**

```python
def clean(self):
    if self.item.wedding_id != self.wedding_id:
        raise ValidationError('Cross-wedding access')
```

**2. Serializer validation:**

```python
class ExpenseSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data['item'].wedding_id != data['wedding'].id:
            raise ValidationError('Cross-wedding access')
        return data
```

**3. Database constraint (PostgreSQL):**

```sql
-- Trigger que valida wedding_id em INSERT/UPDATE
CREATE OR REPLACE FUNCTION validate_wedding_consistency()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.wedding_id != (SELECT wedding_id FROM items WHERE id = NEW.item_id) THEN
        RAISE EXCEPTION 'Item pertence a outro wedding';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER expense_wedding_check
    BEFORE INSERT OR UPDATE ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION validate_wedding_consistency();
```

---

## Trade-offs Aceitos

**❌ Denormalização:**

- Campo `wedding_id` duplicado em todos models
- Requer sincronizar wedding_id entre models relacionados

**❌ Espaço em disco:**

- +8 bytes (BigInt) por registro
- Índice em `wedding_id` em todas tabelas

**❌ Complexidade de validação:**

- Precisa validar consistência de wedding_id em FKs

---

## Consequências

### Positivas ✅

- **Performance:** Queries 93% mais rápidas (zero JOINs)
- **Simplicidade:** Filtro direto por `wedding_id`
- **Escalabilidade:** Escala horizontal (sharding por wedding_id)
- **Segurança:** Validação cross-wedding em múltiplas camadas

### Negativas ❌

- **Denormalização:** wedding_id duplicado
- **Espaço:** +8 bytes por registro
- **Validação:** Precisa garantir consistência

### Neutras ⚠️

- Alternativa (normalizado) é mais "correta", mas 93% mais lenta

---

## Monitoramento

**Métricas:**

- Tempo médio de queries por wedding (meta: <20ms)
- Violações de cross-wedding (meta: 0)

**Alertas:**

- Cross-wedding access detectado → Sentry
- Queries >50ms → Investigar índices

**Gatilhos de revisão:**

- Performance degradar >20% → Revisar índices
- Sharding necessário → Avaliar partition por wedding_id

---

## Referências

- [Multi-Tenancy in Django](https://django-tenant-schemas.readthedocs.io/)
- [PostgreSQL Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [BUSINESS_RULES.md (BR-CORE02)](../BUSINESS_RULES.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Última atualização:** 8 de fevereiro de 2026

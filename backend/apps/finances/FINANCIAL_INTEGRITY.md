# Documentação Técnica: Integridade e Auditoria Financeira

**Módulo:** `finances`

**Conceito:** Persistência de Dados vs. Lógica de Negócio

---

## 1. O Dogma da Imutabilidade Financeira

Em um software de gestão de eventos, **dinheiro gasto é um fato histórico**. Fatos não podem ser deletados sem causar um colapso na realidade contábil do sistema. Portanto, a exclusão física de registros financeiros é estritamente proibida uma vez que existam transações vinculadas.

---

## 2. Estratégia de Deleção em Duas Camadas

### A. BudgetCategory (Soft Delete)

A categoria (`BudgetCategory`) utiliza **Soft Delete** (`is_deleted=True`).

- **Por que:** Permite que o usuário "limpe" sua interface removendo categorias que não deseja mais planejar.

- **Resguardo:** Se a categoria continha gastos reais (`Expense`), esses dados permanecem no banco de dados. Isso evita que o "Gasto Total" do casamento mude retroativamente, o que seria uma mentira contábil.

### B. Expense (on_delete=PROTECT)

A despesa (`Expense`) protege sua categoria via `models.PROTECT`.

- **Por que:** É a trava de segurança definitiva. Impede que qualquer processo (manual ou automatizado) remova fisicamente uma categoria que possua compromissos financeiros.

- **Resguardo:** Garante que toda `Installment` (parcela/boleto) sempre tenha um "pai" (`Expense`) e um "avô" (`Category`). Sem isso, você teria boletos órfãos e o cerimonialista não saberia o que está pagando.

---

## 3. Gestão do "Gap" Orçamentário (O Rombo)

Ao "apagar" uma categoria que possui um `allocated_budget` (valor planejado), o sistema gera uma discrepância entre o **Total Estimado do Casamento** e a **Soma das Categorias Ativas**.

### Regras de Negócio para o Desenvolvedor:

1. **O Saldo Livre:** O sistema deve calcular o saldo disponível como:
   ```
   Saldo = Total_Estimado - Sum(Categorias_Ativas.allocated_budget)
   ```

2. **Transparência:** Se o usuário deleta uma categoria de R$ 10.000, esse valor deve retornar para o "Saldo Livre" do casamento. O "rombo" é, na verdade, dinheiro que voltou para a reserva e aguarda nova alocação.

3. **Auditoria:** O Dashboard deve sempre considerar `Sum(Todas_as_Despesas)`, **incluindo as de categorias deletadas**, para que o cálculo de "Saúde Financeira" seja baseado na realidade do que saiu do bolso, e não apenas no que está visível na tela.

---

## 4. Consequências de Violar esta Arquitetura

Se você alterar para `CASCADE` ou remover o Soft Delete:

- **Erro de Performance:** Você terá que recalcular tudo via Python porque perdeu as referências de banco.

- **Perda de Confiança:** O usuário verá o saldo do casamento mudar sozinho ao apagar uma pasta, perdendo a confiança nos cálculos do software.

- **Caos Jurídico:** Contratos vinculados a despesas apagadas ficarão em um limbo sistêmico.

---

## 5. Queries Seguras para Dashboard

### ❌ ERRADO (considera apenas categorias ativas):
```python
total_spent = BudgetCategory.objects.filter(
    budget=budget
).aggregate(Sum('expenses__actual_amount'))
```

### ✅ CORRETO (considera todas despesas, mesmo de categorias deletadas):
```python
total_spent = Expense.objects.filter(
    category__budget=budget
).aggregate(Sum('actual_amount'))
```

### ✅ CORRETO (saldo livre considerando apenas categorias ativas):
```python
allocated_active = BudgetCategory.objects.filter(
    budget=budget,
    is_deleted=False
).aggregate(Sum('allocated_budget'))['allocated_budget__sum'] or Decimal('0')

free_budget = budget.total_estimated - allocated_active
```

---

## 6. Migrations e Integridade

Ao criar migrations:

```python
# ✅ CORRETO
migrations.AddField(
    model_name='expense',
    name='category',
    field=models.ForeignKey(
        on_delete=django.db.models.deletion.PROTECT,  # ← NUNCA CASCADE
        related_name='expenses',
        to='finances.budgetcategory',
    ),
)
```

---

## 7. Admin Actions

No Django Admin, **desabilite** a ação de delete em massa para `Expense` e `Installment`:

```python
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        # Bloqueia delete via admin
        return False
```

Para `BudgetCategory`, permita delete (soft delete ocorrerá automaticamente).

---

## 8. Testes Obrigatórios

```python
def test_cannot_hard_delete_category_with_expenses():
    """Tenta deletar categoria com despesas → deve falhar"""
    category = BudgetCategory.objects.create(...)
    Expense.objects.create(category=category, ...)

    with pytest.raises(ProtectedError):
        category.hard_delete()

def test_soft_delete_category_preserves_expenses():
    """Soft delete de categoria não afeta despesas"""
    category = BudgetCategory.objects.create(...)
    expense = Expense.objects.create(category=category, ...)

    category.delete()  # Soft delete

    assert category.is_deleted is True
    assert Expense.objects.filter(pk=expense.pk).exists()  # ← Despesa ainda existe
```

---

**Autor:** Rafael
**Data:** 2026-02-03
**Versão:** 1.0

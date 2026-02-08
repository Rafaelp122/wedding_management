# ADR-010: Tolerância Zero em Cálculos Financeiros

**Status:** Aceito
**Data:** Janeiro 2025
**Decisor:** Rafael
**Contexto:** Precisão absoluta em somas financeiras (zero arredondamentos)

---

## Contexto e Problema

Cálculos financeiros com float geram erros de arredondamento:

```python
# ❌ PROBLEMA: Float não é exato
total = 1000.00
installment_1 = total / 3  # 333.33333...
installment_2 = total / 3  # 333.33333...
installment_3 = total / 3  # 333.33333...

sum_installments = installment_1 + installment_2 + installment_3
# 999.99999... (faltam R$0.00001 centavos!)

sum_installments == total  # False ❌
```

**Requisitos:**

1. Soma das parcelas EXATAMENTE igual ao valor do contrato (zero tolerância)
2. Usar `Decimal` para precisão (não `float`)
3. Validação automática de integridade financeira

**Alternativas:**

1. **Float com tolerância** (ex: `abs(diff) < 0.01`)
2. **Decimal com tolerância** (ex: `abs(diff) < Decimal('0.01')`)
3. **Decimal com tolerância zero** (escolhido)

---

## Decisão

Usar **`Decimal` com tolerância zero**:

- ZERO arredondamentos (precisão absoluta)
- Ajuste de centavos na última parcela
- Validação automática `sum(installments) == contract.total_value`

---

## Justificativa

### Comparação de Abordagens

| Aspecto          | Decimal (tolerância zero) | Float (tolerância 0.01) | Decimal (tolerância 0.01) |
| ---------------- | ------------------------- | ----------------------- | ------------------------- |
| **Precisão**     | ✅ Exata                  | ❌ Aproximada           | ⚠️ Quase exata            |
| **Auditoria**    | ✅ Sem discrepâncias      | ❌ Aceita erros         | ⚠️ Aceita erros pequenos  |
| **Complexidade** | ⚠️ Ajuste última parcela  | ✅ Simples              | ✅ Simples                |
| **Conformidade** | ✅ Bancário/Legal         | ❌ Não conforme         | ⚠️ Pode não ser conforme  |

---

### Problema com Float

```python
# ❌ Float gera erros de arredondamento
from decimal import Decimal

contract_value = 1000.00  # Float

installments = [
    contract_value / 3,  # 333.3333333333333
    contract_value / 3,  # 333.3333333333333
    contract_value / 3   # 333.3333333333333
]

sum(installments) == contract_value
# False ❌ (999.9999999999998 != 1000.00)

# Diferença:
abs(sum(installments) - contract_value)
# 0.0000000000002 centavos
```

---

### Solução com Decimal (Tolerância Zero)

```python
# ✅ Decimal com precisão absoluta
from decimal import Decimal, ROUND_DOWN

def distribute_installments(total_value: Decimal, count: int) -> list[Decimal]:
    """
    Distribui valor em parcelas iguais com ajuste na última.

    Estratégia:
    1. Calcula parcela base (arredonda para baixo)
    2. Calcula ajuste (diferença)
    3. Adiciona ajuste na última parcela

    Garante: sum(installments) == total_value (tolerância zero)
    """

    # Parcela base (arredondada para baixo)
    base_value = (total_value / count).quantize(
        Decimal('0.01'),
        rounding=ROUND_DOWN
    )

    # Ajuste (diferença que sobrou)
    adjustment = total_value - (base_value * count)

    # Distribui parcelas
    installments = [base_value] * count
    installments[-1] += adjustment  # Adiciona ajuste na última

    # Validação (tolerância zero)
    assert sum(installments) == total_value

    return installments

# Exemplo:
total = Decimal('1000.00')
installments = distribute_installments(total, 3)

print(installments)
# [Decimal('333.33'), Decimal('333.33'), Decimal('333.34')]
#                                        ↑ Ajuste de R$0.01

sum(installments) == total
# True ✅ (1000.00 == 1000.00)
```

---

### Implementação no Model

```python
# apps/finances/models.py
from decimal import Decimal, ROUND_DOWN
from django.db import models
from django.core.exceptions import ValidationError

class Contract(BaseModel, SoftDeleteModel, WeddingOwnedModel):
    supplier = models.ForeignKey('logistics.Supplier', on_delete=models.PROTECT)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        """Valida tolerância zero."""
        super().clean()

        # Calcula soma das parcelas
        installments_sum = self.installments.aggregate(
            models.Sum('value')
        )['value__sum'] or Decimal('0')

        # Validação: tolerância zero
        if installments_sum != self.total_value:
            raise ValidationError(
                f'Soma das parcelas ({installments_sum}) != '
                f'Valor do contrato ({self.total_value})'
            )

class Installment(BaseModel, WeddingOwnedModel):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    number = models.PositiveSmallIntegerField()  # 1, 2, 3...
    value = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pendente'),
            ('PAID', 'Pago'),
            ('OVERDUE', 'Vencida')
        ]
    )

    class Meta:
        unique_together = [['contract', 'number']]
        ordering = ['number']
```

---

### Implementação no Service

```python
# apps/finances/services.py
from decimal import Decimal, ROUND_DOWN

class InstallmentService:
    @staticmethod
    def create_installments(contract, count: int, first_due_date):
        """
        Cria parcelas com tolerância zero.

        Args:
            contract: Contrato
            count: Quantidade de parcelas
            first_due_date: Data de vencimento da 1ª parcela

        Returns:
            list[Installment]: Parcelas criadas

        Raises:
            ValidationError: Violação de tolerância zero
        """

        # Distribui valor com ajuste na última
        values = InstallmentService._distribute_value(
            contract.total_value,
            count
        )

        installments = []

        for i, value in enumerate(values, start=1):
            due_date = first_due_date + timedelta(days=30 * (i - 1))

            installment = Installment.objects.create(
                contract=contract,
                wedding=contract.wedding,
                number=i,
                value=value,
                due_date=due_date,
                status='PENDING'
            )

            installments.append(installment)

        # Validação final (tolerância zero)
        InstallmentService._validate_zero_tolerance(contract)

        return installments

    @staticmethod
    def _distribute_value(total: Decimal, count: int) -> list[Decimal]:
        """Distribui valor em parcelas com ajuste na última."""

        # Parcela base (arredonda para baixo)
        base_value = (total / count).quantize(
            Decimal('0.01'),
            rounding=ROUND_DOWN
        )

        # Ajuste (diferença)
        adjustment = total - (base_value * count)

        # Cria lista de parcelas
        values = [base_value] * count
        values[-1] += adjustment  # Ajusta última parcela

        # Validação interna
        assert sum(values) == total, 'Tolerância zero violada'

        return values

    @staticmethod
    def _validate_zero_tolerance(contract):
        """Valida que soma das parcelas == valor do contrato."""

        installments_sum = Installment.objects.filter(
            contract=contract
        ).aggregate(Sum('value'))['value__sum'] or Decimal('0')

        if installments_sum != contract.total_value:
            raise ValidationError(
                f'Tolerância zero violada: '
                f'Soma={installments_sum}, Total={contract.total_value}'
            )
```

---

### Exemplo de Uso

```python
# Cria contrato
contract = Contract.objects.create(
    wedding=wedding,
    supplier=supplier,
    total_value=Decimal('1000.00')  # R$1.000,00
)

# Cria 3 parcelas
installments = InstallmentService.create_installments(
    contract=contract,
    count=3,
    first_due_date=date(2025, 2, 1)
)

# Resultado:
for installment in installments:
    print(f'Parcela {installment.number}: R${installment.value}')

# Parcela 1: R$333.33
# Parcela 2: R$333.33
# Parcela 3: R$333.34  ← Ajuste de R$0.01

# Validação:
sum([i.value for i in installments]) == contract.total_value
# True ✅ (1000.00 == 1000.00)
```

---

### Casos de Teste

```python
# tests/test_tolerance_zero.py
import pytest
from decimal import Decimal

def test_distribute_installments_3_parcelas():
    """Testa distribuição em 3 parcelas."""
    total = Decimal('1000.00')
    values = InstallmentService._distribute_value(total, 3)

    assert values == [
        Decimal('333.33'),
        Decimal('333.33'),
        Decimal('333.34')  # Ajuste
    ]

    assert sum(values) == total  # Tolerância zero ✅

def test_distribute_installments_7_parcelas():
    """Testa distribuição em 7 parcelas."""
    total = Decimal('1000.00')
    values = InstallmentService._distribute_value(total, 7)

    assert values == [
        Decimal('142.85'),
        Decimal('142.85'),
        Decimal('142.85'),
        Decimal('142.85'),
        Decimal('142.85'),
        Decimal('142.85'),
        Decimal('142.90')  # Ajuste de R$0.05
    ]

    assert sum(values) == total  # Tolerância zero ✅

def test_distribute_installments_100_parcelas():
    """Testa distribuição em 100 parcelas."""
    total = Decimal('9999.99')
    values = InstallmentService._distribute_value(total, 100)

    # 99 parcelas de R$99.99 + 1 parcela de R$100.00
    assert values[0] == Decimal('99.99')
    assert values[-1] == Decimal('100.00')  # Ajuste de R$0.01

    assert sum(values) == total  # Tolerância zero ✅

def test_tolerance_zero_validation():
    """Testa validação de tolerância zero."""
    contract = Contract.objects.create(
        wedding=wedding,
        supplier=supplier,
        total_value=Decimal('1000.00')
    )

    # Cria parcelas com soma INCORRETA
    Installment.objects.create(contract=contract, value=Decimal('500.00'))
    Installment.objects.create(contract=contract, value=Decimal('499.99'))

    # Validação deve falhar
    with pytest.raises(ValidationError, match='Tolerância zero violada'):
        InstallmentService._validate_zero_tolerance(contract)
```

---

## Por Que Ajustar a Última Parcela?

**Alternativas:**

1. **Ajustar primeira parcela:** Usuário pode estranhar valor diferente logo no início
2. **Distribuir centavos aleatoriamente:** Dificulta auditoria (sem padrão)
3. **Ajustar última parcela:** Padrão bancário (escolhido)

**Vantagem:**

- Usuário vê parcelas iguais (333.33, 333.33, 333.33...)
- Ajuste pequeno na última (333.34) é esperado

---

## Trade-offs Aceitos

**❌ Complexidade:**

- Lógica de ajuste na última parcela
- Precisa validar tolerância zero em múltiplas camadas

**❌ Performance:**

- Query `SUM(value)` para validar tolerância

**❌ UX:**

- Última parcela pode ter valor diferente (confuso para user)

---

## Consequências

### Positivas ✅

- **Precisão:** Zero erros de arredondamento
- **Auditoria:** Soma sempre bate (fácil reconciliar)
- **Conformidade:** Padrão bancário/legal
- **Confiança:** User sabe que cálculos estão corretos

### Negativas ❌

- **Complexidade:** Lógica de ajuste
- **Performance:** Query SUM para validar
- **UX:** Última parcela com valor diferente

### Neutras ⚠️

- Alternativa (tolerância 0.01) é mais simples, mas viola precisão

---

## Monitoramento

**Métricas:**

- Violações de tolerância zero (meta: 0)
- Contratos com soma != total (meta: 0)

**Alertas:**

- Tolerância zero violada → Sentry (critical)
- Soma das parcelas != total → Slack (urgent)

**Gatilhos de revisão:**

- Qualquer violação de tolerância → Investigar imediatamente
- User reporta "soma errada" → Revisar lógica de ajuste

---

## Referências

- [Python Decimal Module](https://docs.python.org/3/library/decimal.html)
- [IEEE 754 Floating Point Problems](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- [Banker's Rounding](https://en.wikipedia.org/wiki/Rounding#Round_half_to_even)
- [BUSINESS_RULES.md (BR-FIN03)](../BUSINESS_RULES.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Última atualização:** 8 de fevereiro de 2026

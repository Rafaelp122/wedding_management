# ADR-006: Service Layer Pattern

**Status:** Aceito
**Data:** Janeiro 2025
**Decisor:** Rafael
**Contexto:** Separação de responsabilidades entre Views, Serializers e Models

---

## Contexto e Problema

Django REST Framework coloca lógica de negócio em 3 lugares:

- **Views:** Validações, orquestrações
- **Serializers:** `.validate()`, `.create()`, `.update()`
- **Models:** Métodos, properties, signals

**Problemas:**

1. **Testabilidade:** Precisa mockar `request` para testar lógica
2. **Reusabilidade:** Lógica presa ao serializer (não reutilizável)
3. **Complexidade:** Serializers com 200+ linhas de `.validate()`
4. **Acoplamento:** Mudança no serializer quebra testes não relacionados

---

## Decisão

Introduzir **Service Layer** para encapsular lógica de negócio complexa.

---

## Justificativa

### Comparação de Arquiteturas

| Aspecto           | Service Layer (escolhido)  | Fat Serializer     | Fat Model          |
| ----------------- | -------------------------- | ------------------ | ------------------ |
| **Testabilidade** | ✅ Unit test direto        | ❌ Precisa request | ⚠️ Precisa DB      |
| **Reusabilidade** | ✅ Isolado                 | ❌ Acoplado ao DRF | ⚠️ Acoplado ao ORM |
| **Separação**     | ✅ SRP (1 serviço/domínio) | ❌ God serializer  | ❌ God model       |
| **Curva**         | ⚠️ Mais abstrações         | ✅ Padrão DRF      | ✅ Padrão Django   |

---

### Estrutura Proposta

```
apps/finances/
├── models.py          # APENAS models (zero lógica de negócio)
├── serializers.py     # APENAS validação de tipos/formato
├── services.py        # ✅ TODA lógica de negócio aqui
└── views.py           # APENAS HTTP (deserializa → service → serializa)
```

**Fluxo de request:**

```
Request (JSON)
   ↓
ViewSet (valida permissão)
   ↓
Serializer (valida formato: is_valid())
   ↓
Service (lógica de negócio)
   ↓
Models (persistência)
   ↓
Serializer (serializa response)
   ↓
Response (JSON)
```

---

### Exemplo Antes (Fat Serializer)

```python
# ❌ ANTES: Lógica no serializer (difícil testar)
class InstallmentSerializer(serializers.ModelSerializer):
    def validate(self, data):
        # 50 linhas de validação de tolerância zero
        # 30 linhas de validação de parcelas duplicadas
        # 20 linhas de validação de data de vencimento
        ...

    def create(self, validated_data):
        # Cria parcela
        # Atualiza total pago do contrato
        # Envia email
        # Cria notificação
        ...
```

**Problemas:**

- Como testar lógica sem mockar `request`?
- Como reutilizar validação em outro endpoint?
- `.create()` faz 4 coisas diferentes (SRP violation)

---

### Exemplo Depois (Service Layer)

```python
# ✅ DEPOIS: Lógica isolada em serviço

# apps/finances/serializers.py
class InstallmentSerializer(serializers.ModelSerializer):
    """Serializer APENAS valida tipos/formato (não lógica de negócio)."""

    class Meta:
        model = Installment
        fields = ['id', 'contract', 'number', 'value', 'due_date', 'status']

    def validate_value(self, value):
        """Valida formato (não lógica de negócio)."""
        if value <= 0:
            raise ValidationError('Valor deve ser positivo')
        return value

# apps/finances/services.py
class InstallmentService:
    """Service concentra TODA lógica de negócio de parcelas."""

    @staticmethod
    def create_installment(contract, number, value, due_date):
        """
        Cria parcela com validações de negócio.

        Raises:
            ValidationError: Violação de regra de negócio
        """
        # Validação de negócio #1: Tolerância zero
        if not InstallmentService._validate_zero_tolerance(contract, value):
            raise ValidationError('Soma das parcelas != valor do contrato')

        # Validação de negócio #2: Parcela duplicada
        if Installment.objects.filter(contract=contract, number=number).exists():
            raise ValidationError(f'Parcela {number} já existe')

        # Validação de negócio #3: Data de vencimento
        if due_date < contract.signature_date:
            raise ValidationError('Vencimento não pode ser antes da assinatura')

        # Cria parcela
        installment = Installment.objects.create(
            contract=contract,
            number=number,
            value=value,
            due_date=due_date,
            status='PENDING'
        )

        # Efeitos colaterais (isolados)
        ContractService.update_paid_total(contract)
        NotificationService.notify_installment_created(installment)
        EmailService.send_installment_reminder(installment)

        return installment

    @staticmethod
    def _validate_zero_tolerance(contract, new_value):
        """Valida que soma das parcelas == valor do contrato."""
        existing_sum = Installment.objects.filter(
            contract=contract
        ).aggregate(Sum('value'))['value__sum'] or Decimal('0')

        total = existing_sum + new_value
        return total == contract.total_value

# apps/finances/views.py
class InstallmentViewSet(viewsets.ModelViewSet):
    """View APENAS orquestra (não contém lógica de negócio)."""

    def create(self, request):
        # Valida formato (serializer)
        serializer = InstallmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Delega lógica para service
        installment = InstallmentService.create_installment(
            contract=serializer.validated_data['contract'],
            number=serializer.validated_data['number'],
            value=serializer.validated_data['value'],
            due_date=serializer.validated_data['due_date']
        )

        # Serializa response
        return Response(
            InstallmentSerializer(installment).data,
            status=201
        )
```

---

### Benefícios para Testes

```python
# ✅ ANTES: Teste do Service (unit test puro)
def test_create_installment_validates_zero_tolerance():
    contract = Contract(total_value=Decimal('1000.00'))

    with pytest.raises(ValidationError, match='Soma das parcelas'):
        InstallmentService.create_installment(
            contract=contract,
            number=1,
            value=Decimal('999.00'),  # Faltam R$1.00
            due_date=date.today()
        )

    # Zero mocks! Teste direto da lógica

# ❌ DEPOIS: Teste do Serializer (precisa mockar request)
def test_create_installment_validates_zero_tolerance():
    request = RequestFactory().post('/', data={...})
    request.user = User(...)  # Mock

    serializer = InstallmentSerializer(data={...}, context={'request': request})

    with pytest.raises(ValidationError):
        serializer.save()

    # Precisa mockar HTTP, user, context...
```

---

## Quando Usar Service Layer?

**✅ USE quando:**

- Lógica envolve múltiplos models (Contract + Installment)
- Validação complexa (tolerância zero, duplicatas)
- Efeitos colaterais (emails, notificações)
- Precisa reutilizar lógica (API + task agendada)

**❌ NÃO USE quando:**

- CRUD simples (list, retrieve, delete)
- Zero lógica de negócio (apenas persistência)
- Model tem 1-2 campos apenas

**Exemplo de CRUD simples (sem service):**

```python
class SupplierViewSet(viewsets.ModelViewSet):
    """CRUD simples (sem service)."""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
```

---

## Estrutura de Services

```python
# apps/finances/services.py
class ExpenseService:
    """Serviço de domínio para despesas."""

    @staticmethod
    def create_expense(category, item, value, payment_date):
        """Cria despesa com validações de negócio."""
        ...

    @staticmethod
    def update_expense(expense, value):
        """Atualiza despesa recalculando totais."""
        ...

    @staticmethod
    def _validate_expense_rules(category, value):
        """Validação interna (privada)."""
        ...

class ContractService:
    """Serviço de domínio para contratos."""

    @staticmethod
    def create_contract_with_installments(supplier, total, installments_count):
        """Cria contrato e gera parcelas automaticamente."""
        ...

    @staticmethod
    def update_paid_total(contract):
        """Recalcula total pago baseado nas parcelas."""
        ...
```

---

## Trade-offs Aceitos

**❌ Mais arquivos:**

- Antes: 3 arquivos (models, serializers, views)
- Depois: 4 arquivos (+ services)

**❌ Curva de aprendizado:**

- Devs precisam entender novo padrão
- Documentação necessária

**❌ Over-engineering em CRUDs simples:**

- Service para `Supplier` (name, contact) é overkill

---

## Consequências

### Positivas ✅

- **Testabilidade:** Unit tests sem mocks HTTP
- **Reusabilidade:** Service usado em views + tasks
- **Separação:** SRP (1 responsabilidade por classe)
- **Manutenibilidade:** Lógica isolada (fácil refatorar)

### Negativas ❌

- **Complexidade:** Mais abstrações
- **Curva:** Devs precisam aprender padrão
- **Boilerplate:** Arquivo extra para lógica simples

### Neutras ⚠️

- Service Layer é padrão em outras linguagens (Java, C#)
- Django/DRF comunidade prefere Fat Models/Serializers

---

## Monitoramento

**Métricas:**

- Cobertura de testes em `services.py` (meta: >90%)
- Linhas de código por serializer (meta: <100)

**Gatilhos de revisão:**

- Serializer com >150 linhas → Extrair para service
- Lógica duplicada entre serializers → Mover para service

---

## Referências

- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [BUSINESS_RULES.md (BR-FIN03)](../BUSINESS_RULES.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Última atualização:** 8 de fevereiro de 2026

# ADR-008: Soft Delete Seletivo

**Status:** Aceito
**Data:** Janeiro 2025
**Decisor:** Rafael
**Contexto:** Estratégia de exclusão lógica para auditoria e recuperação

---

## Contexto e Problema

Hard delete (`DELETE FROM table WHERE id=X`) tem problemas:

1. **Irrecuperável:** Dado deletado não pode ser restaurado
2. **Integridade referencial:** FKs quebram ou cascateiam
3. **Auditoria:** Impossível rastrear quem deletou e quando
4. **Requisito legal:** LGPD pode exigir histórico de dados sensíveis

**Alternativas:**

1. **Hard delete em tudo** (padrão Django)
2. **Soft delete em tudo** (overkill)
3. **Soft delete seletivo** (escolhido)

---

## Decisão

Aplicar **soft delete seletivo**:

- ✅ **COM soft delete:** Wedding, Category, Item, Contract, Supplier
- ❌ **SEM soft delete:** Installment, Event, Notification

---

## Justificativa

### Quando Usar Soft Delete?

| Critério                       | Usar Soft Delete? |
| ------------------------------ | ----------------- |
| Dado pode ser restaurado       | ✅ Sim            |
| Histórico auditável            | ✅ Sim            |
| FKs importantes (ex: Contract) | ✅ Sim            |
| Dado transitório (Event)       | ❌ Não            |
| Volume alto (Notification)     | ❌ Não            |

---

### Comparação de Models

| Model            | Soft Delete? | Justificativa                                |
| ---------------- | ------------ | -------------------------------------------- |
| **Wedding**      | ✅ Sim       | Restaurar casamento completo                 |
| **Category**     | ✅ Sim       | Restaurar categoria de despesas              |
| **Item**         | ✅ Sim       | Restaurar item orçamentário                  |
| **Contract**     | ✅ Sim       | Auditoria legal, restaurar contrato          |
| **Supplier**     | ✅ Sim       | Histórico de fornecedores                    |
| **Installment**  | ❌ Não       | Registro financeiro (imutável após criado)   |
| **Event**        | ❌ Não       | Transitório (tarefa agendada descartável)    |
| **Notification** | ❌ Não       | Volume alto (1000+ por wedding), descartável |

---

### Implementação

**1. Mixin para Soft Delete:**

```python
# apps/core/models.py
from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    """Manager que filtra registros deletados por padrão."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    """
    Model abstrato com soft delete.

    - deleted_at: Timestamp de exclusão (NULL = ativo)
    - objects: Manager padrão (exclui deletados)
    - all_objects: Manager com deletados inclusos
    """

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()      # Padrão: exclui deletados
    all_objects = models.Manager()     # Inclui deletados

    def delete(self, using=None, keep_parents=False):
        """Soft delete: marca deleted_at ao invés de deletar."""
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self):
        """Hard delete real (usar apenas em migrations)."""
        super().delete()

    def restore(self):
        """Restaura registro soft-deletado."""
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True
```

**2. Aplicar em Models Específicos:**

```python
# apps/finances/models.py
class Contract(BaseModel, SoftDeleteModel, WeddingOwnedMixin):
    """
    Contrato COM soft delete (restaurável, auditável).
    """
    supplier = models.ForeignKey('logistics.Supplier', on_delete=models.PROTECT)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

class Installment(BaseModel, WeddingOwnedMixin):
    """
    Parcela SEM soft delete (imutável, registro financeiro).
    """
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    # ZERO soft delete: parcela é registro financeiro imutável
```

**3. Queries Automáticas:**

```python
# ✅ Busca APENAS contratos ativos (deleted_at=NULL)
contracts = Contract.objects.all()

# ✅ Busca TODOS contratos (incluindo deletados)
all_contracts = Contract.all_objects.all()

# ✅ Busca contratos deletados
deleted_contracts = Contract.all_objects.filter(deleted_at__isnull=False)
```

**4. API Endpoint:**

```python
# apps/finances/views.py
class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()  # Exclui deletados automaticamente

    @action(detail=True, methods=['post'])
    def restore(self, request, uuid=None):
        """Restaura contrato soft-deletado."""
        contract = Contract.all_objects.get(uuid=uuid)

        if not contract.deleted_at:
            raise ValidationError('Contrato não está deletado')

        contract.restore()

        return Response({'status': 'restored'})
```

---

## Por Que NÃO Soft Delete em Installment?

**Installment = Registro financeiro imutável:**

```python
# ❌ PROBLEMA: Soft delete em parcela quebra tolerância zero
contract.total_value = Decimal('1000.00')

# Cria 2 parcelas
Installment.objects.create(contract=contract, value=Decimal('500.00'))
Installment.objects.create(contract=contract, value=Decimal('500.00'))

# ✅ Soma = 1000 (OK)

# User deleta parcela 2
installment_2.delete()  # Soft delete: deleted_at = NOW

# ❌ Soma visível = 500 (quebra tolerância zero!)
Installment.objects.filter(contract=contract).aggregate(Sum('value'))
# {'value__sum': 500}  # Faltam R$500!

# Solução: Installment usa HARD delete
# Deletar parcela requer recalcular distribuição
```

**Regra:** Registro financeiro é imutável. Deletar parcela requer:

1. Hard delete da parcela
2. Recalcular distribuição das parcelas restantes
3. Validar tolerância zero novamente

---

## Por Que NÃO Soft Delete em Event?

**Event = Dado transitório de agendamento:**

```python
# Event: "Enviar lembrete 7 dias antes do casamento"
Event.objects.create(
    type='PAYMENT_REMINDER',
    scheduled_for=wedding.date - timedelta(days=7),
    status='PENDING'
)

# Após executar:
event.status = 'EXECUTED'
event.save()

# ❌ PROBLEMA: Acumula 1000+ eventos por wedding
Event.objects.filter(wedding=wedding).count()
# 1234 eventos (maioria executed)

# Solução: Hard delete eventos executed após 30 dias
Event.objects.filter(
    status='EXECUTED',
    created_at__lt=timezone.now() - timedelta(days=30)
).delete()
```

---

## Por Que NÃO Soft Delete em Notification?

**Notification = Volume alto, descartável:**

```python
# Casamento gera 500+ notificações ao longo de 12 meses
Notification.objects.filter(wedding=wedding).count()
# 567 notificações

# User "limpa" notificações antigas
# ❌ Soft delete: 567 registros continuam no banco (apenas hidden)
# ✅ Hard delete: Remove definitivamente (libera espaço)

# Solução: Hard delete notificações lidas após 90 dias
Notification.objects.filter(
    is_read=True,
    created_at__lt=timezone.now() - timedelta(days=90)
).delete()
```

---

## Trade-offs Aceitos

**❌ Complexidade de queries:**

```python
# Precisa lembrar qual Manager usar
Contract.objects.all()      # Sem deletados
Contract.all_objects.all()  # Com deletados
```

**❌ Espaço em disco:**

- Soft delete acumula registros deletados
- Requer cleanup periódico (task agendada)

**❌ Performance:**

- Índice em `deleted_at` adiciona overhead
- Queries precisam filtrar `deleted_at IS NULL`

---

## Consequências

### Positivas ✅

- **Recuperação:** User pode restaurar contrato deletado acidentalmente
- **Auditoria:** Histórico completo de exclusões
- **Integridade:** FKs continuam válidas após delete

### Negativas ❌

- **Complexidade:** Dois managers (objects vs all_objects)
- **Espaço:** Registros deletados acumulam
- **Performance:** Índice adicional em deleted_at

### Neutras ⚠️

- Alternativa (hard delete) é mais simples, mas irrecuperável

---

## Monitoramento

**Métricas:**

- Quantidade de registros soft-deletados (meta: <5% do total)
- Taxa de restauração (meta: >10% dos deletes são restaurados)

**Alertas:**

- Soft-deletados >10% do total → Cleanup necessário
- Zero restaurações em 30 dias → Revisar necessidade de soft delete

**Gatilhos de revisão:**

- Espaço em disco >80% → Avaliar cleanup
- Performance de queries degradar >20% → Revisar índices

---

## Referências

- [Django Soft Delete Patterns](https://django-safedelete.readthedocs.io/)
- [LGPD - Lei Geral de Proteção de Dados](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
- [BUSINESS_RULES.md (BR-CORE04)](../BUSINESS_RULES.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Última atualização:** 8 de fevereiro de 2026

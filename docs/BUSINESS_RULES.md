# 📐 Regras de Negócio - Wedding Management System

## Versão 2.0

---

## 1. Introdução

Este documento centraliza todas as **Regras de Negócio (Business Rules)** do sistema, separadas dos Requisitos Funcionais.

**Diferença:**

- **Requisito Funcional:** "O sistema deve permitir criar contratos"
- **Regra de Negócio:** "Um contrato SIGNED exige valor total > 0 e arquivo PDF"

---

## 2. Domínio: Weddings (Casamento)

### **BR-W01: Status do Casamento**

**Regra:** Um casamento só pode ser marcado como `COMPLETED` se a data do evento já passou.

**Validação:**

```python
if self.status == StatusChoices.COMPLETED:
    if self.date > timezone.now().date():
        raise ValidationError(
            "Não pode marcar como CONCLUÍDO antes da data do casamento"
        )
```

**Motivo:** Prevenir erro humano de concluir casamento prematuramente.

**Status:** ✅ Implementado em `Wedding.clean()`

---

### **BR-W02: Isolamento de Dados (Multitenancy)**

**Regra:** Um Planner só pode acessar casamentos que ele mesmo criou.

**Implementação:**

```python
# Views sempre filtram por planner
queryset = Wedding.objects.filter(planner=request.user)
```

**Motivo:** Segurança e privacidade (LGPD).

**Status:** 🏗️ Definido (Aguardando implementação nas ViewSets)

---

## 3. Domínio: Finances (Financeiro)

### **BR-F01: Integridade de Parcelas (Tolerância Zero)**

**Regra:** A soma das parcelas deve ser EXATAMENTE igual ao valor total da despesa.

**Fórmula:**

```
Sendo V o valor total e n o número de parcelas:
- Valor base: vb = round(V/n, 2)
- Primeiras n-1 parcelas: vb
- Última parcela: vn = V - (vb × (n-1))  ← absorve arredondamento
```

**Validação:**

```python
total_installments = self.installments.aggregate(
    Sum('amount')
)['amount__sum'] or Decimal('0.00')

if total_installments != self.actual_amount:  # Comparação exata
    raise ValidationError(
        f"ERRO DE INTEGRIDADE: A soma das parcelas (R${total_installments}) "
        f"não bate com o valor total (R${self.actual_amount})."
    )
```

**Exemplo Prático:**

```python
# R$ 10.000 / 3
vb = round(10000 / 3, 2) = 3333.33
v1 = 3333.33
v2 = 3333.33
v3 = 10000 - (3333.33 × 2) = 3333.34  # ← ajuste automático
# Soma: 3333.33 + 3333.33 + 3333.34 = 10000.00 ✅
```

**Benefícios:**

- ✅ Auditoria contábil sem ressalvas
- ✅ Conciliação bancária automática
- ✅ Zero divergências em relatórios

**Status:** ✅ Implementado em `Expense.clean()`

---

### **BR-F02: Âncora Jurídica (Contract ↔ Expense)**

**Regra:** Expense vinculada a Contract deve ter `actual_amount` **igual** ao `total_amount` do contrato.

**Validação:**

```python
# apps/finances/models/expense.py
if self.contract and self.actual_amount != self.contract.total_amount:
    raise ValidationError(
        f"Valor da despesa (R${self.actual_amount}) != "
        f"valor do contrato (R${self.contract.total_amount})"
    )
```

**Regra de Alteração:**

- Alterações no valor exigem edição do contrato ou aditivo jurídico
- Sistema bloqueia divergência entre contrato e despesa

**Motivo:**

- Garantir que o valor contratual seja a "fonte da verdade"
- Prevenir divergências entre módulo jurídico e financeiro

**Status:** ✅ Implementado em `Expense.clean()`

---

### **BR-F03: Consistência de Status de Pagamento**

**Regra:** Uma parcela com `paid_date` preenchida DEVE ter `status = PAID`.

**Validação:**

```python
if self.paid_date and self.status != StatusChoices.PAID:
    raise ValidationError(
        "Parcela com data de pagamento deve ter status PAGO"
    )

if self.status == StatusChoices.PAID and not self.paid_date:
    raise ValidationError(
        "Parcela PAGA precisa ter data de pagamento preenchida"
    )
```

**Status:** ✅ Implementado em `Installment.clean()`

---

### **BR-F04: Orçamento por Categoria**

**Regra:** A soma dos gastos de uma categoria não pode exceder o orçamento alocado (soft warning).

**Implementação:**

```python
@property
def is_over_budget(self):
    return self.spent > self.allocated_budget

@property
def budget_health(self):
    percentage = (self.spent / self.allocated_budget * 100) if self.allocated_budget else 0

    if percentage > 100:
        return 'CRITICAL'  # 🚨 Estourou
    elif percentage > 90:
        return 'WARNING'   # ⚠️ Perto do limite
    return 'HEALTHY'       # ✅ OK
```

**Observação:** NÃO bloqueia criação de despesa (soft limit), apenas alerta.

**Status:** 🏗️ Definido (Aguardando implementação de Properties no Model)

---

## 4. Domínio: Logistics (Fornecedores e Contratos)

### **BR-L01: Contrato Assinado Exige PDF e Valor**

**Regra:** Um contrato com `status = SIGNED` DEVE ter:

1. Arquivo PDF anexado
2. Valor total > 0
3. Data de assinatura preenchida

**Validação:**

```python
if self.status == StatusChoices.SIGNED:
    if not self.pdf_file:
        raise ValidationError("Contrato ASSINADO exige arquivo PDF")

    if not self.total_amount or self.total_amount <= 0:
        raise ValidationError("Contrato ASSINADO exige valor total positivo")

    if not self.signed_date:
        raise ValidationError("Informe a data da assinatura")
```

**Status:** ✅ Implementado em `Contract.clean()`

---

### **BR-L02: Isolamento de Orçamento (Cross-Wedding Validation)**

**Regra:** Um `Item` não pode usar uma `BudgetCategory` de outro casamento.

**Validação:**

```python
if self.budget_category.wedding != self.wedding:
    raise ValidationError(
        "A categoria de orçamento não pertence a este casamento"
    )
```

**Motivo:** Prevenir "vazamento" de dados entre casamentos (segurança).

**Status:** ✅ Implementado em `Item.clean()`

---

### **BR-L03: Auto-Geração de Compromissos Financeiros**

**Regra:** Ao assinar um contrato, o sistema deve garantir a integridade do fluxo Contrato → Despesa → Parcelas.:

1. Criar o Contract (Logística).
2. Criar uma Expense (Finanças) como âncora financeira do contrato.
3. Gerar N Installment (Parcelas) vinculadas à despesa, usando a fórmula de tolerância zero.
4. Criar N Event no calendário, vinculados cada um à sua respectiva Installment.

**Implementação:**

```python
# apps/logistics/services.py
from apps.finances.services import ExpenseService
from apps.scheduler.models import Event

@transaction.atomic
def create_contract_with_finance(data, wedding):
    # 1. Cria o Contrato (Logística)
    contract = Contract.objects.create(...)

    # 2. Delega para o Financeiro criar a Despesa e as Parcelas (BR-F01)
    # Isso garante que a lógica de "Tolerância Zero" seja executada em um só lugar
    expense = ExpenseService.create_from_contract(contract)

    # 3. Sincroniza com o Calendário
    current_due_date = contract.first_due_date
    for installment in expense.installments.all():
        Event.objects.create(
            wedding=wedding,
            event_type='PAYMENT',
            installment=installment,  # Link direto para a parcela!
            title=f"Pagar: {contract.supplier.name} ({installment.number}/{expense.installments_count})",
            start_time=installment.due_date,
            reminder_enabled=True,
            reminder_minutes_before=1440  # 24h
        )
```

**Status:** 🏗️ Definido (Aguardando implementação da Service Layer)

---

### **BR-L04: Fornecedor é Compartilhado (User-Owned)**

**Regra:** Um `Supplier` pertence ao **Planner**, não ao casamento.

**Motivo:** Permitir reutilização do mesmo fornecedor em múltiplos casamentos.

**Exemplo:**

```python
# Planner cadastra "Buffet Delícias" uma vez
supplier = Supplier.objects.create(user=planner, name="Buffet Delícias")

# Usa no Casamento A
contract_a = Contract.objects.create(wedding=wedding_a, supplier=supplier)

# Reusa no Casamento B
contract_b = Contract.objects.create(wedding=wedding_b, supplier=supplier)
```

**Status:** ✅ Implementado via `UserOwnedModel`

---

## 5. Domínio: Scheduler (Calendário)

### **BR-S01: Eventos de Pagamento são Automáticos**

**Regra:** Eventos do tipo PAYMENT são "espelhos" das parcelas financeiras e sua gestão é exclusiva do sistema.

**Usuário NÃO pode:**

- ❌ Criar: Proibido criar eventos PAYMENT manualmente (devem vir de uma Installment).
- ❌ Editar: Proibido alterar data ou valor via calendário (deve ser alterado na Installment).
- ❌ Deletar: Proibido deletar o evento (ele morre apenas se a Installment for excluída).

**Motivo:** Garantir que o calendário nunca minta sobre o estado real do fluxo de caixa.

**Implementação Técnica (Backend):**

```python
# apps/scheduler/models.py
def clean(self):
    if self.event_type == 'PAYMENT' and not self.installment:
        raise ValidationError("Eventos de pagamento exigem uma parcela vinculada.")

    if self.pk:
        old_event = Event.objects.get(pk=self.pk)
        if old_event.event_type == 'PAYMENT':
            # Bloqueia alteração manual de campos sensíveis
            if self.start_time != old_event.start_time:
                raise ValidationError("Altere a data da parcela no módulo financeiro.")
```

**Status:** 🏗️ Definido (Aguardando implementação no model Event)

---

### **BR-L05: Status de Aquisição de Itens**

**Regra:** O status de aquisição de um `Item` é independente do status de pagamento. Um item pode estar `ACQUIRED` mesmo se o contrato não foi pago.

**Definição de status:**

```python
class Item(WeddingOwnedModel, SoftDeleteModel):
    class AcquisitionStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        ACQUIRED = "ACQUIRED", "Adquirido"
        DELIVERED = "DELIVERED", "Entregue"
```

**Fluxo normal:**

1. Contrato criado → Item com status `PENDING`
2. Fornecedor entrega → Planner marca `ACQUIRED`
3. Item chega ao local → Planner marca `DELIVERED`

**Motivo:** Desacoplar logística financeira de logística física. Um item pode ser adquirido "a prazo" ou entregue mesmo com pagamento pendente.

**Status:** ✅ Implementado no modelo `Item`

---

## 6. Domínio: Segurança (Cross-Wedding)

### **BR-SEC03: Isolamento Cross-Wedding em Categorias**

**Regra:** Toda operação que envolve `BudgetCategory` deve validar que a categoria pertence ao mesmo `wedding` da entidade relacionada (Expense, Item, etc.).

**Implementação:**

```python
class BudgetCategory(WeddingOwnedModel, SoftDeleteModel):
    def clean(self):
        # Validação adicional: garantir que wedding não mudou
        if self.pk and self._state.fields_cache.get('wedding') != self.wedding:
            raise ValidationError("Não é permitido alterar o wedding de uma categoria")

class Expense(WeddingOwnedModel):
    def clean(self):
        # ... outras validações ...

        # BR-SEC03: Validar que categoria pertence ao mesmo wedding
        if self.category and self.category.wedding != self.wedding:
            raise ValidationError(
                f"Categoria '{self.category.name}' não pertence ao "
                f"casamento '{self.wedding}'"
            )
```

**Cenário bloqueado:**

```python
# Casamento A
wedding_a = Wedding.objects.create(name="João & Maria")
category_a = BudgetCategory.objects.create(wedding=wedding_a, name="Buffet")

# Casamento B
wedding_b = Wedding.objects.create(name="Pedro & Ana")

# ❌ Tentativa de usar categoria do casamento A no casamento B
expense_b = Expense(
    wedding=wedding_b,
    category=category_a,  # ← ERRO!
    actual_amount=5000
)
expense_b.full_clean()  # ValidationError
```

**Motivo:** Prevenir data leakage entre casamentos. Garante isolamento multitenant a nível de objeto.

**Status:** ✅ Implementado via `WeddingOwnedModel` + validação em `clean()`

---

## 7. Domínio: Futuro (V2.0)

### **BR-FUT05: Automação de Inadimplência (OVERDUE)**

**Regra:** O sistema executará verificações diárias via **Cloud Scheduler + OIDC** para detectar parcelas vencidas e atualizar o status para `OVERDUE`.

**Arquitetura:**

```
Cloud Scheduler (diariamente 08:00 BRT)
    ↓ POST /api/tasks/check-overdue
    ↓ Authorization: Bearer <OIDC_TOKEN>
Backend (Django)
    ↓ Verifica OIDC token via Workload Identity
    ↓ Executa: UPDATE installments SET status='OVERDUE' WHERE due_date < NOW() AND status='PENDING'
    ↓ Dispara notificações Resend Email
```

**Endpoint protegido:**

```python
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsOIDCServiceAccount])  # Custom permission
def check_overdue(request):
    """
    Endpoint chamado APENAS pelo Cloud Scheduler via OIDC.
    Requer: Authorization: Bearer <OIDC_TOKEN>
    """
    overdue_count = Installment.objects.filter(
        due_date__lt=timezone.now().date(),
        status='PENDING'
    ).update(status='OVERDUE')

    # Enviar e-mails via Resend
    send_overdue_notifications(overdue_count)

    return Response({'overdue_count': overdue_count})
```

**Segurança:**

- ✅ Endpoint NÃO aceita JWT de usuários
- ✅ Apenas OIDC tokens do Cloud Scheduler
- ✅ Validação de audience e issuer no token

**Motivo:**

- Automação sem custo (Cloud Scheduler free tier: 3 jobs)
- Zero keys/secrets no código (OIDC nativo)
- Escalabilidade (Cloud Run scale-to-zero)

**Status:** 📋 Planejado para V2.0 (Sprint 23-24)

---

### **BR-S02: Lembretes Configuráveis**

**Regra:** Todo evento pode ter lembrete automático configurável.

**Default:**

- Eventos manuais (reunião, visita): 1 hora antes
- Eventos de pagamento: 24 horas antes

**Implementação:**

```python
class Event(BaseModel):
    reminder_enabled = BooleanField(default=False)
    reminder_minutes_before = PositiveIntegerField(default=60)  # 1h
```

**Status:** ✅ Implementado em `Event`

---

### **BR-S03: Lembretes Únicos**

**Regra:** Um lembrete só pode ser enviado UMA vez.

**Implementação:**

```python
# apps/scheduler/tasks.py
@shared_task
def check_upcoming_reminders():
    now = timezone.now()

    events_to_remind = Event.objects.filter(
        reminder_enabled=True,
        start_time__gte=now,
        start_time__lte=now + timedelta(minutes=2)
    ).exclude(
        id__in=ReminderLog.objects.values_list('event_id', flat=True)
    )

    for event in events_to_remind:
        send_email_reminder(event)

        # Registra envio
        ReminderLog.objects.create(
            event=event,
            sent_at=now,
            recipient=event.planner.email
        )
```

**Status:** 📋 Planejado (V1.1 - criar model `ReminderLog`)

---

## 6. Regras Cross-Domain (Integrações)

### **BR-X01: Sincronização Contrato ↔ Orçamento**

**Regra:** O orçamento deve refletir em tempo real a saúde financeira através de dois indicadores baseados nos contratos e parcelas.

Total Comprometido: Soma de todos os total_amount de contratos com status SIGNED. Representa o que o noivo "prometeu" pagar.

Total Realizado (Pago): Soma de todas as Installment com status PAID. Representa o que já saiu do caixa.

**Cálculo Técnico (Referência):**

```python
# apps/finances/models/budget.py
class Budget(BaseModel):
    @property
    def total_committed(self):
        """Soma o valor de face dos contratos assinados (Logistics)"""
        from apps.logistics.models import Contract
        return Contract.objects.filter(
            wedding=self.wedding,
            status='SIGNED'
        ).aggregate(models.Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')

    @property
    def total_paid(self):
        """Soma as parcelas efetivamente pagas no financeiro (Finances)"""
        from apps.finances.models import Installment
        return Installment.objects.filter(
            expense__wedding=self.wedding,
            status='PAID'
        ).aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
```

**Status:** 🏗️ Definido (Aguardando implementação de Properties no Model ou Logic no Service)

---

### **BR-X02: Denormalização com Mixins (WeddingOwnedModel)**

**Regra:** Models que pertencem a um casamento DEVEM herdar `WeddingOwnedModel`.

**Implementação:**

```python
class WeddingOwnedModel(models.Model):
    wedding = models.ForeignKey('weddings.Wedding', on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()  # Validação automática
        super().save(*args, **kwargs)
```

**Aplicado em:**

- ✅ BudgetCategory (finances)
- ✅ Expense (finances)
- ✅ Installment (finances)
- ✅ Contract (logistics)
- ✅ Item (logistics)
- ✅ Event (scheduler)

**Benefícios:**

- ✅ Queries mais rápidas (sem JOINs complexos)
- ✅ Isolamento automático de dados
- ✅ Previne bugs de cross-wedding
- ✅ Validação consistente via `clean()`

**Status:** ✅ Implementado via `apps.core.models.WeddingOwnedModel`

---

### **BR-X03: Dashboard Consolidado**

**Regra:** O dashboard do casamento DEVE agregar dados de TODOS os domínios em uma única consulta otimizada.

**Performance:**

- ✅ Usa `select_related()` para ForeignKeys
- ✅ Usa `prefetch_related()` para ManyToMany
- ✅ Usa `annotate()` para agregações
- ✅ Cache de 5 minutos (opcional)

**Implementação:**

```python
# apps/weddings/services.py
class WeddingService:
    @staticmethod
    def get_dashboard(wedding_id):
        wedding = Wedding.objects.select_related('budget').prefetch_related(
            'contracts__supplier',
            'events',
            'budget__categories'
        ).get(id=wedding_id)

        return {
            'wedding_info': {...},
            'financial': FinancialService.get_summary(wedding),
            'logistics': LogisticsService.get_summary(wedding),
            'schedule': SchedulerService.get_summary(wedding),
        }
```

**Status:** 🏗️ Definido (Aguardando implementação da Service Layer)

---

## 7. Regras de Segurança e Auditoria

### **BR-SEC01: Multitenancy Rigoroso**

**Regra:** TODAS as queries DEVEM filtrar por `planner` ou `wedding`.

**Checklist:**

```python
# ✅ CORRETO
Wedding.objects.filter(planner=request.user)
Contract.objects.filter(wedding__planner=request.user)

# ❌ ERRADO (vazamento de dados!)
Wedding.objects.all()  # Vê casamentos de outros planners
```

**Status:** 🏗️ Definido (Aguardando implementação nas ViewSets)

---

### **BR-SEC02: Soft Delete Seletivo**

**Regra:** Soft delete APENAS em entidades que podem ser restauradas.

**Aplicado em:**

- ✅ Wedding (restaurável)
- ✅ BudgetCategory (restaurável)
- ✅ Supplier (restaurável)
- ✅ Contract (restaurável)
- ✅ Item (restaurável)

**NÃO aplicado em:**

- ❌ Budget (núcleo financeiro)
- ❌ Expense (histórico financeiro)
- ❌ Installment (histórico financeiro imutável)
- ❌ Event (histórico de agenda)

**Status:** ✅ Implementado via `SoftDeleteModel`

---

## 8. Regras de Validação de Dados

### **BR-VAL01: Decimal para Valores Monetários**

**Regra:** NUNCA usar `FloatField` para dinheiro. SEMPRE `DecimalField`.

**Motivo:** Float tem precisão binária limitada:

```python
# ❌ ERRADO
0.1 + 0.2  # = 0.30000000000000004

# ✅ CORRETO
Decimal('0.1') + Decimal('0.2')  # = Decimal('0.3')
```

**Padrão:**

```python
amount = models.DecimalField(max_digits=10, decimal_places=2)
```

**Status:** ✅ Implementado em TODOS os models financeiros

---

### **BR-VAL02: Datas no Futuro**

**Regra:** Vencimentos de parcelas e datas de eventos NÃO podem estar no passado (ao criar).

**Validação:**

```python
if self.due_date < timezone.now().date():
    raise ValidationError("Vencimento não pode estar no passado")
```

**Exceção:** Permitido ao editar (correção de dados históricos).

**Status:** 📋 Planejado (V1.1)

---

## 9. Regras Futuras (Roadmap V2.0)

### **BR-FUT01: Imutabilidade de Parcelas Pagas** 🚀

**Regra:** Parcelas com `status = PAID` não podem ter o valor alterado.

**Implementação Proposta:**

```python
class Installment(BaseModel):
    def clean(self):
        if self.pk and self.status == StatusChoices.PAID:
            old = Installment.objects.get(pk=self.pk)
            if old.amount != self.amount:
                raise ValidationError(
                    "Não é possível alterar valor de parcela já paga"
                )
```

**Motivo:** Auditoria e conciliação bancária.

**Status:** 📋 Planejado (V2.0)

---

### **BR-FUT02: Import de Excel (Mapper Dinâmico)** 🚀

**Regra:** Sistema deve aceitar upload de planilha com mapeamento flexível de colunas.

**Fluxo:**

1. Upload arquivo .xlsx
2. Sistema detecta colunas
3. Usuário mapeia: "Fornecedor" → `supplier`, "Valor" → `amount`
4. Preview em tabela de staging
5. Confirmação → batch insert

**Benefícios:**

- ✅ Onboarding rápido (migração de Excel)
- ✅ Reduz 80% do tempo de entrada de dados

**Complexidade:**

- ⚠️ 2-3 semanas de dev
- ⚠️ Muitos edge cases (datas, formatos, erros)

**Status:** 📋 Planejado (V1.1 - se 5+ clientes pedirem)

---

### **BR-FUT03: WhatsApp Ativo vs E-mail Passivo** 🚀

**Regra:** Alertas críticos (< 24h) via WhatsApp. Lembretes normais via e-mail.

**Critérios:**

- 🚨 WhatsApp: Pagamento vence AMANHÃ
- 📧 E-mail: Pagamento vence em 7 dias

**Custo:**

- E-mail: R$ 0/mês (Resend free tier)
- WhatsApp: R$ 300/mês + R$ 0,10/msg (Twilio)

**Status:** 📋 Planejado (V2.0 - se receita > R$ 5k/mês)

---

### **BR-FUT04: Contract como Âncora Financeira** 🚀

**Regra:** Contrato ASSINADO dispara criação/atualização automática de Expense.

**Implementação Proposta:**

```python
@receiver(post_save, sender=Contract)
def sync_expense(sender, instance, **kwargs):
    if instance.status == 'SIGNED':
        Expense.objects.update_or_create(
            contract=instance,
            defaults={'actual_amount': instance.total_amount}
        )
```

**Benefícios:**

- ✅ Sincronização automática finances ↔ logistics

**Trade-off:**

- ⚠️ "Mágica" dificulta debug
- ⚠️ Signals são implícitos

**Status:** 📋 Planejado (V2.0 - avaliar necessidade)

---

## 10. Glossário de Termos

| Termo               | Definição                                                                         |
| ------------------- | --------------------------------------------------------------------------------- |
| **Tolerância Zero** | Soma de parcelas = valor total (sem margem de erro)                               |
| **Âncora Jurídica** | Regra que vincula Expense ao Contract, impedindo alteração sem modificar contrato |
| **Cross-Wedding**   | Mistura acidental de dados entre casamentos diferentes                            |
| **Soft Delete**     | Deletar logicamente (flag `is_deleted=True`) sem remover do banco                 |
| **Hard Delete**     | Deletar fisicamente (SQL DELETE)                                                  |
| **Service Layer**   | Camada de lógica de negócio separada de Views                                     |
| **Denormalização**  | Duplicar dados para otimizar queries (vs normalização)                            |
| **Bounded Context** | Agrupamento lógico por domínio de negócio                                         |
| **OIDC**            | OpenID Connect - protocolo de autenticação service-to-service sem secrets         |
| **Presigned URL**   | URL temporária com permissão de upload gerada pelo backend                        |
| **OVERDUE**         | Status de parcela vencida (due_date < hoje e status = PENDING)                    |

---

## 11. Referências

- [REQUIREMENTS.md](REQUIREMENTS.md) - Requisitos Funcionais e Não-Funcionais
- [BUILD_ARCHITECTURE.md](BUILD_ARCHITECTURE.md) - Decisões Técnicas
- [FINANCIAL_INTEGRITY.md](../backend/apps/finances/FINANCIAL_INTEGRITY.md) - Regras Específicas de Finanças

---

**Última atualização:** 8 de janeiro de 2025
**Responsável:** Rafael
**Versão:** 2.0 - Consolidação de regras de negócio (BR-F02, BR-L05, BR-SEC03, BR-FUT05)
**Próxima revisão:** Sprint 4 (após 1 mês)

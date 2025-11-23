# App: Contracts

O app `contracts` gerencia contratos financeiros e jurídicos associados aos itens do casamento. Cada contrato é **criado automaticamente** quando um item é adicionado ao orçamento, estabelecendo uma relação OneToOne entre Item e Contract.

---

## Status Atual

**Versão:** 1.0  
**Testes:** 13 passando  
**Cobertura:** models (7 testes), views (6 testes)  
**Tipo:** Entity Management (CRUD parcial - visualização apenas)

---

## Responsabilidades

-   **Gestão de Contratos:** Armazenamento de contratos com fornecedores
-   **Relação 1:1 com Item:** Cada item tem exatamente um contrato
-   **Rastreamento de Status:** Pendente, Assinado, Finalizado, Cancelado
-   **Datas Importantes:** Data de assinatura e vencimento
-   **Validações:** Data de vencimento não pode ser anterior à assinatura
-   **Visualização:** Lista de contratos por casamento com gradientes visuais

---

## Arquitetura

### Padrões Aplicados
- **OneToOne Relationship:** Contrato vinculado a Item (cascade delete)
- **Property Delegation:** Acesso a `supplier` e `wedding` via item relacionado
- **Read-Only View:** Apenas visualização (CRUD completo planejado para v2.0)
- **Visual Feedback:** Gradientes coloridos para diferenciação de contratos
- **Security First:** Isolamento por planner (get_object_or_404)

### Filosofia
Contratos são **criados automaticamente** pelo app `items` quando um novo item é adicionado. O app `contracts` foca em **visualização e gestão**, não em criação direta.

---

## Estrutura de Arquivos

### Models (`models.py`)

-   **`Contract` (BaseModel):**
    - **Relação OneToOne:**
        - `item` (OneToOneField → Item) - Relação única, cascade delete
    - **Campos:**
        - `signature_date` (DateField, opcional) - Data de assinatura
        - `expiration_date` (DateField, opcional) - Data de vencimento
        - `description` (TextField) - Observações/detalhes
        - `status` (CharField, choices) - Status atual do contrato
        - `created_at`, `updated_at` (herdados de BaseModel)
    - **Choices de Status:**
        - `PENDING` - Pendente (default)
        - `SIGNED` - Assinado
        - `COMPLETED` - Finalizado
        - `CANCELED` - Cancelado
    - **Properties (delegadas ao Item):**
        - `supplier` - Retorna `self.item.supplier`
        - `wedding` - Retorna `self.item.wedding`
    - **Validações:**
        - `clean()` - Data de vencimento ≥ data de assinatura
    - **Meta:**
        - `verbose_name` - "Contrato"
        - `verbose_name_plural` - "Contratos"
    - **Métodos:**
        - `__str__()` - "Contrato: {item.name}"

### Views (`views.py`)

-   **`ContractsPartialView` (LoginRequiredMixin + TemplateView):**
    - **Template:** `contracts/contracts_partial.html`
    - **URL Parameter:** `wedding_id`
    - **Segurança:** 
        - `get_object_or_404(Wedding, id=wedding_id, planner=request.user)`
        - Garante isolamento de dados por planner
    - **Query Optimization:**
        - `select_related("item")` - Evita N+1 queries
        - Filtra contratos por `item__wedding`
    - **Visual Enhancement:**
        - Atribui gradiente de `GRADIENTS` a cada contrato
        - Rotaciona cores automaticamente (módulo do índice)
    - **Contexto:**
        - `wedding` - Objeto Wedding
        - `contracts_list` - Lista de dicts: `[{contract, gradient}, ...]`

### URLs (`urls.py`)

-   **Namespace:** `contracts`
-   **Rotas:**
    - `partial/<int:wedding_id>/` - ContractsPartialView (name: `partial_contracts`)

### Admin (`admin.py`)

-   **`ContractAdmin`:**
    - **List Display:** id, wedding, created_at, status
    - **Search Fields:** groom_name, bride_name (via wedding__)
    - **List Filter:** status
    - **Sugestão Futura:** Adicionar mais campos e actions

---

## Testes (`tests/`)

### `test_models.py` (7 testes)
- ✅ **test_contract_creation_and_str** - Criação básica e __str__
- ✅ **test_property_delegation** - Properties `supplier` e `wedding` funcionam
- ✅ **test_date_validation_logic** - Rejeita vencimento < assinatura
- ✅ **test_date_validation_success** - Aceita datas válidas
- ✅ **test_item_deletion_cascades_to_contract** - Cascade delete funciona
- ✅ **test_reverse_access_from_item** - `item.contract` acessível (related_name)
- ✅ **test_one_to_one_constraint** - Não permite 2 contratos para mesmo item

### `test_views.py` (6 testes)
- ✅ **test_anonymous_user_redirected** - Usuário não logado → 302
- ✅ **test_other_planner_cannot_access** - Outro planner → 404
- ✅ **test_view_renders_correct_template_and_context** - Template e contexto corretos
- ✅ **test_contracts_list_structure_and_gradients** - Estrutura de lista e gradientes
- ✅ **test_gradient_cycling** - Gradientes rotacionam se houver muitos contratos
- ✅ **test_view_handles_wedding_without_contracts** - Empty state funciona

**Total:** 13 testes passando ✅

---

## Fluxo de Dados: Criação de Contrato

```
[AddItemView (apps.items)]
    → Usuário cria novo Item
    → transaction.atomic():
        ├─ Item.objects.create(...)
        └─ Contract.objects.create(item=item, status="PENDING")
    → Sucesso: Item + Contract criados juntos
    → Falha: Rollback (nenhum é criado)
         ↓
[ContractsPartialView (apps.contracts)]
    → Busca contratos por item__wedding
    → Atribui gradiente visual
    → Renderiza lista de contratos
         ↓
[Template: contracts_partial.html]
    → Exibe cards de contratos com gradientes
    → Mostra status, fornecedor, datas
```

---

## Integração com Items

### Criação Automática (apps/items/views.py):
```python
from django.db import transaction

class AddItemView(...):
    def form_valid(self, form):
        with transaction.atomic():
            # 1. Cria o item
            item = form.save(commit=False)
            item.wedding = self.wedding
            item.save()
            
            # 2. Cria o contrato automaticamente
            Contract.objects.create(item=item, status="PENDING")
            
        return self.render_htmx_response(...)
```

### Acesso Reverso (apps/items/):
```python
# Em qualquer lugar que tenha um Item
item = Item.objects.get(pk=1)
contract = item.contract  # Acessa o contrato via related_name
```

---

## Segurança

- **Autenticação:** `LoginRequiredMixin` em todas as views
- **Autorização:** `get_object_or_404(Wedding, planner=request.user)`
- **Isolamento:** Planner só vê contratos de seus próprios casamentos
- **Validação:** Data de vencimento validada no model (clean())
- **Integridade:** OneToOneField garante 1 contrato por item

---

## Performance

- **Query Optimization:** `select_related("item")` evita N+1
- **Cascade Delete:** Banco de dados gerencia exclusão (não Python)
- **Indexing (futuro):** Considerar índice em `item_id` e `status`
- **Paginação (futuro):** Adicionar se houver muitos contratos por casamento

---

## Templates (`templates/contracts/`)

### Estrutura:
```
contracts/
└── contracts_partial.html    # Lista de contratos com gradientes
```

### Visualização:
- Cards de contratos com gradiente de fundo
- Informações: nome do item, fornecedor, status, datas
- Badge colorido por status (Pendente, Assinado, etc)
- Empty state se não houver contratos

---

## Validações

### Model-Level (`Contract.clean()`):
```python
if self.expiration_date < self.signature_date:
    raise ValidationError({
        "expiration_date": "A data de vencimento não pode ser anterior à data de assinatura."
    })
```

### OneToOne Constraint:
- Django garante via `IntegrityError` no banco
- Não é possível criar 2 contratos para o mesmo item
- Testado em `test_one_to_one_constraint`

---

## Melhorias Recentes (v1.0)

### Implementado:
1. ✅ Modelo `Contract` com OneToOne para Item
2. ✅ Properties delegadas (`supplier`, `wedding`)
3. ✅ Validação de datas (vencimento ≥ assinatura)
4. ✅ View de visualização com gradientes
5. ✅ Cascade delete automático
6. ✅ Admin básico configurado
7. ✅ 13 testes cobrindo model e view

---

## Melhorias Futuras (v2.0 - Planejado)

### CRUD Completo:
1. **Criar Contrato:**
   - Form para criar contrato manualmente (sem item)
   - Modal HTMX

2. **Editar Contrato:**
   - Update de status, datas, descrição
   - Modal HTMX

3. **Deletar Contrato:**
   - Confirmação antes de exclusão
   - Opção: deletar só contrato ou item + contrato

4. **Upload de Documentos:**
   - FileField para PDF/DOC do contrato
   - Assinatura digital (integração futura)

### Features Avançados:
1. **Notificações:**
   - Celery task para alertar contratos próximos ao vencimento
   - Email/notificação X dias antes
   - Já existe task stub em `apps.core.tasks`

2. **Status Workflow:**
   - Transições de estado validadas
   - Log de mudanças de status (audit trail)

3. **Relatórios:**
   - Exportar contratos em PDF
   - Dashboard de contratos por status

4. **API REST:**
   - Endpoints para CRUD de contratos
   - Serializers e ViewSets

---

## Dependências

### Apps Relacionados:
- **`apps.items`:** Relação OneToOne (item → contract)
- **`apps.weddings`:** Filtro e segurança (via item.wedding)
- **`apps.core.constants`:** `GRADIENTS` para visualização
- **`apps.core.models`:** Herança de `BaseModel`

### Models Utilizados:
- `Item` - Relação OneToOne (chave primária)
- `Wedding` - Filtro indireto via `item__wedding`

---

## Exemplos de Uso

### 1. Criar contrato automaticamente (via Item):
```python
# Em apps/items/views.py
from django.db import transaction
from apps.contracts.models import Contract

with transaction.atomic():
    item = Item.objects.create(wedding=wedding, name="Buffet", ...)
    contract = Contract.objects.create(item=item, status="PENDING")
```

### 2. Acessar contrato de um item:
```python
item = Item.objects.get(pk=1)
contract = item.contract  # Via related_name

print(contract.supplier)  # Acessa item.supplier via property
print(contract.wedding)   # Acessa item.wedding via property
```

### 3. Atualizar status do contrato:
```python
contract = Contract.objects.get(pk=1)
contract.status = "SIGNED"
contract.signature_date = timezone.now().date()
contract.save()
```

### 4. Validar datas antes de salvar:
```python
contract = Contract(item=item, signature_date=today, expiration_date=yesterday)

try:
    contract.full_clean()  # Dispara clean()
except ValidationError as e:
    print(e.message_dict)  # {'expiration_date': [...]}
```

### 5. Listar contratos de um casamento:
```python
wedding = Wedding.objects.get(pk=1)
contracts = Contract.objects.filter(item__wedding=wedding).select_related("item")

for contract in contracts:
    print(f"{contract.item.name} - {contract.status}")
```

---

## Comandos Úteis

### Executar testes:
```bash
# Via pytest (recomendado)
pytest apps/contracts/tests/ -v

# Teste específico
pytest apps/contracts/tests/test_models.py::ContractModelTest -v

# Via Django
python manage.py test apps.contracts
```

### Verificar contratos no shell:
```python
python manage.py shell

from apps.contracts.models import Contract

# Listar todos
Contract.objects.all()

# Por status
Contract.objects.filter(status="PENDING")

# Com item relacionado (otimizado)
Contract.objects.select_related("item__wedding").all()
```

### Criar contrato manualmente:
```python
from apps.items.models import Item
from apps.contracts.models import Contract

item = Item.objects.get(pk=1)
contract = Contract.objects.create(
    item=item,
    status="PENDING",
    description="Contrato de fotografia"
)
```

---

## Integrações

### Com Items:
- Criação automática via transaction.atomic()
- Cascade delete: Item deletado → Contract deletado
- Property delegation: contract.supplier, contract.wedding

### Com Weddings:
- Filtro: `item__wedding` para listar contratos por casamento
- Segurança: Validação de planner ownership

### Com Core:
- Herda `BaseModel` (created_at, updated_at)
- Usa `GRADIENTS` para visualização colorida
- Futuro: Celery tasks para notificações

---

## Estrutura de Status

| Status | Código | Descrição | Próxima Ação |
|--------|--------|-----------|--------------|
| **Pendente** | `PENDING` | Contrato aguardando assinatura | Assinar contrato |
| **Assinado** | `SIGNED` | Contrato assinado, em vigor | Acompanhar execução |
| **Finalizado** | `COMPLETED` | Serviço prestado, contrato encerrado | Arquivar |
| **Cancelado** | `CANCELED` | Contrato cancelado antes da conclusão | Buscar substituto |

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** 1.0 - Visualização e Validações (CRUD completo planejado para v2.0)

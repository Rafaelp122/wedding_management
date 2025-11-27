# App Contracts - Documentação Completa# App Contracts - Documentação Completa<<<<<<< HEAD



**Versão:** 2.0 (Sistema de Assinatura Digital Tripartite)  # App: Contracts

**Testes:** 61 passando ✅  

**Cobertura:** models, querysets, mixins, views  ## Status Atual



---O app `contracts` gerencia contratos financeiros e jurídicos associados aos itens do casamento. Cada contrato é **criado automaticamente** quando um item é adicionado ao orçamento, estabelecendo uma relação OneToOne entre Item e Contract.



## Visão Geral**Versão:** 2.0 (Assinatura Digital Tripartite)  



O app `contracts` gerencia contratos financeiros e jurídicos associados aos itens do casamento, implementando um sistema completo de **assinatura digital tripartite** (Cerimonialista → Fornecedor → Noivos).**Testes:** 61 passando ✅  ---



**Características principais:****Cobertura:** models, mixins, querysets, views  

- ✅ Relação OneToOne com Item (criação automática)

- ✅ Assinatura digital sequencial com validações**Tipo:** Sistema completo de gestão de contratos com assinatura digital## Status Atual

- ✅ Auditoria completa (IP + timestamp)

- ✅ Hash de integridade SHA256

- ✅ Geração de PDF com QR Code

- ✅ Arquitetura refatorada (QuerySets + Mixins)---**Versão:** 1.0  



---**Testes:** 13 passando  



## Estrutura do App## Estrutura do App**Cobertura:** models (7 testes), views (6 testes)  



```**Tipo:** Entity Management (CRUD parcial - visualização apenas)

contracts/

├── __init__.pyO app `contracts` foi reorganizado seguindo os princípios de **SOLID** e **DRY (Don't Repeat Yourself)**.

├── admin.py

├── apps.py---

├── constants.py       # Constantes (status, limites, formatos)

├── models.py          # Contract model com manager customizado```

├── querysets.py       # QuerySets personalizados para otimização

├── mixins.py          # Mixins reutilizáveis para viewscontracts/## Responsabilidades

├── views.py           # Views refatoradas usando mixins

├── urls.py├── __init__.py

├── migrations/

├── templates/├── admin.py-   **Gestão de Contratos:** Armazenamento de contratos com fornecedores

│   └── contracts/

│       ├── contracts_partial.html├── apps.py-   **Relação 1:1 com Item:** Cada item tem exatamente um contrato

│       ├── external_signature.html

│       ├── pdf_template.html├── models.py          # Modelo Contract com manager customizado e assinatura digital-   **Rastreamento de Status:** Pendente, Assinado, Finalizado, Cancelado

│       ├── signature_success.html

│       └── modals/├── querysets.py       # QuerySets personalizados para otimização-   **Datas Importantes:** Data de assinatura e vencimento

│           ├── edit_contract_modal.html

│           ├── signature_modal.html├── mixins.py          # Mixins reutilizáveis para views-   **Validações:** Data de vencimento não pode ser anterior à assinatura

│           └── upload_contract_modal.html

└── tests/├── views.py           # Views refatoradas usando mixins-   **Visualização:** Lista de contratos por casamento com gradientes visuais

    ├── test_models.py      # 25 testes

    ├── test_querysets.py   # Testes de queryset customizado├── urls.py

    ├── test_mixins.py      # 18 testes

    └── test_views.py       # 18 testes├── migrations/---

```

├── templates/

---

│   └── contracts/## Arquitetura

## Funcionalidades

│       ├── contracts_partial.html

### 1. Assinatura Digital Tripartite

│       ├── external_signature.html### Padrões Aplicados

**Fluxo Sequencial:**

```│       ├── pdf_template.html- **OneToOne Relationship:** Contrato vinculado a Item (cascade delete)

[Planner cria contrato]

    ↓│       ├── signature_success.html- **Property Delegation:** Acesso a `supplier` e `wedding` via item relacionado

[Status: WAITING_PLANNER]

    → Planner assina (via dashboard)│       └── modals/- **Read-Only View:** Apenas visualização (CRUD completo planejado para v2.0)

    ↓

[Status: WAITING_SUPPLIER]│           ├── edit_contract_modal.html- **Visual Feedback:** Gradientes coloridos para diferenciação de contratos

    → Link enviado para fornecedor

    → Fornecedor assina via link público│           ├── signature_modal.html- **Security First:** Isolamento por planner (get_object_or_404)

    ↓

[Status: WAITING_COUPLE]│           └── upload_contract_modal.html

    → Link enviado para noivos

    → Noivos assinam via link público└── tests/### Filosofia

    ↓

[Status: COMPLETED]    ├── test_models.pyContratos são **criados automaticamente** pelo app `items` quando um novo item é adicionado. O app `contracts` foca em **visualização e gestão**, não em criação direta.

    → Hash de integridade gerado (SHA256)

    → PDF final disponível para download    ├── test_mixins.py

```

    └── test_views.py---

**Validações:**

- ✅ Formato: PNG, JPG, JPEG apenas```

- ✅ Tamanho máximo: 500KB

- ✅ Base64 válido## Estrutura de Arquivos

- ✅ Status correto para assinatura

- ✅ Sequência respeitada---



**Auditoria:**### Models (`models.py`)

- IP do assinante

- Timestamp preciso## Funcionalidades Principais

- Hash de integridade final

-   **`Contract` (BaseModel):**

### 2. Gestão de Contratos

### 1. Assinatura Digital Tripartite    - **Relação OneToOne:**

- **Upload de contrato externo**: PDF assinado offline

- **Edição de termos**: Apenas em DRAFT/WAITING_PLANNER- **Fluxo**: Planner → Fornecedor → Noivos        - `item` (OneToOneField → Item) - Relação única, cascade delete

- **Cancelamento**: Invalida link de assinatura

- **Download de PDF**: Com QR Code embutido- **Validações**: Formato (PNG/JPG/JPEG), tamanho (máx 500KB), base64    - **Campos:**



### 3. Notificações- **Auditoria**: IP e timestamp de cada assinatura        - `signature_date` (DateField, opcional) - Data de assinatura



- Envio de e-mail com link único- **Integridade**: Hash SHA256 após conclusão        - `expiration_date` (DateField, opcional) - Data de vencimento

- Token UUID seguro

- Links de assinatura temporários        - `description` (TextField) - Observações/detalhes



---### 2. Gestão de Contratos        - `status` (CharField, choices) - Status atual do contrato



## Arquitetura (Refatorada)- Upload de contrato externo (PDF)        - `created_at`, `updated_at` (herdados de BaseModel)



### 1. QuerySets Personalizados (`querysets.py`)- Edição de termos/minuta    - **Choices de Status:**



**Métodos disponíveis:**- Cancelamento de contratos        - `PENDING` - Pendente (default)



```python- Download de PDF com QR Code        - `SIGNED` - Assinado

Contract.objects

  .for_planner(planner)      # Filtra por cerimonialista        - `COMPLETED` - Finalizado

  .for_wedding(wedding)       # Filtra por casamento

  .with_related()             # Otimiza queries (select_related)### 3. Notificações        - `CANCELED` - Cancelado

  .pending_signature()        # Aguardando assinatura

  .completed()                # Completos- Envio de e-mail com link de assinatura    - **Properties (delegadas ao Item):**

  .canceled()                 # Cancelados

  .by_status(status)          # Por status específico- Link único e seguro via UUID token        - `supplier` - Retorna `self.item.supplier`

  .search(query)              # Busca textual

  .fully_signed()             # Com todas as assinaturas        - `wedding` - Retorna `self.item.wedding`

  .editable()                 # Podem ser editados

  .cancelable()               # Podem ser cancelados---    - **Validações:**

  .bulk_cancel()              # Cancela múltiplos

  .bulk_update_description()  # Atualiza múltiplos        - `clean()` - Data de vencimento ≥ data de assinatura

```

## Arquitetura    - **Meta:**

**Exemplo de uso:**

```python        - `verbose_name` - "Contrato"

# Buscar contratos pendentes de um casamento específico

contracts = (### 1. QuerySets Personalizados (`querysets.py`)        - `verbose_name_plural` - "Contratos"

    Contract.objects

    .for_wedding(wedding)    - **Métodos:**

    .pending_signature()

    .with_related()#### `ContractQuerySet`        - `__str__()` - "Contrato: {item.name}"

)

```



### 2. Mixins Reutilizáveis (`mixins.py`)Métodos disponíveis:### Views (`views.py`)



**Mixins Independentes:**

- `ContractOwnershipMixin`: Garante ownership (planner)

- `ContractQuerysetMixin`: Lógica de construção de querysets- **`for_planner(planner)`**: Filtra contratos de um cerimonialista-   **`ContractsPartialView` (LoginRequiredMixin + TemplateView):**

- `ContractSignatureMixin`: Processamento de assinaturas

- `ContractUrlGeneratorMixin`: Geração de URLs e links- **`for_wedding(wedding)`**: Filtra contratos de um casamento    - **Template:** `contracts/contracts_partial.html`

- `ContractEmailMixin`: Envio de e-mails

- `ContractActionsMixin`: Ações (cancelar, editar, upload)- **`with_related()`**: Otimiza queries com select_related    - **URL Parameter:** `wedding_id`



**Mixin Facade:**- **`pending_signature()`**: Filtra contratos aguardando assinatura    - **Segurança:** 

- `ContractManagementMixin`: Agrupa todos os mixins acima

- **`completed()`**: Filtra contratos completos        - `get_object_or_404(Wedding, id=wedding_id, planner=request.user)`

**Exemplo de uso:**

```python- **`canceled()`**: Filtra contratos cancelados        - Garante isolamento de dados por planner

class MyContractView(

    ContractOwnershipMixin,- **`by_status(status)`**: Filtra por status específico    - **Query Optimization:**

    ContractManagementMixin,

    View- **`search(query)`**: Busca por nome do item, descrição ou fornecedor        - `select_related("item")` - Evita N+1 queries

):

    def post(self, request, contract_id):- **`with_priority_annotation()`**: Anota prioridade baseada em status e data        - Filtra contratos por `item__wedding`

        contract = self.get_queryset().get(id=contract_id)

        success, message = self.cancel_contract(contract)- **`order_by_priority()`**: Ordena por prioridade e data    - **Visual Enhancement:**

        

        if success:- **`fully_signed()`**: Filtra contratos com todas as assinaturas        - Atribui gradiente de `GRADIENTS` a cada contrato

            return self.json_success(message)

        return self.json_error(message)- **`editable()`**: Filtra contratos que podem ser editados        - Rotaciona cores automaticamente (módulo do índice)

```

    - **Contexto:**

### 3. Models (`models.py`)

**Exemplo de uso:**        - `wedding` - Objeto Wedding

**Campos principais:**

```python        - `contracts_list` - Lista de dicts: `[{contract, gradient}, ...]`

class Contract(BaseModel):

    item = OneToOneField(Item)```python

    description = TextField()

    status = CharField(choices=STATUS_CHOICES)# Buscar contratos pendentes de um casamento específico### URLs (`urls.py`)

    token = UUIDField(default=uuid.uuid4)

    contracts = (

    # Assinaturas - Planner

    planner_signature = FileField()    Contract.objects-   **Namespace:** `contracts`

    planner_signed_at = DateTimeField()

    planner_ip = GenericIPAddressField()    .for_wedding(wedding)-   **Rotas:**

    

    # Assinaturas - Fornecedor    .pending_signature()    - `partial/<int:wedding_id>/` - ContractsPartialView (name: `partial_contracts`)

    supplier_signature = FileField()

    supplier_signed_at = DateTimeField()    .order_by_priority()

    supplier_ip = GenericIPAddressField()

    )### Admin (`admin.py`)

    # Assinaturas - Noivos

    couple_signature = FileField()

    couple_signed_at = DateTimeField()

    couple_ip = GenericIPAddressField()# Buscar contratos completos do cerimonialista-   **`ContractAdmin`:**

    

    # Integridadecompleted = (    - **List Display:** id, wedding, created_at, status

    integrity_hash = CharField(max_length=64)  # SHA256

        Contract.objects    - **Search Fields:** groom_name, bride_name (via wedding__)

    # Arquivos

    external_pdf = FileField()    .for_planner(request.user)    - **List Filter:** status

```

    .completed()    - **Sugestão Futura:** Adicionar mais campos e actions

**Métodos principais:**

- `process_signature(signature_b64, client_ip)`: Processa assinatura    .with_related()

- `get_next_signer_info()`: Info do próximo assinante

- `is_fully_signed()`: Verifica conclusão)---

- `get_signatures_status()`: Status de todas as assinaturas

- `_generate_integrity_hash()`: Gera hash SHA256```



**Properties delegadas:**## Testes (`tests/`)

- `supplier` → `self.item.supplier`

- `wedding` → `self.item.wedding`### 2. Mixins Reutilizáveis (`mixins.py`)

- `contract_value` → `self.item.total_price`

### `test_models.py` (7 testes)

### 4. Views (`views.py`)

Mixins granulares que seguem o **Princípio da Responsabilidade Única (SRP)**:- ✅ **test_contract_creation_and_str** - Criação básica e __str__

**Class-Based Views:**

- `ContractsPartialView`: Lista contratos de um casamento- ✅ **test_property_delegation** - Properties `supplier` e `wedding` funcionam

- `GenerateSignatureLinkView`: Gera link + envia e-mail

- `SignContractExternalView`: Página pública de assinatura#### Mixins Independentes (Standalone)- ✅ **test_date_validation_logic** - Rejeita vencimento < assinatura

- `CancelContractView`: Cancela contrato

- `EditContractView`: Edita descrição- ✅ **test_date_validation_success** - Aceita datas válidas

- `UploadContractView`: Upload de PDF externo

- **`ClientIPMixin`**: Extração de IP do cliente- ✅ **test_item_deletion_cascades_to_contract** - Cascade delete funciona

**Function-Based Views:**

- `download_contract_pdf()`: Download do PDF com QR Code- **`ContractOwnershipMixin`**: Garante ownership através do planner- ✅ **test_reverse_access_from_item** - `item.contract` acessível (related_name)

- `link_callback()`: Callback para recursos estáticos (xhtml2pdf)

- **`TokenAccessMixin`**: Acesso por token UUID- ✅ **test_one_to_one_constraint** - Não permite 2 contratos para mesmo item

---

- **`PDFResponseMixin`**: Geração de PDFs

## Testes (61 passando ✅)

- **`ContractQuerysetMixin`**: Lógica de construção de querysets### `test_views.py` (6 testes)

### Models (25 testes)

- ✅ CRUD básico (5 testes)- **`ContractSignatureMixin`**: Lógica de processamento de assinaturas- ✅ **test_anonymous_user_redirected** - Usuário não logado → 302

- ✅ Processamento de assinaturas (8 testes)

- ✅ Métodos de status (5 testes)- **`ContractUrlGeneratorMixin`**: Geração de URLs e links- ✅ **test_other_planner_cannot_access** - Outro planner → 404

- ✅ Hash de integridade (2 testes)

- ✅ Informações do próximo assinante (5 testes)- **`ContractEmailMixin`**: Envio de e-mails- ✅ **test_view_renders_correct_template_and_context** - Template e contexto corretos



### Mixins (18 testes)- **`ContractActionsMixin`**: Ações em contratos (cancelar, editar, upload)- ✅ **test_contracts_list_structure_and_gradients** - Estrutura de lista e gradientes

- ✅ ContractOwnershipMixin (4 testes)

- ✅ ContractSignatureMixin (5 testes)- **`JsonResponseMixin`**: Helpers para respostas JSON- ✅ **test_gradient_cycling** - Gradientes rotacionam se houver muitos contratos

- ✅ ContractEmailMixin (3 testes)

- ✅ ContractActionsMixin (6 testes)- ✅ **test_view_handles_wedding_without_contracts** - Empty state funciona



### Views (18 testes)#### Mixin de Composição (Facade)

- ✅ ContractsPartialView (6 testes)

- ✅ GenerateSignatureLinkView (4 testes)**Total:** 13 testes passando ✅

- ✅ SignContractExternalView (5 testes)

- ✅ DownloadContractPDFView (3 testes)- **`ContractManagementMixin`**: Agrupa todos os mixins acima em uma interface única



------



## Segurança**Exemplo de uso:**



- **Autenticação**: `LoginRequiredMixin` em views protegidas## Fluxo de Dados: Criação de Contrato

- **Autorização**: Verificação de ownership (planner do casamento)

- **Acesso Público**: Apenas para assinatura via token UUID único```python

- **Validações**:

  - Formato de imagem (PNG, JPG, JPEG)class MyContractView(```

  - Tamanho máximo (500KB)

  - Base64 válido    LoginRequiredMixin,[AddItemView (apps.items)]

- **Auditoria**: IP e timestamp de cada assinatura

- **Integridade**: Hash SHA256 após todas as assinaturas    ContractOwnershipMixin,    → Usuário cria novo Item



---    ContractManagementMixin,    → transaction.atomic():



## Performance    View        ├─ Item.objects.create(...)



- **Query Optimization**: `select_related("item")` evita N+1):        └─ Contract.objects.create(item=item, status="PENDING")

- **Cascade Delete**: Gerenciado pelo banco de dados

- **Queries Otimizadas**: QuerySets customizados com anotações    def post(self, request, contract_id):    → Sucesso: Item + Contract criados juntos

- **PDF Generation**: Cache de QR Code

        contract = get_object_or_404(Contract, id=contract_id)    → Falha: Rollback (nenhum é criado)

---

        success, message = self.cancel_contract(contract)         ↓

## Exemplos de Uso

        [ContractsPartialView (apps.contracts)]

### 1. Processar assinatura:

```python        if success:    → Busca contratos por item__wedding

contract = Contract.objects.get(token=token)

try:            return self.json_success(message)    → Atribui gradiente visual

    contract.process_signature(

        signature_b64="data:image/png;base64,iVBORw0KG...",        return self.json_error(message)    → Renderiza lista de contratos

        client_ip="192.168.1.1"

    )```         ↓

except ValueError as e:

    print(f"Erro: {e}")[Template: contracts_partial.html]

```

### 3. Models (`models.py`)    → Exibe cards de contratos com gradientes

### 2. Verificar status de assinaturas:

```python    → Mostra status, fornecedor, datas

contract = Contract.objects.get(pk=1)

status = contract.get_signatures_status()#### Campos de Assinatura Digital```

# {

#     'planner': {'signed': True, 'signed_at': datetime, 'ip': '...'},

#     'supplier': {'signed': True, 'signed_at': datetime, 'ip': '...'},

#     'couple': {'signed': False, 'signed_at': None, 'ip': None}```python---

# }

```class Contract(BaseModel):



### 3. Buscar contratos pendentes:    # Relação## Integração com Items

```python

# Todos os contratos aguardando assinatura    item = models.OneToOneField(Item, on_delete=models.CASCADE)

pending = Contract.objects.pending_signature()

    ### Criação Automática (apps/items/views.py):

# Contratos completos de um casamento

completed = (    # Campos de contrato```python

    Contract.objects

    .for_wedding(wedding)    description = models.TextField(blank=True)from django.db import transaction

    .completed()

    .with_related()    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

)

```    token = models.UUIDField(default=uuid.uuid4, unique=True)class AddItemView(...):



---        def form_valid(self, form):



## Comandos Úteis    # Assinaturas - Planner        with transaction.atomic():



### Executar testes:    planner_signature = models.FileField(upload_to="signatures/planner/")            # 1. Cria o item

```bash

# Todos os testes    planner_signed_at = models.DateTimeField(null=True)            item = form.save(commit=False)

python manage.py test apps.contracts

    planner_ip = models.GenericIPAddressField(null=True)            item.wedding = self.wedding

# Com verbosidade

python manage.py test apps.contracts -v 2                item.save()



# Apenas um teste específico    # Assinaturas - Fornecedor            

python manage.py test apps.contracts.tests.test_models.ContractSignatureProcessingTest

```    supplier_signature = models.FileField(upload_to="signatures/supplier/")            # 2. Cria o contrato automaticamente



### Verificar contratos no shell:    supplier_signed_at = models.DateTimeField(null=True)            Contract.objects.create(item=item, status="PENDING")

```python

from apps.contracts.models import Contract    supplier_ip = models.GenericIPAddressField(null=True)            



# Listar contratos pendentes            return self.render_htmx_response(...)

Contract.objects.pending_signature()

    # Assinaturas - Noivos```

# Contratos completamente assinados

Contract.objects.fully_signed()    couple_signature = models.FileField(upload_to="signatures/couple/")



# Buscar por casamento    couple_signed_at = models.DateTimeField(null=True)### Acesso Reverso (apps/items/):

Contract.objects.for_wedding(wedding).with_related()

```    couple_ip = models.GenericIPAddressField(null=True)```python



---    # Em qualquer lugar que tenha um Item



## Integração com Outros Apps    # Arquivositem = Item.objects.get(pk=1)



### Com Items:    integrity_hash = models.CharField(max_length=64)contract = item.contract  # Acessa o contrato via related_name

- Criação automática via `transaction.atomic()`

- Cascade delete: Item deletado → Contract deletado    final_pdf = models.FileField(upload_to="contracts_pdf/")```

- Property delegation: `contract.supplier`, `contract.wedding`

    external_pdf = models.FileField(upload_to="contracts_external/")

### Com Weddings:

- Filtro: `item__wedding` para listar contratos por casamento```---

- Segurança: Validação de planner ownership



### Com Core:

- Herda `BaseModel` (created_at, updated_at)#### Status do Contrato## Segurança

- Usa `GRADIENTS` para visualização colorida



---

- **`DRAFT`**: Rascunho- **Autenticação:** `LoginRequiredMixin` em todas as views

## Benefícios da Arquitetura

- **`WAITING_PLANNER`**: Aguardando Cerimonialista- **Autorização:** `get_object_or_404(Wedding, planner=request.user)`

### 1. Reutilização de Código (DRY)

- Lógica comum extraída para mixins- **`WAITING_SUPPLIER`**: Aguardando Fornecedor- **Isolamento:** Planner só vê contratos de seus próprios casamentos

- QuerySets reutilizáveis entre views

- Redução de duplicação de código- **`WAITING_COUPLE`**: Aguardando Noivos- **Validação:** Data de vencimento validada no model (clean())



### 2. Manutenibilidade- **`COMPLETED`**: Concluído- **Integridade:** OneToOneField garante 1 contrato por item

- Código organizado por responsabilidade

- Fácil localização de funcionalidades- **`CANCELED`**: Cancelado

- Alterações isoladas sem efeitos colaterais

---

### 3. Testabilidade

- Mixins testados individualmente#### Métodos Principais

- QuerySets testáveis isoladamente

- 61 testes cobrindo toda funcionalidade## Performance



### 4. Legibilidade- **`process_signature(signature_b64, client_ip)`**: Processa assinatura com validações

- Views limpas e focadas

- Nomenclatura clara e consistente- **`get_next_signer_info()`**: Retorna info do próximo signatário- **Query Optimization:** `select_related("item")` evita N+1

- Documentação inline

- **`is_fully_signed()`**: Verifica se todas as partes assinaram- **Cascade Delete:** Banco de dados gerencia exclusão (não Python)

### 5. Performance

- Queries otimizadas com select_related- **`get_signatures_status()`**: Retorna status de todas as assinaturas- **Indexing (futuro):** Considerar índice em `item_id` e `status`

- Anotações eficientes

- Prevenção de N+1 queries- **`_generate_integrity_hash()`**: Gera hash SHA256 após conclusão- **Paginação (futuro):** Adicionar se houver muitos contratos por casamento



---



## Padrões de Design### 4. Views (`views.py`)---



### 1. Facade Pattern

`ContractManagementMixin` simplifica acesso a múltiplos mixins

#### Class-Based Views## Templates (`templates/contracts/`)

### 2. Mixin Pattern

Composição de funcionalidades através de herança múltipla



### 3. Manager Pattern- **`ContractsPartialView`**: Lista contratos de um casamento### Estrutura:

QuerySets customizados conectados ao modelo

- **`GenerateSignatureLinkView`**: Gera link e envia e-mail```

### 4. Strategy Pattern

Diferentes estratégias de filtragem e ordenação- **`SignContractExternalView`**: Assinatura externa (pública)contracts/



---- **`CancelContractView`**: Cancela contrato└── contracts_partial.html    # Lista de contratos com gradientes



## Referências- **`EditContractView`**: Edita descrição do contrato```



- [Django QuerySets](https://docs.djangoproject.com/en/stable/ref/models/querysets/)- **`UploadContractView`**: Upload de contrato externo

- [Django Mixins](https://docs.djangoproject.com/en/stable/topics/class-based-views/mixins/)

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)### Visualização:

- [xhtml2pdf Documentation](https://xhtml2pdf.readthedocs.io/)

- [QR Code Library](https://github.com/lincolnloop/python-qrcode)#### Function-Based Views- Cards de contratos com gradiente de fundo



---- Informações: nome do item, fornecedor, status, datas



**Última Atualização:** 26 de novembro de 2025  - **`download_contract_pdf(request, contract_id)`**: Download do PDF com QR Code- Badge colorido por status (Pendente, Assinado, etc)

**Versão:** 2.0 - Sistema Completo de Assinatura Digital Tripartite

- **`link_callback(uri, rel)`**: Callback para recursos estáticos no PDF- Empty state se não houver contratos



------



## Testes (61 passando ✅)## Validações



### Mixins (18 testes)### Model-Level (`Contract.clean()`):

- ✅ ClientIPMixin (4 testes)```python

- ✅ ContractOwnershipMixin (4 testes)if self.expiration_date < self.signature_date:

- ✅ PDFResponseMixin (5 testes)    raise ValidationError({

- ✅ TokenAccessMixin (2 testes)        "expiration_date": "A data de vencimento não pode ser anterior à data de assinatura."

    })

### Models (25 testes)```

- ✅ Contract CRUD básico (5 testes)

- ✅ Processamento de assinaturas (8 testes)### OneToOne Constraint:

- ✅ Métodos de status (5 testes)- Django garante via `IntegrityError` no banco

- ✅ Hash de integridade (2 testes)- Não é possível criar 2 contratos para o mesmo item

- ✅ Informações do próximo assinante (5 testes)- Testado em `test_one_to_one_constraint`



### Views (18 testes)---

- ✅ ContractsPartialView (6 testes)

- ✅ GenerateSignatureLinkView (4 testes)## Melhorias Recentes (v1.0)

- ✅ SignContractExternalView (5 testes)

- ✅ DownloadContractPDFView (3 testes)### Implementado:

1. ✅ Modelo `Contract` com OneToOne para Item

---2. ✅ Properties delegadas (`supplier`, `wedding`)

3. ✅ Validação de datas (vencimento ≥ assinatura)

## Fluxo de Assinatura Digital4. ✅ View de visualização com gradientes

5. ✅ Cascade delete automático

```6. ✅ Admin básico configurado

[Planner cria contrato]7. ✅ 13 testes cobrindo model e view

    ↓

[Status: WAITING_PLANNER]---

    → Planner assina

    ↓## Melhorias Futuras (v2.0 - Planejado)

[Status: WAITING_SUPPLIER]

    → Link enviado para fornecedor### CRUD Completo:

    → Fornecedor assina via link público1. **Criar Contrato:**

    ↓   - Form para criar contrato manualmente (sem item)

[Status: WAITING_COUPLE]   - Modal HTMX

    → Link enviado para noivos

    → Noivos assinam via link público2. **Editar Contrato:**

    ↓   - Update de status, datas, descrição

[Status: COMPLETED]   - Modal HTMX

    → Hash de integridade gerado

    → PDF final disponível para download3. **Deletar Contrato:**

```   - Confirmação antes de exclusão

   - Opção: deletar só contrato ou item + contrato

---

4. **Upload de Documentos:**

## Segurança   - FileField para PDF/DOC do contrato

   - Assinatura digital (integração futura)

- **Autenticação**: `LoginRequiredMixin` em views protegidas

- **Autorização**: Verificação de ownership (planner do casamento)### Features Avançados:

- **Acesso Público**: Apenas para assinatura via token UUID único1. **Notificações:**

- **Validações**:   - Celery task para alertar contratos próximos ao vencimento

  - Formato de imagem (PNG, JPG, JPEG)   - Email/notificação X dias antes

  - Tamanho máximo (500KB)   - Já existe task stub em `apps.core.tasks`

  - Base64 válido

- **Auditoria**: IP e timestamp de cada assinatura2. **Status Workflow:**

- **Integridade**: Hash SHA256 após todas as assinaturas   - Transições de estado validadas

   - Log de mudanças de status (audit trail)

---

3. **Relatórios:**

## Performance   - Exportar contratos em PDF

   - Dashboard de contratos por status

- **Query Optimization**: `select_related("item")` evita N+1

- **Cascade Delete**: Gerenciado pelo banco de dados4. **API REST:**

- **Queries Otimizadas**: QuerySets customizados com anotações   - Endpoints para CRUD de contratos

- **PDF Generation**: Cache de QR Code   - Serializers e ViewSets



------



## Exemplos de Uso## Dependências



### 1. Processar assinatura:### Apps Relacionados:

```python- **`apps.items`:** Relação OneToOne (item → contract)

contract = Contract.objects.get(token=token)- **`apps.weddings`:** Filtro e segurança (via item.wedding)

try:- **`apps.core.constants`:** `GRADIENTS` para visualização

    contract.process_signature(- **`apps.core.models`:** Herança de `BaseModel`

        signature_b64="data:image/png;base64,iVBORw0KG...",

        client_ip="192.168.1.1"### Models Utilizados:

    )- `Item` - Relação OneToOne (chave primária)

except ValueError as e:- `Wedding` - Filtro indireto via `item__wedding`

    print(f"Erro: {e}")

```---



### 2. Verificar status de assinaturas:## Exemplos de Uso

```python

contract = Contract.objects.get(pk=1)### 1. Criar contrato automaticamente (via Item):

status = contract.get_signatures_status()```python

# {# Em apps/items/views.py

#     'planner': {'signed': True, 'signed_at': datetime, 'ip': '...'},from django.db import transaction

#     'supplier': {'signed': True, 'signed_at': datetime, 'ip': '...'},from apps.contracts.models import Contract

#     'couple': {'signed': False, 'signed_at': None, 'ip': None}

# }with transaction.atomic():

```    item = Item.objects.create(wedding=wedding, name="Buffet", ...)

    contract = Contract.objects.create(item=item, status="PENDING")

### 3. Gerar link de assinatura:```

```python

contract = Contract.objects.get(pk=1)### 2. Acessar contrato de um item:

link = request.build_absolute_uri(contract.get_absolute_url())```python

# https://example.com/contratos/sign/uuid-token/item = Item.objects.get(pk=1)

```contract = item.contract  # Via related_name



---print(contract.supplier)  # Acessa item.supplier via property

print(contract.wedding)   # Acessa item.wedding via property

## Comandos Úteis```



### Executar testes:### 3. Atualizar status do contrato:

```bash```python

# Todos os testescontract = Contract.objects.get(pk=1)

python manage.py test apps.contractscontract.status = "SIGNED"

contract.signature_date = timezone.now().date()

# Com verbosidadecontract.save()

python manage.py test apps.contracts -v 2```



# Apenas um teste específico### 4. Validar datas antes de salvar:

python manage.py test apps.contracts.tests.test_models.ContractSignatureProcessingTest```python

```contract = Contract(item=item, signature_date=today, expiration_date=yesterday)



### Verificar contratos no shell:try:

```python    contract.full_clean()  # Dispara clean()

from apps.contracts.models import Contractexcept ValidationError as e:

    print(e.message_dict)  # {'expiration_date': [...]}

# Listar contratos pendentes```

Contract.objects.pending_signature()

### 5. Listar contratos de um casamento:

# Contratos completamente assinados```python

Contract.objects.fully_signed()wedding = Wedding.objects.get(pk=1)

contracts = Contract.objects.filter(item__wedding=wedding).select_related("item")

# Buscar por casamento

Contract.objects.for_wedding(wedding).with_related()for contract in contracts:

```    print(f"{contract.item.name} - {contract.status}")

```

---

---

## Benefícios da Arquitetura

## Comandos Úteis

### 1. Reutilização de Código (DRY)

- Lógica comum extraída para mixins### Executar testes:

- QuerySets reutilizáveis entre views```bash

- Redução de duplicação de código# Via pytest (recomendado)

pytest apps/contracts/tests/ -v

### 2. Manutenibilidade

- Código organizado por responsabilidade# Teste específico

- Fácil localização de funcionalidadespytest apps/contracts/tests/test_models.py::ContractModelTest -v

- Alterações isoladas sem efeitos colaterais

# Via Django

### 3. Testabilidadepython manage.py test apps.contracts

- Mixins testados individualmente```

- QuerySets testáveis isoladamente

- 61 testes cobrindo toda funcionalidade### Verificar contratos no shell:

```python

### 4. Legibilidadepython manage.py shell

- Views limpas e focadas

- Nomenclatura clara e consistentefrom apps.contracts.models import Contract

- Documentação inline

# Listar todos

### 5. PerformanceContract.objects.all()

- Queries otimizadas com select_related

- Anotações eficientes# Por status

- Prevenção de N+1 queriesContract.objects.filter(status="PENDING")



---# Com item relacionado (otimizado)

Contract.objects.select_related("item__wedding").all()

## Padrões de Design```



### 1. **Facade Pattern**### Criar contrato manualmente:

`ContractManagementMixin` simplifica acesso a múltiplos mixins```python

from apps.items.models import Item

### 2. **Mixin Pattern**from apps.contracts.models import Contract

Composição de funcionalidades através de herança múltipla

item = Item.objects.get(pk=1)

### 3. **Manager Pattern**contract = Contract.objects.create(

QuerySets customizados conectados ao modelo    item=item,

    status="PENDING",

### 4. **Strategy Pattern**    description="Contrato de fotografia"

Diferentes estratégias de filtragem e ordenação)

```

---

---

## Referências

## Integrações

- [Django QuerySets](https://docs.djangoproject.com/en/stable/ref/models/querysets/)

- [Django Mixins](https://docs.djangoproject.com/en/stable/topics/class-based-views/mixins/)### Com Items:

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)- Criação automática via transaction.atomic()

- Cascade delete: Item deletado → Contract deletado

---- Property delegation: contract.supplier, contract.wedding



**Última Atualização:** 26 de novembro de 2025  ### Com Weddings:

**Versão:** 2.0 - Sistema Completo de Assinatura Digital Tripartite- Filtro: `item__wedding` para listar contratos por casamento

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
=======
# App Contracts - Documentação

## Estrutura do App

O app `contracts` foi reorganizado seguindo o mesmo padrão do app `weddings`, utilizando os princípios de **SOLID** e **DRY (Don't Repeat Yourself)**.

```
contracts/
├── __init__.py
├── admin.py
├── apps.py
├── models.py          # Modelo Contract com manager customizado
├── querysets.py       # QuerySets personalizados para otimização
├── mixins.py          # Mixins reutilizáveis para views
├── views.py           # Views refatoradas usando mixins
├── urls.py
├── migrations/
├── templates/
└── tests/
```

## Arquitetura

### 1. QuerySets Personalizados (`querysets.py`)

QuerySets customizados que encapsulam lógicas de filtragem e anotação:

#### `ContractQuerySet`

Métodos disponíveis:

- **`for_planner(planner)`**: Filtra contratos de um cerimonialista
- **`for_wedding(wedding)`**: Filtra contratos de um casamento
- **`with_related()`**: Otimiza queries com select_related
- **`pending_signature()`**: Filtra contratos aguardando assinatura
- **`completed()`**: Filtra contratos completos
- **`canceled()`**: Filtra contratos cancelados
- **`by_status(status)`**: Filtra por status específico
- **`search(query)`**: Busca por nome do item, descrição ou fornecedor
- **`with_priority_annotation()`**: Anota prioridade baseada em status e data
- **`order_by_priority()`**: Ordena por prioridade e data
- **`fully_signed()`**: Filtra contratos com todas as assinaturas
- **`editable()`**: Filtra contratos que podem ser editados

**Exemplo de uso:**

```python
# Buscar contratos pendentes de um casamento específico
contracts = (
    Contract.objects
    .for_wedding(wedding)
    .pending_signature()
    .order_by_priority()
)

# Buscar contratos completos do cerimonialista
completed = (
    Contract.objects
    .for_planner(request.user)
    .completed()
    .with_related()
)
```

### 2. Mixins Reutilizáveis (`mixins.py`)

Mixins granulares que seguem o **Princípio da Responsabilidade Única (SRP)**:

#### Mixins Independentes (Standalone)

- **`ContractOwnershipMixin`**: Garante ownership através do planner
- **`ContractQuerysetMixin`**: Lógica de construção de querysets
- **`ContractSignatureMixin`**: Lógica de processamento de assinaturas
- **`ContractUrlGeneratorMixin`**: Geração de URLs e links
- **`ContractEmailMixin`**: Envio de e-mails
- **`ContractActionsMixin`**: Ações em contratos (cancelar, editar, upload)
- **`JsonResponseMixin`**: Helpers para respostas JSON

#### Mixin de Composição (Facade)

- **`ContractManagementMixin`**: Agrupa todos os mixins acima em uma interface única

**Exemplo de uso:**

```python
class MyContractView(
    LoginRequiredMixin,
    ContractOwnershipMixin,
    ContractManagementMixin,
    View
):
    def post(self, request, contract_id):
        contract = get_object_or_404(Contract, id=contract_id)
        
        # Usar métodos dos mixins
        success, message = self.cancel_contract(contract)
        
        if success:
            return self.json_success(message)
        return self.json_error(message)
```

### 3. Models (`models.py`)

O modelo `Contract` foi atualizado com:

- **Manager customizado**: Usa `ContractQuerySet.as_manager()`
- **Métodos de negócio**: Lógica de assinatura, hash de integridade, etc.
- **Properties**: `supplier`, `wedding`, `contract_value`
- **Métodos auxiliares**: 
  - `process_signature()`: Processa e valida assinaturas
  - `get_next_signer_info()`: Retorna info do próximo signatário
  - `is_fully_signed()`: Verifica se todas as partes assinaram
  - `get_signatures_status()`: Retorna status de todas as assinaturas

### 4. Views (`views.py`)

Views refatoradas usando os mixins:

#### Class-Based Views

- **`ContractsPartialView`**: Lista contratos de um casamento
- **`GenerateSignatureLinkView`**: Gera link e envia e-mail
- **`SignContractExternalView`**: Assinatura externa (pública)
- **`CancelContractView`**: Cancela contrato
- **`EditContractView`**: Edita descrição do contrato
- **`UploadContractView`**: Upload de contrato externo

#### Function-Based Views

- **`download_contract_pdf()`**: Download do PDF com QR Code
- **`link_callback()`**: Callback para recursos estáticos no PDF

## Benefícios da Refatoração

### 1. Reutilização de Código (DRY)
- Lógica comum extraída para mixins
- QuerySets reutilizáveis entre views
- Redução de duplicação de código

### 2. Manutenibilidade
- Código organizado por responsabilidade
- Fácil localização de funcionalidades
- Alterações isoladas sem efeitos colaterais

### 3. Testabilidade
- Mixins podem ser testados individualmente
- QuerySets testáveis isoladamente
- Mocks mais simples

### 4. Legibilidade
- Views mais limpas e focadas
- Nomenclatura clara e consistente
- Documentação inline

### 5. Performance
- Queries otimizadas com select_related
- Anotações eficientes
- Prevenção de N+1 queries

## Padrões de Design Utilizados

### 1. **Facade Pattern**
O `ContractManagementMixin` atua como uma fachada que simplifica o acesso a múltiplos mixins.

### 2. **Mixin Pattern**
Composição de funcionalidades através de herança múltipla.

### 3. **Manager Pattern**
QuerySets customizados conectados ao modelo via manager.

### 4. **Strategy Pattern**
Diferentes estratégias de filtragem e ordenação nos querysets.

## Comparação: Antes vs Depois

### Antes (views.py original)

```python
class GenerateSignatureLinkView(LoginRequiredMixin, View):
    def get(self, request, contract_id):
        contract = get_object_or_404(Contract, id=contract_id)
        link = request.build_absolute_uri(contract.get_absolute_url())
        
        # Lógica repetida para determinar próximo signatário
        next_signer = "Alguém"
        if contract.status == "WAITING_PLANNER":
            next_signer = "Você (Cerimonialista)"
        elif contract.status == "WAITING_SUPPLIER":
            # ... mais código repetido
        
        return JsonResponse({
            "link": link,
            "status": contract.status,
            "message": f"Próximo a assinar: {next_signer}"
        })
```

### Depois (views.py refatorado)

```python
class GenerateSignatureLinkView(
    LoginRequiredMixin,
    ContractManagementMixin,
    View
):
    def get(self, request, contract_id):
        contract = get_object_or_404(Contract, id=contract_id)
        link_info = self.generate_signature_link(contract)
        return JsonResponse(link_info)
```

**Resultado:**
- ✅ Menos linhas de código
- ✅ Lógica reutilizável
- ✅ Mais fácil de testar
- ✅ Consistente com outros apps

## Testes

Para testar os querysets e mixins:

```python
# Testar QuerySet
def test_for_planner():
    contracts = Contract.objects.for_planner(planner)
    assert all(c.item.wedding.planner == planner for c in contracts)

# Testar Mixin
class TestContractSignatureMixin:
    def test_get_client_ip(self):
        mixin = ContractSignatureMixin()
        request = RequestFactory().get('/')
        ip = mixin.get_client_ip(request)
        assert ip is not None
```

## Próximos Passos

1. ✅ Criar testes unitários para querysets
2. ✅ Criar testes unitários para mixins
3. ✅ Criar testes de integração para views
4. ✅ Adicionar type hints completos
5. ✅ Documentar APIs públicas

## Referências

- [Django QuerySets](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- [Django Mixins](https://docs.djangoproject.com/en/stable/topics/class-based-views/mixins/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
>>>>>>> origin/main

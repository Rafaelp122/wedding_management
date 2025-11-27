# Contracts - Documentação Técnica Completa

Sistema de assinatura digital tripartite para contratos de casamento.

**Versão:** 2.0  
**Status:** ✅ 61 testes passando  
**Cobertura:** models, querysets, mixins, views  

---

## Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Models](#models)
- [QuerySets](#querysets)
- [Mixins](#mixins)
- [Views](#views)
- [Fluxo de Assinatura](#fluxo-de-assinatura)
- [Segurança](#segurança)
- [Testes](#testes)
- [Exemplos de Uso](#exemplos-de-uso)
- [Referências](#referências)

---

## Visão Geral

O app `contracts` gerencia contratos financeiros e jurídicos associados aos itens do casamento, implementando um **sistema completo de assinatura digital sequencial** com três partes:

1. **Cerimonialista** (Planner) - Valida e inicia o contrato
2. **Fornecedor** (Supplier) - Aceita os termos
3. **Noivos** (Couple) - Aprovação final

### Características Principais

- ✅ Relação OneToOne com Item (criação automática)
- ✅ Assinatura digital sequencial com validações
- ✅ Auditoria completa (IP + timestamp)
- ✅ Hash de integridade SHA256
- ✅ Geração de PDF com QR Code
- ✅ Notificações por e-mail
- ✅ Upload de contratos externos
- ✅ Gestão completa (edição, cancelamento)

---

## Arquitetura

O app segue os princípios **SOLID** e **DRY**, organizado em camadas:

```
contracts/
├── models.py          # Modelo Contract com lógica de negócio
├── querysets.py       # QuerySets customizados
├── mixins.py          # Mixins reutilizáveis para views
├── views.py           # Views (CBV e FBV)
├── urls.py            # Rotas
├── constants.py       # Constantes (status, limites)
├── forms.py           # Formulários (se houver)
└── tests/
    ├── test_models.py      # 25 testes
    ├── test_querysets.py   # Testes de querysets
    ├── test_mixins.py      # 18 testes
    └── test_views.py       # 18 testes
```

### Padrões de Design

1. **Facade Pattern** - `ContractManagementMixin` simplifica acesso a múltiplos mixins
2. **Mixin Pattern** - Composição de funcionalidades via herança múltipla
3. **Manager Pattern** - QuerySets customizados conectados ao modelo
4. **Strategy Pattern** - Diferentes estratégias de filtragem e ordenação

---

## Models

### Contract

Modelo principal que representa um contrato.

**Campos principais:**

```python
class Contract(BaseModel):
    # Relação
    item = OneToOneField(Item, on_delete=CASCADE)
    
    # Dados do contrato
    description = TextField(blank=True)
    status = CharField(max_length=50, choices=STATUS_CHOICES)
    token = UUIDField(default=uuid.uuid4, unique=True)
    
    # Assinaturas - Planner
    planner_signature = FileField(upload_to="signatures/planner/")
    planner_signed_at = DateTimeField(null=True)
    planner_ip = GenericIPAddressField(null=True)
    
    # Assinaturas - Fornecedor
    supplier_signature = FileField(upload_to="signatures/supplier/")
    supplier_signed_at = DateTimeField(null=True)
    supplier_ip = GenericIPAddressField(null=True)
    
    # Assinaturas - Noivos
    couple_signature = FileField(upload_to="signatures/couple/")
    couple_signed_at = DateTimeField(null=True)
    couple_ip = GenericIPAddressField(null=True)
    
    # Integridade
    integrity_hash = CharField(max_length=64)  # SHA256
    
    # Arquivos
    external_pdf = FileField(upload_to="contracts_external/")
```

**Status do Contrato:**

- `DRAFT` - Rascunho
- `WAITING_PLANNER` - Aguardando Cerimonialista
- `WAITING_SUPPLIER` - Aguardando Fornecedor
- `WAITING_COUPLE` - Aguardando Noivos
- `COMPLETED` - Concluído
- `CANCELED` - Cancelado

**Métodos principais:**

```python
# Processar assinatura
contract.process_signature(signature_b64, client_ip)

# Verificar próximo assinante
info = contract.get_next_signer_info()  # {'role': 'Fornecedor', 'name': '...'}

# Verificar se está completo
is_complete = contract.is_fully_signed()  # True/False

# Status de todas as assinaturas
status = contract.get_signatures_status()
```

**Properties delegadas:**

```python
contract.supplier        # self.item.supplier
contract.wedding         # self.item.wedding
contract.contract_value  # self.item.total_price
```

---

## QuerySets

### ContractQuerySet

QuerySet customizado com métodos de filtragem e operações em lote.

**Métodos disponíveis:**

```python
Contract.objects
    .for_planner(planner)      # Filtra por cerimonialista
    .for_wedding(wedding)       # Filtra por casamento
    .with_related()             # Otimiza queries
    .pending_signature()        # Aguardando assinatura
    .completed()                # Completos
    .canceled()                 # Cancelados
    .by_status(status)          # Por status específico
    .search(query)              # Busca textual
    .fully_signed()             # Com todas as assinaturas
    .editable()                 # Podem ser editados
    .cancelable()               # Podem ser cancelados
    .bulk_cancel()              # Cancela múltiplos
    .bulk_update_description()  # Atualiza múltiplos
```

**Exemplo:**

```python
# Buscar contratos pendentes de um casamento
contracts = (
    Contract.objects
    .for_wedding(wedding)
    .pending_signature()
    .with_related()
)

# Cancelar todos os contratos de um planner
count = (
    Contract.objects
    .for_planner(planner)
    .bulk_cancel()
)
```

---

## Mixins

### Mixins Independentes

1. **ContractOwnershipMixin** - Garante ownership através do planner
2. **ContractQuerysetMixin** - Lógica de construção de querysets
3. **ContractSignatureMixin** - Processamento de assinaturas
4. **ContractUrlGeneratorMixin** - Geração de URLs e links
5. **ContractEmailMixin** - Envio de e-mails
6. **ContractActionsMixin** - Ações (cancelar, editar, upload)

### Mixin Facade

**ContractManagementMixin** - Agrupa todos os mixins acima em uma interface única.

**Exemplo de uso:**

```python
class MyContractView(
    ContractOwnershipMixin,
    ContractManagementMixin,
    View
):
    def post(self, request, contract_id):
        contract = self.get_queryset().get(id=contract_id)
        success, message = self.cancel_contract(contract)
        
        if success:
            return self.json_success(message)
        return self.json_error(message)
```

---

## Views

### Class-Based Views

1. **ContractsPartialView** - Lista contratos de um casamento
2. **GenerateSignatureLinkView** - Gera link e envia e-mail
3. **SignContractExternalView** - Página pública de assinatura
4. **CancelContractView** - Cancela contrato
5. **EditContractView** - Edita descrição
6. **UploadContractView** - Upload de PDF externo

### Function-Based Views

1. **download_contract_pdf()** - Download do PDF com QR Code
2. **link_callback()** - Callback para recursos estáticos (xhtml2pdf)

### Rotas

```python
urlpatterns = [
    path("partial/<int:wedding_id>/", 
         ContractsPartialView.as_view(), 
         name="partial_contracts"),
    
    path("generate-link/<int:contract_id>/", 
         GenerateSignatureLinkView.as_view(), 
         name="generate_link"),
    
    path("sign/<uuid:token>/", 
         SignContractExternalView.as_view(), 
         name="sign_contract"),
    
    path("download-pdf/<int:contract_id>/", 
         download_contract_pdf, 
         name="download_pdf"),
    
    path("cancel/<int:contract_id>/", 
         CancelContractView.as_view(), 
         name="cancel_contract"),
    
    path("edit/<int:contract_id>/", 
         EditContractView.as_view(), 
         name="edit_contract"),
    
    path("upload/<int:contract_id>/", 
         UploadContractView.as_view(), 
         name="upload_contract"),
]
```

---

## Fluxo de Assinatura

```
[Planner cria contrato]
    ↓
[Status: WAITING_PLANNER]
    → Planner assina (via dashboard)
    ↓
[Status: WAITING_SUPPLIER]
    → Link enviado para fornecedor
    → Fornecedor assina via link público (UUID token)
    ↓
[Status: WAITING_COUPLE]
    → Link enviado para noivos
    → Noivos assinam via link público (UUID token)
    ↓
[Status: COMPLETED]
    → Hash de integridade SHA256 gerado
    → PDF final disponível para download
```

### Validações de Assinatura

**Formato:**
- PNG, JPG, JPEG apenas
- Base64 válido

**Tamanho:**
- Máximo 500KB

**Segurança:**
- Status correto para assinatura
- Sequência respeitada
- Token UUID único e não-guessável

**Auditoria:**
- IP do assinante capturado
- Timestamp preciso registrado
- Hash SHA256 final após conclusão

---

## Segurança

### Autenticação e Autorização

- **Views protegidas**: `LoginRequiredMixin`
- **Ownership**: Verificação de planner do casamento
- **Acesso público**: Apenas para assinatura via token UUID

### Validações

```python
# Validação de formato
ALLOWED_SIGNATURE_FORMATS = ['image/png', 'image/jpeg', 'image/jpg']

# Validação de tamanho
MAX_SIGNATURE_SIZE = 500 * 1024  # 500KB

# Validação de base64
if not signature_b64 or 'base64,' not in signature_b64:
    raise ValueError("Assinatura inválida ou vazia")
```

### Auditoria

Cada assinatura registra:
- IP do assinante (`GenericIPAddressField`)
- Timestamp exato (`DateTimeField`)
- Hash final SHA256 (após todas as assinaturas)

---

## Testes

### Estrutura de Testes (61 total)

**Models (25 testes):**
- CRUD básico (5)
- Processamento de assinaturas (8)
- Métodos de status (5)
- Hash de integridade (2)
- Informações do próximo assinante (5)

**QuerySets:**
- Filtros e buscas
- Operações em lote

**Mixins (18 testes):**
- ContractOwnershipMixin (4)
- ContractSignatureMixin (5)
- ContractEmailMixin (3)
- ContractActionsMixin (6)

**Views (18 testes):**
- ContractsPartialView (6)
- GenerateSignatureLinkView (4)
- SignContractExternalView (5)
- DownloadContractPDFView (3)

### Executar Testes

```bash
# Todos os testes
python manage.py test apps.contracts

# Com verbosidade
python manage.py test apps.contracts -v 2

# Teste específico
python manage.py test apps.contracts.tests.test_models.ContractSignatureProcessingTest

# Com cobertura
pytest apps/contracts --cov=apps.contracts --cov-report=html
```

---

## Exemplos de Uso

### 1. Processar Assinatura

```python
contract = Contract.objects.get(token=token)
try:
    contract.process_signature(
        signature_b64="data:image/png;base64,iVBORw0KG...",
        client_ip="192.168.1.1"
    )
except ValueError as e:
    print(f"Erro: {e}")
```

### 2. Verificar Status de Assinaturas

```python
contract = Contract.objects.get(pk=1)
status = contract.get_signatures_status()

# Resultado:
# {
#     'planner': {'signed': True, 'signed_at': datetime, 'ip': '192.168.1.1'},
#     'supplier': {'signed': True, 'signed_at': datetime, 'ip': '10.0.0.1'},
#     'couple': {'signed': False, 'signed_at': None, 'ip': None}
# }
```

### 3. Gerar Link de Assinatura

```python
contract = Contract.objects.get(pk=1)
link = request.build_absolute_uri(contract.get_absolute_url())
# https://example.com/contratos/sign/uuid-token/
```

### 4. Buscar Contratos

```python
# Todos pendentes
pending = Contract.objects.pending_signature()

# Completos de um casamento
completed = (
    Contract.objects
    .for_wedding(wedding)
    .completed()
    .with_related()
)

# Editáveis de um planner
editable = (
    Contract.objects
    .for_planner(request.user)
    .editable()
)
```

### 5. Cancelar Contrato

```python
success, message = contract_management_mixin.cancel_contract(contract)
if success:
    print(f"Contrato cancelado: {message}")
```

---

## Performance

### Otimizações

1. **Query Optimization**: `select_related("item__wedding")` evita N+1
2. **Cascade Delete**: Gerenciado pelo banco de dados
3. **Queries Anotadas**: QuerySets com anotações eficientes
4. **Cache de QR Code**: Gerado uma vez e armazenado

### Indexação

Considerar adicionar índices em:
- `status` (queries frequentes por status)
- `token` (já é unique, mas adicionar índice explícito)
- `item_id` (foreign key, já indexada automaticamente)

---

## Integração com Outros Apps

### Com Items
- Relação OneToOne automática
- Cascade delete (Item deletado → Contract deletado)
- Property delegation (`contract.supplier`, `contract.wedding`)

### Com Weddings
- Filtro por casamento via `item__wedding`
- Verificação de ownership (planner)

### Com Core
- Herda `BaseModel` (created_at, updated_at)
- Usa constantes compartilhadas

---

## Referências

- [Django QuerySets](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- [Django Mixins](https://docs.djangoproject.com/en/stable/topics/class-based-views/mixins/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [xhtml2pdf Documentation](https://xhtml2pdf.readthedocs.io/)
- [QR Code Library](https://github.com/lincolnloop/python-qrcode)

---

**Última Atualização:** 27 de novembro de 2025  
**Versão:** 2.0 - Sistema Completo de Assinatura Digital Tripartite

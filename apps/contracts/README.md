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

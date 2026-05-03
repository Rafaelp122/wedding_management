# Padrões de Testes - Backend

Este documento estabelece as diretrizes e padrões para a implementação de testes automatizados no backend do projeto Wedding Management. O objetivo é garantir consistência, segurança por design e alta confiabilidade nas regras de negócio.

## 1. Ferramental

O projeto utiliza o ecossistema `pytest` para execução de testes:
- **pytest-django**: Integração com o framework Django.
- **factory-boy**: Criação de blueprints (factories) para dados de teste.
- **faker (pt_BR)**: Geração de dados realistas brasileiros (configurado globalmente em `conftest.py`).
- **pytest-cov**: Relatórios de cobertura de código.
- **pytest-mock**: Facilita o uso de mocks e patches.

## 2. Estrutura de Arquivos e Fixtures

### 2.1.1 Estrutura Padrão (Entidade Única)
Cada aplicativo (`app`) com foco em um único recurso principal (ex: `weddings`) segue esta estrutura:
```text
apps/meu_app/tests/
├── conftest.py          # Fixtures locais (específicas do domínio)
├── factories.py         # Blueprints de modelos do app
├── test_models.py       # Testes de integridade física e metadados
├── test_services.py     # Testes de lógica de negócio Pura (Core)
└── test_apis.py         # Testes de contrato, segurança e isolamento
```

### 2.1.2 Domínios com Múltiplas Entidades
Para aplicativos que gerenciam diversos recursos independentes (ex: `logistics`, `finances`), a estrutura deve ser expandida para evitar arquivos gigantescos e facilitar a manutenção. Crie subdiretórios por entidade:

```text
apps/meu_app/tests/
├── conftest.py
├── factories.py
├── entidade_a/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_apis.py
└── entidade_b/
    ├── __init__.py
    ├── ...
```
> **Nota de Implementação:** É obrigatório incluir um arquivo `__init__.py` em cada subdiretório de entidade. Isso garante que o motor do Pytest diferencie os módulos (ex: `entidade_a.test_models` vs `entidade_b.test_models`) e evita erros de colisão durante a coleta.

### 2.2 Conftest Global vs Local
- **`backend/conftest.py` (Global)**: Contém fixtures compartilhadas por todo o projeto, como `user` (usuário base), `auth_client` (cliente Ninja com JWT injetado) e registro de factories globais.
- **`apps/meu_app/tests/conftest.py` (Local)**: Contém fixtures específicas para o domínio daquela aplicação (ex: um casamento pronto, um contrato assinado).

## 3. Camadas de Teste

### 3.1 Modelos (`test_models.py`)
Foca na integridade do banco de dados e metadados.
- **O que testar**:
  - Validações de campo físicas (`max_length`, `null`, `blank`).
  - Regras que dependem do `full_clean` (estado interno do modelo).
  - Representação em string (`__str__`).
  - Ordenação padrão (`Meta.ordering`).
  - **Transições de estado puramente locais** (que não exijam orquestração de outros serviços ou models).

### 3.2 Serviços (`test_services.py`) - **Pureza do Domínio**
Onde reside a lógica de negócio complexa. O Service Layer recebe instâncias já validadas.
- **O que testar**:
  - Regras de negócio puras (cálculos, validações de estado complexas).
  - **Fail Fast**: Validar que o serviço levanta exceções (`BusinessRuleViolation`, `DomainIntegrityError`) ao receber dados inconsistentes.
  - **Isolamento**: Testar o filtro de escopo apenas em métodos de `list` e `create`.
  - **Nota:** Testes de "Isolamento de Recurso" (ex: tentar atualizar um UUID alheio) são responsabilidade da **API**, pois a trava de autorização está no Controller, não no Service.

**Regra de cobertura (Mandatório):** Toda função pública em `services.py` deve ter pelo menos **um teste de sucesso** e **um teste de falha**. Serviço sem testes não pode ser alterado — primeiro cubra o comportamento atual, depois refatore.

### 3.3 APIs (`test_apis.py`) - **Segurança e Isolamento**
Valida o contrato HTTP e a barreira de segurança de acesso aos dados.
- **O que testar**:
  - **Cenários Felizes**: Retorno 200/201 com JSON correto.
  - **Isolamento (Multitenancy)**: Tentar acessar/modificar UUID de outro planner deve retornar `404 Not Found`. Nunca `403 Forbidden` para UUIDs alheios — isso vazaria a existência do recurso.
  - **Segurança**: Chamadas sem Token ou com Token expirado devem retornar `401 Unauthorized`.
  - **Integridade**: Enviar UUIDs malformados ou tipos errados deve retornar `422 Unprocessable Entity`.

### 3.4 Auditoria de Segurança Estática (`test_security_audit.py`) - **CRÍTICO**
Localizado em `apps/core/tests/`, este teste usa AST (Abstract Syntax Tree) para garantir que nenhum endpoint de instância (UUID) seja criado sem a chamada explícita para a sua função auxiliar de autorização (ex: `get_wedding()`). O CI quebrará se essa regra for violada.

## 4. Padrões e Convenções

### 4.1 Uso de Factories
Sempre use factories para criação de dados. `.objects.create()` é proibido em testes.
```python
# Correto
wedding = WeddingFactory(company=user.company, bride_name="Maria")

# Evite
wedding = Wedding.objects.create(company=user.company, bride_name="Maria", date="2026-01-01")
```

### 4.2 Mocks e Patches
Use mocks para validar se efeitos colaterais ocorrem (ou não) conforme o esperado.

```python
# Exemplo 1: Efeito esperado ocorreu
def test_create_wedding_triggers_budget_creation(user, wedding_payload):
    with patch("apps.finances.services.BudgetService.create") as mock_budget:
        WeddingService.create(company=user.company, data=wedding_payload)
    mock_budget.assert_called_once()

# Exemplo 2: Efeito não deve ocorrer em certo fluxo
def test_create_draft_does_not_trigger_budget(user, draft_payload):
    with patch("apps.finances.services.BudgetService.create") as mock_budget:
        WeddingService.create_draft(company=user.company, data=draft_payload)
    mock_budget.assert_not_called()
```

### 4.3 Markers do Pytest
Utilize markers para categorizar testes e otimizar a execução local:
```python
@pytest.mark.slow
def test_massive_data_export():
    ...
```
Configure-os no `backend/pyproject.toml` (seção `[tool.pytest.ini_options]`) e utilize `pytest -m "not slow"` para um ciclo de feedback mais rápido durante o desenvolvimento.

### 4.4 Naming Convention
- **Classes**: `Test<NomeDoServiçoOuModel>`
- **Métodos**: `test_<comportamento>_<cenário>_<resultado_esperado>`
  - Ex: `test_create_installment_with_invalid_value_raises_error`
  - Ex: `test_pay_paid_installment_raises_business_rule_violation`

### 4.5 Independência de Factories
Factories de um app não devem depender de factories de outro app. Se `ExpenseFactory` depende de `ContractFactory` (logistics), acoplamento entre domínios é introduzido nos testes. Prefira criar apenas os objetos mínimos necessários para o teste, usando `SubFactory` apenas dentro do mesmo app.
```python
# Evite: cross-app SubFactory
class ExpenseFactory(factory.django.DjangoModelFactory):
    contract = factory.SubFactory("apps.logistics.tests.factories.ContractFactory")

# Prefira: criar dependências mínimas no próprio teste
def test_expense_creation(user):
    category = BudgetCategoryFactory(company=user.company)
    expense = ExpenseFactory(company=user.company, category=category, contract=None)
```

## 5. O que NÃO testar (Economia de Tempo)
- **Django ORM**: Não teste se o `.save()` persiste dados ou se filtros básicos do Django funcionam.
- **Bibliotecas Externas**: Não teste o Pydantic, Django Ninja ou bibliotecas de terceiros isoladamente.
- **Lógica Pura de Framework**: Não teste se um Schema valida tipos básicos se não houver regra de negócio envolvida.
- **422 de tipagem**: Não teste exaustivamente erros 422 para cada campo com tipo incorreto. Confie no Pydantic/Django Ninja. Teste apenas 422 que envolvam regra de negócio.

**Foque nas SUAS regras e nos SEUS contratos.**

## 6. Regras de Qualidade do Código de Teste

### 6.1 Proibição de Stubs Vazios
Métodos de teste com `pass` ou corpo vazio são proibidos. Eles geram falsa sensação de cobertura e mascaram funcionalidade não testada.
```python
# Proibido
def test_something(self):
    pass

# Proibido
def test_something(self):
    """TODO: implement later"""
```
Se um teste não pode ser escrito agora, deixe um comentário `# SKIP: <motivo>` e use `@pytest.mark.skip(reason="...")`.

### 6.2 Proibição de Debug Files em tests/
Arquivos como `test_jwt_debug.py` com `print()` ou `breakpoint()` não pertencem ao diretório de testes. Testes são documentação executável — debug files devem ser descartados ou movidos para fora do path de coleta do pytest.

### 6.3 Proibição de Duplicação de Testes
Dois arquivos de teste que validam os mesmos cenários (ex: `test_apis.py` e `test_viewsets.py` com testes idênticos) devem ser consolidados. Mantenha apenas um arquivo por camada por entidade. A duplicação aumenta o tempo de execução e a carga de manutenção sem adicionar cobertura real.

### 6.4 Cobertura Pré-Refactor (Regra de Ouro)
**Antes de alterar um serviço existente, escreva testes para o comportamento atual.** Isso vale especialmente para código sem cobertura. O fluxo correto é:

1. Escrever testes que passam no código atual (baseline)
2. Refatorar ou adicionar funcionalidade
3. Verificar que os testes antigos ainda passam + novos testes para o novo comportamento

Nunca refatore às cegas um serviço com 0% de cobertura.

## 7. Apêndice: Cenários Universais de Teste (Cheat Sheet)

Use esta lista como um guia mental rápido ao desenvolver novos recursos. A ordem de priorização natural é: **Negócio > Segurança > Contrato > Limites > Efeitos Colaterais**.

### 7.1 Regras de Negócio (Prioridade Máxima)
- **Caminhos felizes:** Operação executada com dados válidos retorna o esperado.
- **Efeitos Colaterais Esperados:** Ocorrem conforme planejado (testado via mocks).
- **Caminhos Tristes:** Dados inválidos levantam a exceção correta (`BusinessRuleViolation`).
- **Invariantes de Domínio:** Um estado inválido nunca pode ser atingido (ex: convidados negativos, data fim antes de data início). Testado no `test_models.py` e `test_services.py`.

### 7.2 Isolamento e Segurança (Multitenancy)
- **Isolamento Estrito:** Usuário A não consegue ler, modificar ou deletar dados do Usuário B.
- **Privacidade de Existência:** A resposta de erro não vaza a existência do recurso (sempre retornar `404`, nunca `403` para UUIDs alheios). Validado via dependências de autorização no Controller.

### 7.3 Contrato da API (Endpoints)
- **Aderência ao Schema:** Payload correto retorna status (200/201) e estrutura (JSON) esperados.
- **Nota sobre o Framework:** Não teste exaustivamente erros 422 para cada campo de tipagem incorreta. Confie no Pydantic/Django Ninja para a validação de tipos de dados. Concentre-se em garantir que o Schema correto está acoplado ao Endpoint.

### 7.4 Limites e Valores Extremos (Boundary Testing)
Para qualquer campo numérico ou de tamanho, sempre teste:
- `valor = 0` (zero)
- `valor = -1` (abaixo do mínimo)
- `valor = máximo` (exatamente no limite)
- `valor = máximo + 1` (acima do limite)
- `valor = None` (ausência de valor)

### 7.5 Concorrência e Performance (Pragmatismo)
- **Concorrência:** Não tente simular *race conditions* no Pytest (gera flaky tests). Teste a existência do mecanismo de proteção (ex: `select_for_update` foi chamado? A `UniqueConstraint` existe no Model?).
- **N+1 Queries:** Não faça `assertNumQueries` manualmente. Confie no pacote `django-zeal` e na flag `--nplusone-raise` do CI para quebrar o build automaticamente se houver consultas desnecessárias.

### 7.6 Regressão
- Todo bug corrigido ganha um teste que reproduz exatamente aquele bug.
- O teste deve falhar no commit do bug e passar no commit da correção.

---

**Última atualização:** 3 de maio de 2026
**Versão:** 2.0 — Adicionada estrutura multi-entidade, auditoria estática, markers, cheat sheet, anti-stub, anti-debug, anti-duplicação e regra de cobertura pré-refactor.

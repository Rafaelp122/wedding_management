# Padrões de Testes - Backend

Este documento estabelece as diretrizes e padrões para a implementação de testes automatizados no backend do projeto Wedding Management. O objetivo é garantir consistência, isolamento de dados (multitenancy) e alta confiabilidade nas regras de negócio.

## 1. Ferramental

O projeto utiliza o ecossistema `pytest` para execução de testes:
- **pytest-django**: Integração com o framework Django.
- **factory-boy**: Criação de blueprints (factories) para dados de teste.
- **faker (pt_BR)**: Geração de dados realistas brasileiros.
- **pytest-cov**: Relatórios de cobertura de código.
- **pytest-mock**: Facilita o uso de mocks e patches.

## 2. Estrutura de Diretórios

Cada aplicativo (`app`) dentro de `backend/apps/` deve seguir esta estrutura de testes:

```text
apps/meu_app/tests/
├── __init__.py
├── conftest.py          # Fixtures locais do app
├── factories.py         # Blueprints de modelos
├── test_models.py       # Testes de integridade de dados e modelos
├── test_services.py     # Testes de lógica de negócio (Core)
└── test_apis.py         # Testes de endpoints (Django Ninja)
```

## 3. Camadas de Teste

### 3.1 Modelos (`test_models.py`)
Foca na integridade do banco de dados e comportamentos básicos do objeto.
- **O que testar**:
  - Validações de campo (especialmente regras que dependem do `full_clean`).
  - Representação em string (`__str__`).
  - Ordenação padrão (`Meta.ordering`).
  - Transições de estado simples.

### 3.2 Serviços (`test_services.py`) - **Prioridade Máxima**
Onde reside a lógica de negócio complexa. É a camada mais importante para garantir a correção do sistema.
- **O que testar**:
  - Fluxos completos de criação, atualização e deleção.
  - **Isolamento (Multitenancy)**: Garantir que um usuário não acesse dados de outro através do manager `.for_tenant(company)`.
  - **Fail Fast**: Validar que o serviço interrompe a execução (levanta exceção) ao receber dados inválidos antes de tocar no banco.
  - **Efeitos Colaterais**: Validar se processos em segundo plano ou *lazy loading* estão funcionando conforme esperado usando mocks.

### 3.3 APIs (`test_apis.py`)
Valida o contrato de entrada e saída e a integração com o protocolo HTTP.
- **O que testar**:
  - Códigos de status HTTP (200, 201, 403, 404, 422).
  - Permissões de acesso (autenticação e autorização).
  - Estrutura do JSON de resposta (Schema).
  - Mensagens de erro para validação de payload.

## 4. Padrões e Convenções

### 4.1 Uso de Factories
Nunca crie objetos manualmente com `Model.objects.create()`. Use sempre as factories:
```python
# Correto
wedding = WeddingFactory(company=user.company, bride_name="Maria")

# Evite
wedding = Wedding.objects.create(company=user.company, bride_name="Maria", date="2026-01-01")
```

### 4.2 Isolamento de Dados (Multitenancy)
Sempre inclua um teste que valide se os dados estão isolados entre usuários (planners):
1. Crie dados para o `Usuário A`.
2. Tente acessar ou modificar esses dados com o `Usuário B`.
3. Garanta que o sistema retorne 404 (API) ou uma lista vazia (Manager).

### 4.3 Mocks e Patches
Use mocks para isolar componentes que não fazem parte do teste atual, especialmente para evitar que a execução de um serviço dispare ações indesejadas em outros apps:
```python
def test_create_wedding_no_side_effects(user, wedding_payload):
    with patch("apps.finances.services.BudgetService.create") as mock_budget:
        WeddingService.create(company=user.company, data=wedding_payload)

    mock_budget.assert_not_called()
```

### 4.4 Naming Convention
- **Classes**: `Test<NomeDoServiçoOuModel>`
- **Métodos**: `test_<comportamento>_<cenário>_<resultado_esperado>`
  - Ex: `test_create_installment_with_invalid_value_raises_error`

## 5. Filosofia "Fail Fast"
Nossos serviços devem validar os dados agressivamente. Se uma regra de negócio for violada, o teste deve verificar se a exceção correta foi lançada (`BusinessRuleViolation` ou `DomainIntegrityError`) e se nenhuma alteração foi persistida no banco de dados.

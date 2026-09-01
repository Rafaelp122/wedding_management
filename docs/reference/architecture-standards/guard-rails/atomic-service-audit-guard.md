# Especificação Técnica: Guard-Rail de Atomicidade na Service Layer

> **Categoria:** Referência Técnica (Guard-Rails & Integridade)
> **Relacionados:** [MOC de Guard-Rails](index.md) · [ADR-006: Service Layer Pattern](../../../architecture/adr/006-service-layer.md) · [Suíte de Guard-Rails](../../../architecture/concepts/architectural-guard-rails-suite.md)
> **Implementação:** `backend/apps/core/tests/test_atomic_service_audit.py`

---

## 1. Visão Geral e Importância Arquitetural

Em sistemas transacionais com múltiplos modelos interdependentes (ex: criação de contrato logístico que gera despesa, parcelas e atualiza o orçamento total), falhas intermediárias podem deixar o banco de dados em um estado corrompido ou parcial (*partial write disaster*).

O guard-rail **`test_atomic_service_audit.py`** utiliza análise estática de Árvore Sintática Abstrata (AST) para garantir que **qualquer função ou método de serviço que execute duas ou mais operações de escrita no ORM esteja obrigatoriamente encapsulada em uma transação atômica** (`@transaction.atomic` ou `with transaction.atomic():`).

```mermaid
flowchart TD
    FindServices["1. Descobre arquivos em apps/*/services/"] --> ParseAST["2. Parse para Árvore AST (ast.parse)"]
    ParseAST --> WalkFuncs["3. Itera sobre FunctionDef e AsyncFunctionDef"]
    WalkFuncs --> CountWrites["4. Conta chamadas ao ORM (save, create, delete, update)"]
    CountWrites --> CheckCount{write_count >= 2?}
    CheckCount -->|Não (0 ou 1)| PassFunc["✅ Função Segura"]
    CheckCount -->|Sim (2+ escritas)| CheckAtomic{Possui @atomic ou with atomic?}
    CheckAtomic -->|Sim| PassFunc
    CheckAtomic -->|Não| FailTest["❌ Reprova o Teste no pytest com arquivo e linha"]
```

---

## 2. Mecânica de Análise Estática por AST

O teste opera de forma instantânea em memória (sem necessidade de banco de dados ativo):

### 2.1 Métodos de Escrita Monitorados (`WRITE_METHODS`)
```python
WRITE_METHODS: set[str] = {
    "save",
    "create",
    "bulk_create",
    "bulk_update",
    "update",
    "delete",
    "get_or_create",
    "update_or_create",
}
```

### 2.2 Isolamento de Escopo de Funções Aninhadas
A função `_walk_own_body(func_node)` percorre estritamente os nós da própria função, evitando que chamadas de escrita dentro de closures ou callbacks internos inflem a contagem da função principal.

---

## 3. Comparativo de Conformidade no Código

### ❌ Incorreto (Violará o Guard-Rail no CI)
```python
# apps/finances/services/contract_service.py
class ContractService:
    @staticmethod
    def create_contract_and_expense(company, payload):  # ❌ 2 escritas sem @transaction.atomic
        contract = Contract.objects.create(company=company, name=payload.name)  # Escrita 1
        expense = Expense.objects.create(company=company, amount=payload.amount) # Escrita 2
        return contract
```
*Erro disparado:* `Função 'create_contract_and_expense' em apps/finances/services/contract_service.py:12 realiza 2 escritas sem atomic.`

---

### :material-check-circle: Correto (Aprovado pelo Guard-Rail)
```python
# apps/finances/services/contract_service.py
from django.db import transaction

class ContractService:
    @staticmethod
    @transaction.atomic  # :material-check-circle: Protegido contra escritas parciais
    def create_contract_and_expense(company, payload):
        contract = Contract.objects.create(company=company, name=payload.name)
        expense = Expense.objects.create(company=company, amount=payload.amount)
        return contract
```

---

## 4. Como Executar e Resolver Violações

### Comando de Execução
```bash
pytest backend/apps/core/tests/test_atomic_service_audit.py -v
```

### Guia de Resolução
1. Abra o arquivo e linha apontados pelo relatório do pytest.
2. Importe o módulo de transação do Django: `from django.db import transaction`.
3. Adicione o decorador `@transaction.atomic` sobre a função ou encapsule as escritas em um bloco `with transaction.atomic():`.

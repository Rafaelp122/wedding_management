# Padrões de Comentários e Docstrings

> **Módulo:** Padrões de Arquitetura | [system-overview](../../architecture/concepts/system-overview.md)
> **Escopo:** Backend Python/Django e Frontend React/TypeScript

---

## 1. Idioma Padrão

* **Explicações de Lógica e Negócio:** Devem ser escritas em **Português (PT-BR)**, alinhadas com as definições de regras de negócio do produto.
* **Termos Técnicos e de Bibliotecas:** Mantêm-se no idioma original em **Inglês** (ex: *QuerySet*, *OneToOne*, *middleware*, *fallback*, *payload*).

---

## 2. Docstrings de Classe e Método

### Docstrings de Classe
Devem descrever de forma concisa a responsabilidade do módulo ou classe no domínio do sistema, mencionando regras de negócio ou ADRs relevantes.

```python
class SupplierService:
    """
    Camada de serviço para gestão de fornecedores.
    Centraliza a lógica de catálogo transversal à Company (RF09).
    """
```

### Docstrings de Método — Padrão "Lean Provenance" (WHY, not WHAT)
Para métodos públicos na camada de serviço (`services/`) ou interfaces públicas (`interfaces.py`), adote o padrão **Lean Provenance Docstrings** em formato **Google Style Pragmático**.

O objetivo de uma docstring Lean Provenance é registrar a **intenção de negócio e a proveniência** (*WHY*), e não parafrasear o que o código faz (*WHAT*).

#### Fórmula Canônica de 3 a 5 Linhas:
1. **Resumo do Propósito de Negócio (1 linha):** Frase concisa declarando a intenção de negócio da operação no domínio.
2. **Regra de Negócio (Proveniência):** Declaração explícita de `Regra de Negócio:` ou `Decisão Arquitetural:` contendo link relativo para o documento de especificação em `docs/`.
3. **Efeitos Colaterais:** Seção `Efeitos Colaterais:` obrigatória sempre que houver mutação atômica (`transaction.atomic`), persistência em múltiplos agregados, agendamento de tarefas assíncronas (`django.tasks`) ou disparos no scheduler.
4. **Raises:** Seção `Raises:` obrigatória sempre que o método contiver instruções `raise` para exceções de domínio ou invariantes violadas.

#### Regras de Tipagem e Retorno:
* **Proibido Duplicar Tipos na Docstring (mypy é a SSOT):** Jamais declare tipos em `Args:` (ex: proibido `Args: foo (int):`) ou em `Returns:` (ex: proibido `Returns: bool:`). O sistema de tipagem estrita do Python 3.12 (`mypy`) é a Única Fonte da Verdade.
* **Desobrigação da Seção `Returns:`:** Quando a função já possui anotação explícita de retorno tipado na assinatura (`-> Tipo`), a seção burocrática `Returns:` é **desobrigada**. Ela só deve ser incluída se houver **semântica de estado de retorno não óbvia** (ex: retorno de tupla com flags booleanas, dicionários com chaves dinâmicas, ou retorno condicional de `None` com significado específico de negócio). Se for incluída, nunca declare o tipo do retorno.
* **Escopo Semântico de `Args:`:** Documente em `Args:` apenas parâmetros com limites numéricos, invariantes de negócio ou restrições não óbvias. Parâmetros de modelo autoexplicativos (`company`, `user`) não devem ser parafraseados. Se todos os parâmetros forem óbvios, omita a seção `Args:`.

#### Exemplo Canônico de Lean Provenance Docstring (Sem `Returns:` Burocrático):
```python
def auto_generate_installments(
    company: Company,
    expense: Expense,
    num_installments: int,
    first_due_date: date,
) -> list[Installment]:
    """
    Gera automaticamente as parcelas de uma despesa com ajuste na última parcela (Tolerância Zero).

    Regra de Negócio:
        BR-F01 (docs/architecture/business-rules/finances/financial-integrity-rules.md)

    Efeitos Colaterais:
        - Persiste as instâncias de Installment atomicamente.
        - Dispara a criação síncrona de eventos 'PAYMENT' no calendário da agenda (BR-S01).

    Raises:
        BusinessRuleViolation: Se a despesa já possuir parcelas, se o número
            de parcelas for <= 0, ou se o valor total for inválido.
    """
```

#### Exemplo com Semântica de Retorno Não Óbvia (`Returns:` descritivo sem tipos redundantes):
```python
def calculate_budget_distribution(
    company: Company,
    total_budget: Decimal,
) -> dict[str, Decimal]:
    """
    Calcula a distribuição percentual recomendada do orçamento por categoria de fornecedor.

    Regra de Negócio:
        BR-F05 (docs/architecture/business-rules/finances/budget-category-distribution.md)

    Returns:
        Mapeamento de categorias de serviço para suas respectivas cotas orçamentárias alocadas.

    Raises:
        BusinessRuleViolation: Se o orçamento total for menor ou igual a zero.
    """
```

---

## 3. Comentários Inline (Código)

* **Foco no "Porquê" (*Why*), não no "O quê" (*What*):**
  Evite descrever o que uma linha de código autoexplicativa faz. Use comentários para documentar decisões de design, restrições de banco de dados, contornos de bugs (*workarounds*) ou otimizações.
* **Marcação de Sequência:**
  Em fluxos lineares complexos (como transações atômicas com múltiplas etapas), use comentários numerados para guiar o leitor.

```python
# BOM:
# O Django não valida a senha por padrão no create_user, executamos a validação preventivamente.
validate_password(password)

# RUIM (Redundante):
# Salva o usuário no banco de dados
user.save()
```

---

## 4. Legibilidade de Código e Engenharia de Exceções

### 4.1 Mensagens de Exceção e a Regra Obrigatória do "Offending Value"
Ao lançar exceções de regra de negócio (`BusinessRuleViolation`), de validação de modelo (`ValidationError`) ou transições de estado inválidas, **é obrigatório sempre interpolar o valor recebido causador (*offending value*) e o conjunto ou formato esperado**.

Mensagens genéricas ou opacas são estritamente proibidas pois impedem a identificação imediata da causa raiz nos logs de produção e depuração.

```python
# CORRETO: Interpolação explícita do offending value e conjunto esperado
raise BusinessRuleViolation(
    f"Status '{status}' inválido para transição; esperados: {sorted(ALLOWED_TRANSITIONS)}"
)

# INCORRETO: Mensagem genérica sem o valor causador nem o conjunto esperado
raise BusinessRuleViolation("Status inválido para transição.")
```

### 4.2 Regra dos Nomes Greppáveis (< 5 matches no `rg`)
Identificadores de constantes, funções de serviço, eventos e métodos devem ser altamente específicos e semanticamente únicos.
* **Critério de Greppabilidade:** Uma busca textual exata via ripgrep (`rg <identificador>`) deve retornar idealmente **menos de 5 matches** no repositório.
* **Anti-Padrão:** Nomes genéricos como `DATA`, `HANDLER`, `STATUS`, `PROCESS`, `ITEMS` ou `MANAGER` poluem buscas globais e dificultam refatorações e rastreabilidade estática.

```python
# CORRETO: Identificador único e greppável (< 5 ocorrências no repositório)
WEDDING_CONTRACT_TERMINATION_ALLOWED_STATUSES = {"DRAFT", "PENDING_APPROVAL"}

# INCORRETO: Identificador genérico que colide com centenas de símbolos
ALLOWED_STATUSES = {"DRAFT", "PENDING_APPROVAL"}
```

### 4.3 Regra de Aninhamento Raso e Early Returns (Limite Máximo de 2 Níveis)
Mantenha a complexidade ciclomática baixa e a leitura linear adotando *Guard Clauses* (Early Returns / Early Raises) logo no início das funções.
* **Limite Máximo:** É tolerado no máximo **2 níveis de aninhamento** de estruturas de controle (`if`, `for`, `while`, `try`, `with`).
* **Refatoração Obrigatória:** Se um fluxo de execução demandar um 3º nível de aninhamento, a lógica interna deve ser imediatamente extraída para um método auxiliar privado (`_helper`) ou função utilitária pura.

```python
# CORRETO: Guard clauses e aninhamento raso (<= 2 níveis de estruturas de controle)
def process_installments(company: Company, expense: Expense) -> None:
    if not expense.is_active:
        return

    if not expense.installments.exists():
        raise BusinessRuleViolation(
            f"Despesa '{expense.id}' não possui parcelas registradas."
        )

    with transaction.atomic():
        for installment in expense.installments.all():
            installment.reconcile()

# INCORRETO: Aninhamento em pirâmide (> 2 níveis de profundidade)
def process_installments(company: Company, expense: Expense) -> None:
    if expense.is_active:
        if expense.installments.exists():
            with transaction.atomic():
                for installment in expense.installments.all():
                    if installment.can_reconcile:
                        installment.reconcile()
```

---

## 5. Restrições e Proibições

### Sem Referências a Ferramentas Externas ou IAs
É terminantemente **proibido** incluir referências a assistentes de codificação, ferramentas de geração ou termos de ambientes de terceiros nos comentários de produção.
* **Exemplos proibidos:** `# Bolt Optimization`, `# jules fix`, `# Copilot Review Fix`, `# gerado por IA`.
* **Substitutos adequados:** `# Otimização de performance: ...`, `# Correção de segurança: ...`, `# Ajuste preventivo: ...`.

### Sem Metadados Temporários
Evite incluir números de Pull Requests, nomes de branches ou nomes de desenvolvedores nos comentários. Esse histórico pertence ao Git.

---

## 6. Documentando Padrões de Arquitetura Implícitos

Quando uma classe utilizar padrões estruturais menos comuns (como Injeção de Dependência manual para desacoplar infraestrutura de storage em testes), documente claramente a finalidade do atributo e seus métodos acessores.

```python
# Injeção de dependência para desacoplar a infraestrutura de Storage.
# Permite que testes unitários injetem mocks para evitar chamadas reais à rede.
_storage_service: StorageService | None = None
```

---

## 7. Padrões por Camada da Aplicação

Cada camada arquitetural do Django Ninja possui necessidades diferentes de documentação:

| Camada | Padrão de Documentação Recomendado | Finalidade Principal |
| :--- | :--- | :--- |
| **API / Views (`api.py`)** | Docstring descritiva simples (1 a 2 linhas). Sem necessidade de `Args:` ou `Returns:`. | Alimentar automaticamente a descrição da rota na documentação gerada pelo Swagger / OpenAPI do Django Ninja. |
| **Services (`services/`)** | Docstrings **Lean Provenance** (`Regra de Negócio`, `Efeitos Colaterais`, `Raises`; `Args`/`Returns` apenas se não óbvios). | Documentar a orquestração de lógica de negócios, proveniência e efeitos colaterais sem duplicar tipagem. |
| **Models (`models.py`)** | Docstring de classe simples focada no papel da entidade. Docstrings Lean Provenance para métodos de *Manager* / *QuerySet*. | Explicar o papel do modelo no domínio de negócio e relações. |
| **Schemas (`schemas.py`)** | Sem docstrings nas classes. Apenas comentários inline quando houver resolvedores ou validadores (`@model_validator`) complexos. | Manter a camada de transporte de dados limpa (os tipos Pydantic já são autoexplicativos). |

---

## 8. Rastreabilidade Bidirecional (*Code $\leftrightarrow$ Docs*)

Para manter sincronização contínua entre o código-fonte e as especificações técnicas sem fragilidade a mudanças de linhas de código:

### 8.1 Do Código para a Documentação (*Code $\to$ Docs*)
Docstrings de métodos ou classes que implementam regras de negócio atômicas (`BR-XXX`) ou padrões arquiteturais específicos (`ADR-XXX`) devem declarar as referências no corpo da docstring Google Style:

```python
def create_contract(
    company: Company,
    payload: ContractCreateIn,
) -> Contract:
    """
    Cria um contrato e dispara a geração inicial de obrigações financeiras.

    Regra de Negócio:
        BR-L01 (docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md)
    Decisão Arquitetural:
        ADR-030 (docs/architecture/adr/030-rich-domain-model-service-layer.md)

    Args:
        company: Empresa locatária (tenant) proprietária.
        payload: Dados validados de entrada para a criação do contrato.
    ...
    """
```

> [!NOTE]
> O validador automatizado `scripts/validate_docs_links.py` inspeciona todas as docstrings do backend e falha no CI caso o caminho referenciado não exista na pasta `docs/`.

### 8.2 Da Documentação para o Código (*Docs $\to$ Code*)
As notas atômicas em `docs/` devem apontar diretamente para os símbolos semânticos e arquivos do backend/frontend utilizando links Markdown relativos, dispensando citações de números de linha que sofrem drift com facilidade:
```markdown
- **Serviço de Negócio**: [`ContractService.create_contract()`](../../backend/apps/logistics/services/contract_service.py)
- **Validador de Domínio**: [`Contract.clean()`](../../backend/apps/logistics/models/contract.py)
- **Teste de Regra**: [`test_contract_hierarchy_depth`](../../backend/apps/logistics/tests/test_services.py)
```

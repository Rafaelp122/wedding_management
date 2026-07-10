# Padrões de Comentários e Docstrings

Este documento define os padrões oficiais de comentários e documentação de código (*docstrings*) para a base de código do **Wedding Management System**.

O objetivo é garantir legibilidade de longo prazo, facilitar o onboarding de novos desenvolvedores e evitar poluição ou referências desnecessárias a ferramentas externas.

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

### Docstrings de Método (Google Style)
Para métodos públicos ou com regras de negócio complexas, use o formato **Google Style**. Ele deve incluir seções explícitas de `Args`, `Returns` e `Raises` (se aplicável).

```python
def auto_generate_installments(
    company: Company,
    expense: Expense,
    num_installments: int,
    first_due_date: date,
) -> list[Installment]:
    """
    Gera automaticamente as parcelas de uma despesa com ajuste na última
    parcela (Tolerância Zero).

    Args:
        company: O tenant atual para isolamento de dados.
        expense: A despesa pai que receberá o parcelamento.
        num_installments: Número total de parcelas (> 0).
        first_due_date: Data de vencimento da primeira parcela.

    Returns:
        Lista com as instâncias de parcelas geradas e salvas no banco.

    Raises:
        BusinessRuleViolation: Se a despesa já possuir parcelas ou valor inválido.
    """
```

---

## 3. Comentários Inline (Código)

* **Foco no "Porquê" (*Why*), não no "O quê" (*What*):**
  Evite descrever o que uma linha de código autoexplicativa faz. Use comentários para documentar decisões de design, restrições de banco de dados, contornos de bugs (*workarounds*) ou otimizações.
* **Marcação de Sequência:**
  Em fluxos lineares complexos (como transações atômicas com múltiplas etapas), use comentários numerados para guiar o leitor.

```python
# ⚠️ BOM:
# O Django não valida a senha por padrão no create_user, executamos a validação preventivamente.
validate_password(password)

# ❌ RUIM (Redundante):
# Salva o usuário no banco de dados
user.save()
```

---

## 4. Restrições e Proibições

### Sem Referências a Ferramentas Externas ou IAs
É terminantemente **proibido** incluir referências a assistentes de codificação, ferramentas de geração ou termos de ambientes de terceiros nos comentários de produção.
* **Exemplos proibidos:** `# Bolt Optimization`, `# jules fix`, `# Copilot Review Fix`, `# gerado por IA`.
* **Substitutos adequados:** `# Otimização de performance: ...`, `# Correção de segurança: ...`, `# Ajuste preventivo: ...`.

### Sem Metadados Temporários
Evite incluir números de Pull Requests, nomes de branches ou nomes de desenvolvedores nos comentários. Esse histórico pertence ao Git.

---

## 5. Documentando Padrões de Arquitetura Implícitos

Quando uma classe utilizar padrões estruturais menos comuns (como Injeção de Dependência manual para desacoplar infraestrutura de storage em testes), documente claramente a finalidade do atributo e seus métodos acessores.

```python
# Injeção de dependência para desacoplar a infraestrutura de Storage.
# Permite que testes unitários injetem mocks para evitar chamadas reais à rede.
_storage_service: StorageService | None = None
```

---

## 6. Padrões por Camada da Aplicação

Cada camada arquitetural do Django Ninja possui necessidades diferentes de documentação:

| Camada | Padrão de Documentação Recomendado | Finalidade Principal |
| :--- | :--- | :--- |
| **API / Views (`api.py`)** | Docstring descritiva simples (1 a 2 linhas). Sem necessidade de `Args:` ou `Returns:`. | Alimentar automaticamente a descrição da rota na documentação gerada pelo Swagger / OpenAPI do Django Ninja. |
| **Services (`services/`)** | Docstrings completas em estilo **Google Style** (`Args`, `Returns`, `Raises`). | Documentar a orquestração de lógica de negócios, tipos internos e fluxo de exceções. |
| **Models (`models.py`)** | Docstring de classe simples focada no papel da entidade. Docstrings Google Style apenas para métodos de *Manager* / *QuerySet*. | Explicar o papel do modelo no domínio de negócio e relações. |
| **Schemas (`schemas.py`)** | Sem docstrings nas classes. Apenas comentários inline quando houver resolvedores ou validadores (`@model_validator`) complexos. | Manter a camada de transporte de dados limpa (os tipos Pydantic já são autoexplicativos). |

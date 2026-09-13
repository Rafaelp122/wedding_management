---
title: "Regras de Validação e Sanitização de CNPJ"
domain: logistics
type: business-rule
source_code:
  - backend/apps/logistics/models/supplier.py
  - backend/apps/logistics/services/supplier_service.py
tests:
  - backend/apps/logistics/tests/suppliers/test_models.py
  - backend/apps/logistics/tests/suppliers/test_services.py
---

# Regras de Validação e Sanitização de CNPJ de Fornecedores

> **Categoria:** Regra de Negócio (Domínio Logístico)
> **Relacionados:** [Máquina de Estados de Contratos](contract-state-machine.md) · [Hierarquia de Contratos](contract-parent-child-hierarchy.md) · [Domínio de Logística](../../domains/logistics-domain.md)

---

## 1. Contexto e Invariantes do Domínio

No módulo de Logística do **Wedding Management System**, os fornecedores de produtos e serviços (espaço, buffet, fotografia, decoração, etc.) representam pessoas jurídicas com obrigações contratuais e fiscais. O identificador fiscal oficial adotado é o **CNPJ (Cadastro Nacional da Pessoa Jurídica)**.

### Invariantes Fundamentais:
1. **Formato Canônico de 18 Caracteres:** O campo CNPJ, quando informado, deve estar estritamente no padrão mascarado `XX.XXX.XXX/XXXX-XX`.
2. **Opcionalidade de Cadastro (`blank=True`):** Fornecedores autônomos ou em fase inicial de prospecção podem ser cadastrados sem CNPJ. Porém, quando preenchido, a validação estrutural é obrigatória.
3. **Isolamento Multitenant do Catálogo:** Fornecedores são entidades vinculadas à empresa assessora (`Company`). Um mesmo fornecedor cadastrado pela empresa pode ser associado a múltiplos casamentos gerenciados por ela.
4. **Validação em Duas Camadas:**
   - **Backend:** Validação estrita via `RegexValidator` no modelo `Supplier` durante o `full_clean()`.
   - **Frontend:** Validação instantânea via schema Zod (`SupplierFormSchema`) antes do envio à API.

### O Algoritmo de Módulo 11 (Cálculo dos Dígitos Verificadores):
Um CNPJ é composto por 14 dígitos decimais: $D = [d_1, d_2, \dots, d_{12}, d_{13}, d_{14}]$, onde os 12 primeiros representam a base/filial e $d_{13}, d_{14}$ são os Dígitos Verificadores ($DV_1$ e $DV_2$).

#### Cálculo do Primeiro Dígito Verificador ($DV_1$):
Com pesos $W_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]$:

$$S_1 = \sum_{i=1}^{12} d_i \cdot W_{1,i}$$

$$R_1 = S_1 \bmod 11$$

$$DV_1 = \begin{cases} 0, & \text{se } R_1 < 2 \\ 11 - R_1, & \text{se } R_1 \ge 2 \end{cases}$$

#### Cálculo do Segundo Dígito Verificador ($DV_2$):
Com pesos $W_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]$:

$$S_2 = \sum_{i=1}^{13} d_i \cdot W_{2,i} \quad (\text{incluindo } d_{13} = DV_1)$$

$$R_2 = S_2 \bmod 11$$

$$DV_2 = \begin{cases} 0, & \text{se } R_2 < 2 \\ 11 - R_2, & \text{se } R_2 \ge 2 \end{cases}$$

#### Rejeição de Máscaras Homogêneas Inválidas:
Sequências formadas por 14 dígitos repetidos (ex.: `00.000.000/0000-00`, `11.111.111/1111-11`, etc.) são consideradas matematicamente inválidas pelo algoritmo oficial da Receita Federal.

---

## 2. Diagrama de Fluxo e Validação de CNPJ

```mermaid
graph TD
    A["Início: Entrada do CNPJ"] --> B{"CNPJ informado (não vazio)?"}

    B -->|Não (blank=True)| C["Validação Aprovada (Fornecedor sem CNPJ)"]
    B -->|Sim| D{"Formato Regex XX.XXX.XXX/XXXX-XX?"}

    D -->|Não| ERR1["Raise ValidationError<br/>('CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX.')"]
    D -->|Sim| E{"Possui 18 caracteres mascarados (14 dígitos)?"}

    E -->|Não| ERR2["Raise ValidationError"]
    E -->|Sim| F["Validação Aprovada"]

    F --> G["Supplier.save() (full_clean)"]
    C --> G
    G --> H["Fornecedor Persistido com Sucesso"]
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Comportamento do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-L-CNPJ-01** | **Formato Estrutural** | CNPJ preenchido fora do padrão `XX.XXX.XXX/XXXX-XX` (ex.: dígitos puros `12345678000195` ou letras). | `ValidationError` | Bloqueia persistência e orienta a formatação correta. |
| **BR-L-CNPJ-02** | **Aceite de Campo Vazio** | Cadastro com `cnpj=""` ou `None`. | Nenhuma (Permitido) | Salva fornecedor sem identificador fiscal para agilidade de pré-cadastro. |
| **BR-L-CNPJ-03** | **Validação Frontend Antecipada** | Usuário digita CNPJ em formulário React. | Erro de validação Zod no formulário | Exibe feedback visual imediato antes da requisição HTTP à API. |
| **BR-L-CNPJ-04** | **Escopo de Tenant** | Busca ou alteração de fornecedor por CNPJ/Nome. | `for_tenant(company)` | Garante que fornecedores não vazem entre diferentes empresas do sistema. |

---

## 4. Implementação no Código-Fonte Real

### A. Validador Regex e Campo no Modelo (`supplier.py`)

```python
--8<-- "backend/apps/logistics/models/supplier.py:20:47"
```

### B. Criação de Fornecedor no Serviço (`supplier_service.py`)

```python
--8<-- "backend/apps/logistics/services/supplier_service.py:23:48"
```

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes unitários em `apps/logistics/tests/suppliers/test_models.py` e `apps/logistics/tests/suppliers/test_services.py` cobre as validações de CNPJ:

- `test_full_clean_rejects_invalid_cnpj`: Valida que CNPJ fora do formato (ex.: `"123"`) é rejeitado com `ValidationError`.
- `test_full_clean_accepts_valid_cnpj`: Valida que CNPJ no formato correto (`"00.000.000/0001-00"`) é aceito pelo `full_clean()`.
- `test_full_clean_accepts_empty_cnpj`: Valida que CNPJ vazio (`""`) é aceito (`blank=True`).
- `test_create_supplier_success`: Valida criação completa de fornecedor pelo serviço com persistência e validação.

---
title: "Regras de Validação e Sanitização de CNPJ"
domain: suppliers
type: business-rule
source_code:
  - backend/apps/suppliers/validators.py
  - backend/apps/suppliers/models.py
  - backend/apps/suppliers/schemas.py
  - backend/apps/suppliers/services.py
tests:
  - backend/apps/suppliers/tests/test_models.py
  - backend/apps/suppliers/tests/test_apis.py
---

# Regras de Validação e Sanitização de CNPJ de Fornecedores

> **Categoria:** Regra de Negócio (Domínio de Fornecedores)
> **Relacionados:** [Catálogo de Regras](../index.md) · [Domínio de Fornecedores](../../domains/suppliers-domain.md) · [Domínio de Contratos](../../domains/contracts-domain.md) · [Máquina de Estados de Contratos](contract-state-machine.md) · [Hierarquia de Contratos](contract-parent-child-hierarchy.md)

---

## 1. Contexto e Invariantes do Domínio

No módulo de Fornecedores (`apps.suppliers`) do **Wedding Management System**, os fornecedores de produtos e serviços (espaço, buffet, fotografia, decoração, etc.) representam parceiros cadastrados no catálogo corporativo do tenant (`Company`). O identificador fiscal oficial adotado é o **CNPJ (Cadastro Nacional da Pessoa Jurídica)**.

### Invariantes Fundamentais:
1. **Formato Canônico de 18 Caracteres:** O campo CNPJ, quando informado, deve estar estritamente no padrão mascarado `XX.XXX.XXX/XXXX-XX`.
2. **Opcionalidade de Cadastro (`blank=True`):** Fornecedores autônomos ou em fase inicial de prospecção podem ser cadastrados sem CNPJ. Porém, quando preenchido, a validação estrutural e algorítmica é obrigatória.
3. **Isolamento Multitenant do Catálogo:** Fornecedores são entidades vinculadas à empresa assessora (`Company`). Um mesmo fornecedor cadastrado pela empresa pode ser associado a múltiplos casamentos gerenciados por ela.
4. **Validação em Três Níveis Formais (ADR-030):**
   - **Nível 1 (Entrada / Fail-Fast):** Pydantic Schema (`SupplierIn`, `SupplierUpdateIn`) valida formato de máscara e executa `validate_cnpj_modulo11` disparando HTTP 422 imediato em entradas inválidas.
   - **Nível 2 (Invariante de Domínio):** Modelo `Supplier` aplica `validators=[validate_cnpj_modulo11]` no campo e garante integridade matemática no `clean()` via `full_clean()`.
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
    D -->|Sim| E{"Possui 14 dígitos e não é repetido?"}

    E -->|Não| ERR2["Raise ValidationError<br/>('CNPJ não pode ser composto por dígitos repetidos.')"]
    E -->|Sim| F{"Módulo 11 confere DV1 e DV2?"}

    F -->|Não| ERR3["Raise ValidationError<br/>('Dígito verificador não confere.')"]
    F -->|Sim| G["Validação Aprovada"]

    G --> H["Supplier.save() (full_clean)"]
    C --> H
    H --> I["Fornecedor Persistido com Sucesso"]
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Comportamento do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-SUP-CNPJ-01** | **Formato Estrutural** | CNPJ preenchido fora do padrão `XX.XXX.XXX/XXXX-XX` (ex.: dígitos puros `12345678000195` ou letras). | `ValidationError` | Bloqueia persistência e orienta a formatação correta. |
| **BR-SUP-CNPJ-02** | **Cálculo Módulo 11** | CNPJ com dígitos verificadores matematicamente incorretos ou repetidos. | `ValidationError` | Rejeita CNPJ inválido ou fictício (ex: `00.000.000/0001-00`). |
| **BR-SUP-CNPJ-03** | **Aceite de Campo Vazio** | Cadastro com `cnpj=""` ou `None`. | Nenhuma (Permitido) | Salva fornecedor sem identificador fiscal para agilidade de pré-cadastro. |
| **BR-SUP-CNPJ-04** | **Validação Frontend Antecipada** | Usuário digita CNPJ em formulário React. | Erro de validação Zod no formulário | Exibe feedback visual imediato antes da requisição HTTP à API. |
| **BR-SUP-CNPJ-05** | **Escopo de Tenant** | Busca ou alteração de fornecedor por CNPJ/Nome. | `for_tenant(company)` | Garante que fornecedores não vazem entre diferentes empresas do sistema. |

---

## 4. Implementação no Código-Fonte Real

- **Validador Oficial (Módulo 11):** [`validate_cnpj_modulo11`](../../../../backend/apps/suppliers/validators.py)
- **Modelo de Domínio:** [`Supplier`](../../../../backend/apps/suppliers/models.py)
- **Schema Ninja (Pydantic):** [`SupplierIn`](../../../../backend/apps/suppliers/schemas.py)
- **Serviço de Orquestração:** [`SupplierService.create()`](../../../../backend/apps/suppliers/services.py)
- **Testes de Domínio:** [`test_models.py`](../../../../backend/apps/suppliers/tests/test_models.py) e [`test_apis.py`](../../../../backend/apps/suppliers/tests/test_apis.py)

### A. Validador Canônico Módulo 11 (`validators.py`)

```python
def validate_cnpj_modulo11(value: str) -> None:
    if not value:
        return

    digits = re.sub(r"\D", "", value)
    if not digits:
        return

    if len(digits) != 14:
        raise ValidationError("CNPJ deve conter exatamente 14 dígitos numéricos.", code="invalid_cnpj_length")

    if digits == digits[0] * 14:
        raise ValidationError("CNPJ não pode ser composto por dígitos repetidos.", code="invalid_cnpj_homogeneous")

    # DV1
    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum1 = sum(int(digit) * weight for digit, weight in zip(digits[:12], weights_first))
    remainder1 = sum1 % 11
    expected_dv1 = 0 if remainder1 < 2 else 11 - remainder1
    if int(digits[12]) != expected_dv1:
        raise ValidationError("CNPJ inválido (primeiro dígito verificador não confere).", code="invalid_cnpj_dv1")

    # DV2
    weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum2 = sum(int(digit) * weight for digit, weight in zip(digits[:13], weights_second))
    remainder2 = sum2 % 11
    expected_dv2 = 0 if remainder2 < 2 else 11 - remainder2
    if int(digits[13]) != expected_dv2:
        raise ValidationError("CNPJ inválido (segundo dígito verificador não confere).", code="invalid_cnpj_dv2")
```

### B. Definição no Modelo (`models.py`)

```python
class Supplier(TenantModel):
    name = models.CharField(max_length=255, verbose_name="Nome")
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        validators=[validate_cnpj_modulo11],
        verbose_name="CNPJ",
        help_text="Formato: 00.000.000/0000-00",
    )

    def clean(self) -> None:
        super().clean()
        if self.cnpj:
            try:
                validate_cnpj_modulo11(self.cnpj)
            except ValidationError as exc:
                raise ValidationError({"cnpj": exc.messages}) from exc
```

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes unitários em `apps/suppliers/tests/test_models.py` e `apps/suppliers/tests/test_apis.py` cobre as validações de CNPJ:

- `test_full_clean_rejects_invalid_cnpj`: Valida que CNPJ fora do formato (ex.: `"123"`) é rejeitado com `ValidationError`.
- `test_full_clean_rejects_mathematically_invalid_cnpj`: Valida que CNPJ com DV incorreto (ex.: `"00.000.000/0001-00"`) é rejeitado.
- `test_full_clean_accepts_valid_cnpj`: Valida que CNPJ matematicamente válido (`"11.222.333/0001-81"`) é aceito pelo `full_clean()`.
- `test_full_clean_accepts_empty_cnpj`: Valida que CNPJ vazio (`""`) é aceito (`blank=True`).
- `test_create_supplier_invalid_cnpj_returns_422`: Valida rejeição HTTP 422 na camada de entrada da API Ninja.

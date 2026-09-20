# Regras de Negócio do Domínio de Logística — MOC

> **Categoria:** Regras de Negócio (Domínio Logístico)
> **Relacionados:** [MOC Central de Regras de Negócio](../index.md) · [Domínio de Logística](../../domains/logistics-domain.md) · [ADR-030: Rich Domain Model](../../adr/030-rich-domain-model-service-layer.md)

---

## 1. Visão Geral

O subdomínio de **Logística (`logistics`)** gerencia o relacionamento com fornecedores credenciados (`Supplier`), os contratos jurídicos formalizados e seus termos aditivos (`Contract`), bem como o catálogo e ciclo de vida de aquisição de itens e serviços do evento (`Item`). As regras de logística asseguram validade documental e fiscal, integridade em aditivos contratuais e desacoplamento entre aquisição de itens e status financeiro.

---

## 2. Índice de Notas Atômicas de Regras de Negócio

| Regra / Especificação | Código Canônico | Escopo / Responsabilidade | Entidades Envolvidas |
| :--- | :--- | :--- | :--- |
| **[Máquina de Estados de Contratos e Itens Logísticos](contract-state-machine.md)** | `BR-L01`, `BR-L03`, `BR-L04` | Ciclo de vida determinístico de contratos (`DRAFT` $\to$ `PENDING_SIGNATURE` $\to$ `SIGNED` $\to$ `CANCELED`) com exigência de PDF/valor/data para assinatura; compartilhamento multi-casamento de fornecedores e desacoplamento de entrega de itens. | `Contract`, `Item`, `Supplier` |
| **[Hierarquia Pai-Filho e Termos Aditivos de Contratos](contract-parent-child-hierarchy.md)** | `BR-L02` | Estrutura de termos aditivos (`parent`), agregação financeira em cascata (\(V_{\text{efetivo}} = V_{\text{base}} + \sum V_{\text{aditivos}}\)) e garantia de pertencimento ao mesmo casamento. | `Contract`, `Wedding` |
| **[Regras de Validação e Sanitização de CNPJ](cnpj-validation-rules.md)** | `BR-L05` | Formatação padronizada em 18 caracteres (`XX.XXX.XXX/XXXX-XX`), validação rigorosa dos dígitos verificadores pelo algoritmo módulo 11 e rejeição de sequências repetidas inválidas. | `Supplier` |

---

## 3. Matriz de Integração e Relações Cruzadas

- **Com o Módulo de Finanças:** Contratos com status `SIGNED` podem ser vinculados a despesas em `finances`, exigindo paridade monetária idêntica. Veja [Regras de Integridade Financeira](../finances/financial-integrity-rules.md).
- **Com o Armazenamento Cloudflare R2:** Upload e download de arquivos PDF de contratos assinados utilizam URLs pré-assinadas com custo zero de egresso. Veja [Fluxo de Upload de Contratos no R2](../../concepts/contract-pdf-upload-r2-flow.md).

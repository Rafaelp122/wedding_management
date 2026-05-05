# 📐 Regras de Negócio - Wedding Management System

Este documento centraliza as regras que regem o comportamento do sistema. Estas regras são agnósticas de tecnologia e focam na integridade dos dados e processos de negócio.

---

## 1. Domínio: Casamentos (Weddings)

### **BR-W01: Status de Conclusão**
- **Regra:** Um casamento só pode ser marcado como **CONCLUÍDO** após a data real do evento ter passado.
- **Objetivo:** Prevenir o fechamento acidental de casamentos ainda em andamento.

### **BR-W02: Isolamento de Dados (Multi-tenancy)**
- **Regra:** O acesso aos casamentos e demais dados é isolado por empresa (`company`/tenant). Usuários da mesma empresa compartilham os dados do seu tenant, enquanto usuários de empresas diferentes não podem acessar os dados entre si.
- **Objetivo:** Garantir a privacidade e segurança dos dados entre diferentes empresas/clientes (LGPD), respeitando o compartilhamento interno dentro do mesmo tenant.

---

## 2. Domínio: Financeiro (Finances)

### **BR-F01: Integridade de Parcelas (Tolerância Zero)**
- **Regra:** A soma exata de todas as parcelas (`Installments`) deve ser rigorosamente igual ao valor total da despesa (`Expense`).
- **Funcionamento:** Caso a divisão do valor total pelo número de parcelas gere dízimas, o sistema deve ajustar automaticamente a **última parcela** para absorver a diferença de centavos.

**Fórmula de Cálculo:**
Sendo `V` o valor total e `n` o número de parcelas:
- Valor base: `vb = V ÷ n`, arredondado para 2 casas decimais
- Primeiras `n−1` parcelas: `vb`
- Última parcela: `V − (vb × (n−1))` — absorve o arredondamento

**Exemplo:** R$ 10.000 ÷ 3 parcelas → vb = 3.333,33 → Parcela 1: 3.333,33, Parcela 2: 3.333,33, Parcela 3: 3.333,34. Soma = 10.000,00 ✅
- **Objetivo:** Garantir precisão absoluta para auditoria contábil e conciliação bancária.
- **Referência:** Veja [ADR-010 (Tolerância Zero)](ADR/010-tolerance-zero.md) para detalhes técnicos.

### **BR-F02: Âncora Jurídica (Documento ↔ Despesa)**
- **Regra:** Quando uma despesa é vinculada a um documento de referência (ex: contrato), o valor da despesa deve ser idêntico ao valor total registrado no documento.
- **Objetivo:** Manter a consistência entre o compromisso firmado e a execução financeira.

### **BR-F03: Consistência de Pagamentos**
- **Regra:** Toda parcela marcada como **PAGA** deve obrigatoriamente registrar a data em que o pagamento ocorreu. Inversamente, parcelas com data de pagamento preenchida devem estar no status **PAGO**.

### **BR-F04: Monitoramento de Orçamento**
- **Regra:** O sistema deve alertar o cerimonialista caso a soma das despesas de uma categoria exceda o orçamento alocado originalmente para ela.
- **Nota:** Esta é uma regra de aviso (soft warning) e não bloqueia a operação.

### **BR-F05: Transições de Status de Parcelas**
- **Regra:** O ciclo de vida de uma parcela segue o fluxo **PENDENTE → PAGO** (quando quitada) ou **PENDENTE → VENCIDA** (quando a data de vencimento passa sem pagamento).
- **Condições:**
  - PENDENTE → PAGO: exige registro obrigatório da data de pagamento.
  - PENDENTE → VENCIDA: ocorre automaticamente quando `due_date < hoje` e status ainda é PENDENTE.
  - VENCIDA → PAGO: permitido (pagamento em atraso), registra data de pagamento.
- **Objetivo:** Rastreabilidade completa do ciclo financeiro para auditoria e conciliação.

### **BR-F06: Imutabilidade de Parcelas Pagas**
- **Regra:** Parcelas com status **PAGO** não podem ter seu valor, data de vencimento ou número alterados após serem marcadas como pagas.
- **Objetivo:** Garantir integridade contábil e rastreabilidade de auditoria. Qualquer ajuste deve ser feito via estorno e nova parcela.

### **BR-F07: Parcelamento Obrigatório**
- **Regra:** Toda despesa deve ter no mínimo 1 (uma) parcela. O sistema gera automaticamente 1 parcela caso o número não seja informado na criação.
- **Valor padrão:** `num_installments = 1`, `first_due_date = data atual`.
- **Objetivo:** Garantir que toda despesa tenha ao menos um vencimento registrado, eliminando o conceito de "à vista sem controle".

### **BR-F08: Redistribuição de Parcelas**
- **Regra:** O número de parcelas de uma despesa pode ser alterado (remanejado) apenas se **nenhuma** parcela estiver marcada como paga (`PAID`). Se houver parcelas pagas, o remanejamento é bloqueado.
- **Funcionamento:** O sistema deleta todas as parcelas existentes e as regera com o novo número informado, recalculando a Tolerância Zero (BR-F01). Tudo em uma transação atômica.
- **Objetivo:** Permitir correção de planejamento sem comprometer a integridade de pagamentos já confirmados.

### **BR-F09: Status Composto da Despesa**
- **Regra:** O status de uma despesa é derivado automaticamente do estado de suas parcelas:
  - `PENDING` (Pendente): nenhuma parcela marcada como paga.
  - `PARTIALLY_PAID` (Parcial): ao menos uma parcela paga, mas não todas.
  - `SETTLED` (Quitada): todas as parcelas marcadas como pagas.
- **Cálculo:** O status é computado em tempo real via annotation no banco (não é persistido), garantindo consistência com o estado real das parcelas.
- **Objetivo:** Fornecer visibilidade consolidada sem risco de divergência entre o status persistido e o estado real.

### **BR-F11: Desmarcação de Parcela Paga**
- **Regra:** Parcelas marcadas como pagas podem ser desmarcadas (revertidas). Ao desmarcar:
  - `paid_date` é limpo (null)
  - Se `due_date < hoje` → status volta para `OVERDUE`
  - Caso contrário → status volta para `PENDING`
- **Objetivo:** Permitir correção de marcação acidental sem perder rastreabilidade contábil.

---

### **BR-F10: Identificação da Despesa**
- **Regra:** Toda despesa requer um **nome** (`name`) obrigatório. O campo **descrição** (`description`) é opcional e serve para detalhamento adicional.
- **Motivo:** Separar identificação curta (nome) do detalhamento (descrição), evitando sobrecarga semântica de um campo único.
- **Objetivo:** Melhorar a legibilidade nas listagens e tabelas, onde o nome aparece como identificador principal.

---

## 3. Domínio: Logística (Logistics)

### **BR-L01: Requisitos de Documentos Assinados**
- **Regra:** Documentos marcados como **ASSINADOS** exigem obrigatoriamente:
  1. Upload do arquivo (PDF).
  2. Valor total maior que zero.
  3. Registro da data de assinatura.

### **BR-L02: Isolamento de Orçamento**
- **Regra:** Itens de logística e categorias de orçamento não podem ser compartilhados entre casamentos diferentes, mesmo que pertençam ao mesmo cerimonialista.
- **Validação Cross-Wedding:** Toda operação que envolve `BudgetCategory` deve validar que a categoria pertence ao mesmo `wedding` da entidade relacionada (Expense, Item, etc.). O sistema deve rejeitar operações que tentem usar uma categoria de um casamento em outro.

### **BR-L03: Compartilhamento de Fornecedores**
- **Regra:** O cadastro de um fornecedor é vinculado ao cerimonialista e pode ser reutilizado em múltiplos casamentos.

### **BR-L04: Desacoplamento de Aquisição e Pagamento**
- **Regra:** O status de entrega/aquisição de um item é independente do seu estado de pagamento. Um item pode ser marcado como entregue mesmo se houver parcelas financeiras pendentes.

---

## 4. Domínio: Cronograma (Scheduler)

### **BR-S01: Automatização de Eventos Financeiros**
- **Regra:** Eventos de calendário do tipo **PAGAMENTO** são gerados automaticamente a partir das parcelas financeiras e não podem ser editados manualmente no calendário (apenas através do módulo financeiro).
- **Objetivo:** Garantir que o cronograma reflita fielmente o fluxo de caixa planejado.

### **BR-S02: Lembretes de Vencimento**
- **Regra:** O sistema deve gerar alertas automáticos para parcelas que atingirem a data de vencimento sem registro de pagamento (Status: **OVERDUE**).

---

## 5. Domínio: Validação de Dados (Regras Transversais)

### **BR-VAL01: Decimal para Valores Monetários**
- **Regra:** Todo valor monetário no sistema DEVE usar precisão decimal fixa (2 casas decimais). É proibido usar ponto flutuante (`float`) para dinheiro.
- **Motivo:** Ponto flutuante tem precisão binária limitada e pode gerar erros de arredondamento (ex: `0.1 + 0.2 = 0.30000000000000004`).
- **Objetivo:** Garantir exatidão em cálculos financeiros e conciliação bancária.

### **BR-VAL02: Datas de Vencimento no Futuro**
- **Regra:** Ao criar uma parcela ou evento, a data de vencimento NÃO pode estar no passado.
- **Exceção:** Permitido ao editar registros existentes para correção de dados históricos.

---

## 6. Glossário de Negócio

| Termo | Definição |
| :--- | :--- |
| **Tolerância Zero** | Princípio de que nem um centavo pode ser perdido em arredondamentos de parcelas. |
| **Cross-Wedding** | Mistura acidental de dados entre casamentos diferentes — prevenido via validação. |
| **Planner** | O cerimonialista ou empresa que utiliza o sistema. |
| **Tenant** | A entidade que isola os dados de uma empresa de outras no banco de dados. |
| **OVERDUE** | Status de parcela vencida (data de vencimento anterior à data atual sem pagamento). |

---

**Última atualização:** 4 de maio de 2026
**Responsável:** Rafael
**Versão:** 3.1 (Adicionadas BR-F07 a BR-F10 do Sprint 1)

# 📐 Regras de Negócio - Wedding Management System

## Versão 3.0 (SaaS B2B)

---

## 1. Introdução

Este documento centraliza as **Regras de Negócio (Business Rules)** do sistema. No modelo B2B, as regras garantem a integridade tanto no nível da agência (**Company**) quanto no nível do projeto (**Event**).

---

## 2. Domínio: Core & Tenancy

### **BR-SEC01: Isolamento de Agência (B2B)**
**Regra:** Um usuário só pode acessar dados (Eventos, Fornecedores, Clientes) pertencentes à sua `Company`.
**Implementação:** Filtro mandatório em nível de Manager: `queryset.filter(company=user.company)`.

### **BR-SEC02: Tenant Silencioso**
**Regra:** Todo novo usuário deve ter uma `Company` criada automaticamente no momento do cadastro.
**Motivo:** Evitar migrações complexas no futuro quando a agência crescer.

---

## 3. Domínio: Events (Eventos)

### **BR-EV01: Status de Conclusão**
**Regra:** Um evento só pode ser marcado como `COMPLETED` se a data do evento já passou.

### **BR-EV02: Detalhamento Polimórfico**
**Regra:** Ao criar um evento do tipo `WEDDING`, o sistema deve garantir a existência de um registro em `WeddingDetail`.

---

## 4. Domínio: Finances (Finanças)

### **BR-F01: Integridade de Parcelas (Tolerância Zero)**
**Regra:** A soma das parcelas deve ser EXATAMENTE igual ao valor total da despesa.
**Fórmula:** A última parcela absorve os resíduos de arredondamento.

### **BR-F02: Âncora Jurídica (Contract ↔ Expense)**
**Regra:** Uma `Expense` vinculada a um `Contract` deve ter o valor idêntico ao valor de face do contrato.

### **BR-F03: Consistência de Pagamento**
**Regra:** Status `PAID` exige `paid_date` preenchida, e vice-versa.

---

## 5. Domínio: Logistics (Logística)

### **BR-L01: Contrato Assinado**
**Regra:** Um contrato `SIGNED` exige: arquivo PDF anexado, valor total > 0 e data de assinatura.

### **BR-L02: Fornecedor Compartilhado**
**Regra:** Um `Supplier` pertence à agência (`Company`), permitindo seu reuso em múltiplos eventos da mesma empresa.

---

## 6. Domínio: Scheduler (Agenda)

### **BR-S01: Compromissos de Pagamento**
**Regra:** Compromissos (`Appointment`) do tipo `PAYMENT` são espelhos automáticos das parcelas financeiras e não podem ser editados manualmente via agenda.

---

## 10. Glossário de Termos

| Termo | Definição |
|---|---|
| **Company** | Agência contratante do software (Tenant Primário). |
| **Event** | Projeto gerenciado (Tenant Secundário). |
| **Tolerância Zero** | Soma de parcelas = valor total (sem margem de erro). |
| **Âncora Jurídica** | Vinculação obrigatória entre valor contratual e financeiro. |

---

**Última atualização:** Abril 2026
**Responsável:** Rafael

# 🎯 Levantamento de Requisitos - Wedding Management System

Este documento detalha os requisitos funcionais e não funcionais do sistema, servindo como o contrato de escopo para o desenvolvimento.

---

## 1. Visão Geral e Proposta de Valor
O sistema visa eliminar a fragmentação de dados e erros de cálculo em cerimonias de casamento, garantindo integridade financeira e logística centralizada.

---

## 2. Requisitos Funcionais (RF)

### 2.1 Módulo Core & Multitenancy
- **RF01 (Isolamento de Dados):** O sistema deve garantir que o usuário acesse apenas os casamentos e dados pertencentes à sua empresa (tenant), impedindo o acesso a dados de outras empresas.
- **RF02 (Gestão de Casamentos):** O sistema deve permitir o CRUD de casamentos, com data, nomes dos noivos e status.

### 2.2 Módulo Financeiro
- **RF03 (Categorias de Orçamento):** O sistema deve permitir organizar gastos em categorias customizáveis com valores orçados.
- **RF04 (Gestão de Despesas):** O sistema deve registrar despesas com nome obrigatório, descrição opcional, vinculadas a categorias e contratos.
- **RF05 (Parcelamento Inteligente):** O sistema deve gerar parcelas automaticamente (mínimo 1), aplicando a regra de **Tolerância Zero** (ajuste de centavos na última parcela).
- **RF06 (Controle de Pagamentos):** O sistema deve permitir marcar parcelas como pagas, remanejar parcelas (se nenhuma paga), e monitorar parcelas vencidas (**OVERDUE**). O status da despesa é derivado automaticamente: `PENDING` → `PARTIALLY_PAID` → `SETTLED`.
- **RF12 (Remanejamento de Parcelas):** O sistema deve permitir alterar o número de parcelas de uma despesa (redistribuição), desde que nenhuma parcela esteja marcada como paga.

### 2.3 Módulo Logístico
- **RF07 (Gestão de Fornecedores):** O sistema deve manter um cadastro de fornecedores reaproveitável entre diferentes casamentos.
- **RF08 (Itens e Serviços):** O sistema deve gerenciar itens contratados, vinculando-os ao orçamento e status de entrega.
- **RF09 (Documentação de Referência):** O sistema deve permitir o upload e controle de status de documentos (ex: contratos assinados).

### 2.4 Cronograma e Notificações
- **RF10 (Calendário de Eventos):** O sistema deve gerar eventos automáticos para vencimentos de parcelas.
- **RF11 (Sistema de Alertas):** O sistema deve notificar o cerimonialista sobre parcelas vencidas e prazos críticos.

---

## 3. Requisitos Não Funcionais (RNF)

| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| **RNF01** | **Performance** | API deve responder em < 200ms (P50). Dashboard deve carregar em < 500ms. |
| **RNF02** | **Segurança** | Autenticação via JWT Stateless. Rate limiting por IP. Isolamento multitenant rigoroso. |
| **RNF03** | **Disponibilidade** | Escala automática via Cloud Run. Backups diários com retenção de 7 dias. |
| **RNF04** | **Usabilidade** | Interface responsiva (Mobile-First) e acessível. |
| **RNF05** | **Auditoria** | Chaves híbridas (UUID público / BigInt interno) e timestamps em todos os registros. |

---

## 4. Roadmap e Priorização (MoSCoW)

### Must Have (MVP)
- CRUD de Casamentos, Fornecedores e Categorias.
- Lançamento de Despesas com Parcelamento Automático.
- Dashboard financeiro básico.

### Should Have (V1.1)
- Upload de documentos (PDF) via R2.
- Alertas de vencimento por e-mail.
- Exportação iCal para calendários externos.

### Could Have (V2.0)
- Importação de planilhas Excel.
- Integração com WhatsApp para alertas automáticos.

---

## 5. Referências e Detalhamentos
- **Fluxos de Tela:** Consulte os **[Casos de Uso (docs/use-cases/index.md)](use-cases/index.md)** para o passo a passo de cada RF.
- **Regras de Validação:** Consulte as **[Regras de Negócio (docs/BUSINESS_RULES.md)](BUSINESS_RULES.md)**.
- **Decisões Técnicas:** Veja os **[ADRs](ARCHITECTURE.md#9-referências)**.

---

**Última atualização:** 4 de maio de 2026
**Versão:** 7.1 (RF04/RF05/RF06 atualizados + RF12 adicionado — Sprint 1)

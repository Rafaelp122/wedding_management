# 🎯 Levantamento de Requisitos - Wedding Management System

## Versão 7.0 - SaaS B2B para Agências de Eventos

---

## 1. Visão Geral: Controle de Agência

### O Problema
Agências de eventos sofrem com a dispersão de dados entre planilhas, WhatsApp e e-mails, resultando em:
- 💸 Juros por atrasos financeiros.
- ❌ Erros de cálculo em parcelamentos complexos.
- 🔒 Falta de isolamento e segurança de dados entre clientes.

### A Solução
Uma plataforma centralizada que garante a **Integridade Financeira** e o **Isolamento B2B**, permitindo que uma agência gerencie múltiplos casamentos, aniversários e eventos corporativos com precisão matemática.

---

## 2. Domínios de Negócio

| Domínio | Responsabilidade |
|---|---|
| **Tenancy** | Isolamento por Agência (`Company`) e Usuários. |
| **Events** | Gestão polimórfica de projetos (Casamentos e outros). |
| **Finances** | Orçamento com tolerância zero, parcelamento e fluxo de caixa. |
| **Logistics** | Gestão de Fornecedores (`Suppliers`) e Contratos Jurídicos. |
| **Scheduler** | Agenda de compromissos (`Appointments`) e alertas. |

---

## 3. Requisitos Funcionais (RF)

### 🎯 Módulo de Tenancy (B2B)
- **RF01:** Isolamento total de dados entre diferentes agências.
- **RF02:** Cadastro automático de agência no primeiro acesso (Tenant Silencioso).

### 📅 Módulo de Eventos
- **RF03:** Suporte a múltiplos tipos de eventos (Casamento como padrão inicial).
- **RF04:** Detalhamento específico por tipo de evento (ex: nomes de noivos em casamentos).

### 💰 Módulo Financeiro
- **RF05:** Categorias de orçamento dinâmicas e isoladas por evento.
- **RF06:** Cálculo de parcelas com ajuste automático (Tolerância Zero).
- **RF07:** Sincronização obrigatória entre valor de contrato e despesa financeira.

### 🤝 Módulo Logístico e Jurídico
- **RF08:** Banco de fornecedores centralizado por agência.
- **RF09:** Gestão de contratos com upload de PDF e controle de status de assinatura.
- **RF10:** Upload seguro via Presigned URLs (direto para o storage).

---

## 4. Requisitos Não Funcionais (RNF)

- **RNF01:** Segurança JWT para autenticação de usuários.
- **RNF02:** Integridade Semântica (Service Layer isolada).
- **RNF03:** Alta performance em queries multitenant (Denormalização estratégica).
- **RNF04:** Documentação de API automática via OpenAPI/Swagger.

---

## 5. Roadmap e Métricas

### Sucesso do MVP
1. ✅ **Adoção:** 5 agências operando por 30 dias.
2. ✅ **Eficiência:** Redução de 50% no tempo de conciliação financeira.
3. ✅ **Qualidade:** Zero perda de dados e cobertura de testes > 75%.

---

**Referências:**
- Para detalhes de implementação: **[ARCHITECTURE.md](ARCHITECTURE.md)**
- Para regras de validação: **[BUSINESS_RULES.md](BUSINESS_RULES.md)**

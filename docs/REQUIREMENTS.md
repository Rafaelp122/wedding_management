# 🎯 Levantamento de Requisitos - Wedding Management System

## Versão 6.0 - Sistema de Controle Financeiro e Logístico

---

## 1. Visão Geral: Sistema de Controle (não apenas Gestão)

### Problema Real

Cerimonialistas perdem **4-6 horas/semana** procurando informações espalhadas e sofrem com:

- 📱 Dados fragmentados (WhatsApp, Excel, e-mail, papel)
- 💸 Juros por atrasos não monitorados
- ❌ Erros de digitação em valores financeiros
- 🔢 Soma de parcelas incorreta (arredondamentos manuais)

### Solução: Controle Máximo

Sistema que **garante integridade financeira** e **impede erro humano** através de:

- ⚖️ Validação financeira com tolerância zero
- 🤖 Auto-geração de parcelas com ajuste automático
- 📊 Pipeline de importação inteligente (Excel → Sistema)
- 🔒 Isolamento rigoroso de dados (Multitenancy denormalizado)

### Proposta de Valor

> "Sistema que não apenas guarda seus dados, mas **garante que eles estejam matematicamente corretos e financeiramente seguros**."

---

## 2. Arquitetura de Domínios de Negócio

```
backend/apps/
├── core/           # Infraestrutura (BaseModel, Mixins, Managers)
├── users/          # Autenticação JWT (Planner único no MVP)
├── weddings/       # 💒 Entidade raiz (Wedding)
├── finances/       # 💰 Domínio Financeiro
│   ├── Budget, BudgetCategory
│   ├── Expense (âncora financeira)
│   └── Installment (parcelas)
├── logistics/      # 🤝 Domínio Logístico + Jurídico
│   ├── Supplier (fornecedores)
│   ├── Item (itens/serviços)
│   └── Contract (contratos com valor de face)
└── scheduler/      # 📅 Domínio de Cronograma
    ├── Event (calendário)
    └── Notification (alertas)
```

### Separação de Responsabilidades

| Domínio       | Responsabilidade          | Pergunta que Responde                |
| ------------- | ------------------------- | ------------------------------------ |
| **weddings**  | Orquestração cross-domain | "Qual a visão geral do casamento X?" |
| **finances**  | Orçamento e integridade   | "Os números estão corretos?"         |
| **logistics** | Relacionamento B2B        | "O que contratei e quando pagar?"    |
| **scheduler** | Calendário profissional   | "O que tenho pra fazer essa semana?" |

---

## 3. Regras de Negócio (Business Rules)

As regras de negócio do sistema estão **consolidadas** em [BUSINESS_RULES.md](BUSINESS_RULES.md).

**Principais regras implementadas:**

- **BR-F01:** Invariante Financeira (tolerância zero na soma de parcelas)
- **BR-F02:** Âncora Jurídica (Contract ↔ Expense com validação de valores)
- **BR-F03:** Consistência de Status de Pagamento
- **BR-F04:** Orçamento por Categoria (saúde financeira)
- **BR-L03:** Auto-geração de Parcelas com cálculo exato
- **BR-L05:** Status de Aquisição independente de pagamento
- **BR-SEC01:** Isolamento Multitenant com cross-check
- **BR-SEC03:** Validação Cross-Wedding em Categorias
- **BR-FUT01:** Imutabilidade de Parcelas Pagas (pendente V2.0)
- **BR-FUT05:** Automação OVERDUE com OIDC (pendente V2.0)

👉 **Para detalhes completos, implementação e exemplos:** [BUSINESS_RULES.md](BUSINESS_RULES.md)

---

## 4. Requisitos Funcionais

### 🎯 Módulo de Multitenancy

#### RF01: Isolamento Rigoroso de Dados ✅ **IMPLEMENTADO**

Planner só acessa dados de sua empresa. Implementado via `TenantModel` (app Tenants) e `WeddingOwnedMixin`. Ver BR-SEC01 e BR-SEC03 em [BUSINESS_RULES.md](BUSINESS_RULES.md).

---

#### RF02: Gestão de Permissões (2 Níveis)

- **Owner (Planner):** CRUD total
- **Viewer (Noivos - V2.0):** Read-Only

Tentativa de acesso cross-wedding retorna HTTP 404.

---

### 💰 Módulo Financeiro

#### RF03: Categorias Dinâmicas ✅ **IMPLEMENTADO**

Planners criam categorias customizadas via `BudgetCategory`. Deleção de categorias é gerenciada pela Service Layer.

---

#### RF04: Validação Financeira Automática ✅ **IMPLEMENTADO**

Sistema valida:

1. Soma parcelas = Expense.actual_amount (tolerância zero)
2. Expense vinculada = Contract.total_amount
3. Categoria pertence ao mesmo wedding

Ver BR-F01, BR-F02, BR-SEC03 em [BUSINESS_RULES.md](BUSINESS_RULES.md).

---

#### RF05: Automação de Inadimplência (OVERDUE) 📋 **PENDENTE**

Task diária (Cloud Scheduler + OIDC) atualiza parcelas vencidas para status OVERDUE e envia alertas. Ver BR-FUT05 em [BUSINESS_RULES.md](BUSINESS_RULES.md).

---

#### RF06: Dashboard de Saúde Financeira

Visão em tempo real por categoria:

- **Orçado:** BudgetCategory.allocated_budget
- **Comprometido:** Soma de Contracts (SIGNED)
- **Realizado:** Soma de Installments (PAID)
- **Status:** OK (≤ orçado) ou OVER (> orçado)

Performance: < 500ms. Exportável para PDF (V1.1).

---

### 🤝 Módulo Logístico

#### RF07: Integração Financeiro-Logístico ✅ **IMPLEMENTADO**

Items vinculados a categorias de orçamento via `budget_category`. Validação cross-wedding implementada. Ver BR-SEC03 em [BUSINESS_RULES.md](BUSINESS_RULES.md).

Cadeia: Wedding → Budget → BudgetCategory ← Expense ← Contract ← Item ← Supplier

---

#### RF08: Gestão de Status de Itens ✅ **IMPLEMENTADO**

Status de aquisição independente do financeiro: `PENDING` → `IN_PROGRESS` → `DONE`. Ver BR-L05 em [BUSINESS_RULES.md](BUSINESS_RULES.md).

---

#### RF09: Notas Internas de Fornecedores ✅ **IMPLEMENTADO**

Campo texto livre (`Supplier.notes`) para anotações como "Atende apenas SP capital", "Requer 50% sinal".

---

#### RF10: Pipeline de Importação Inteligente (Excel → Sistema) 📋 **V2.0**

**Descrição:** Mapper dinâmico para importação em lote de planilhas.

**Fluxo:**

1. Upload de `.xlsx` → Detecção automática de colunas
2. Interface de mapeamento: "Fornecedor" → `supplier`, "Valor" → `amount`
3. Preview com validação de dados
4. Confirmação → Criação em lote

**Tecnologias:** `openpyxl`/`pandas` (backend) + React Table (frontend)

**Complexidade:** 2-3 semanas

**Status:** 📋 Planejado para V2.0

---

### 📄 Módulo Jurídico (Contratos)

#### RF11: Upload via Presigned URLs (Cloudflare R2)

**Descrição:** Upload direto de PDFs ao R2 sem passar pelo backend.

**Fluxo:**

1. Frontend solicita presigned URL ao backend
2. Backend gera URL temporária (15min) no R2
3. Frontend faz PUT direto ao R2
4. Frontend confirma upload ao backend

**Vantagens:**

- ✅ Backend gasta ~50ms (não 5s processando upload)
- ✅ Uploads simultâneos não sobrecarregam Cloud Run
- ✅ Escalável (100+ uploads paralelos sem problemas)

**Critérios de Aceitação:**

- ✅ Suporta PDFs até 50MB
- ✅ URL expira em 15 minutos
- ✅ Frontend mostra progresso do upload
- ✅ Validação de tipo MIME no backend

---

#### RF12: Metadados Contratuais ✅ **IMPLEMENTADO**

Contratos armazenam: `total_amount` (âncora financeira), `expiration_date`, `status`, `pdf_file`, `signed_date`. Ver BR-F02 em [BUSINESS_RULES.md](BUSINESS_RULES.md).

---

#### RF13: Controle de Assinatura Simplificado ✅ **IMPLEMENTADO**

Fluxo: Upload PDF (presigned URL) → Validação → Marcar SIGNED. Assinatura digital (DocuSign) em V2.0.

---

#### RF14: Alertas de Vencimento Contratual 📋 **V1.1**

E-mails automáticos para contratos vencendo em ≤ 30 dias ou PENDING há > 15 dias.

---

### 📅 Módulo de Cronograma

#### RF15: Exportação .ics (iCal)

Sincronização unidirecional (read-only) com Google/Outlook/Apple Calendar. URL única (UUID), atualização 1h. Formato: iCalendar (RFC 5545).

---

#### RF16: Notificações Estratificadas

| Canal                   | Casos de Uso            | Custo         |
| ----------------------- | ----------------------- | ------------- |
| **E-mail (Resend)**     | Alertas críticos        | R$ 0 (3k/mês) |
| **In-App (Badge)**      | Lembretes suaves        | R$ 0          |
| **WhatsApp Quick Link** | Cobrança manual (wa.me) | R$ 0          |
| **WhatsApp API (V2.0)** | Automação premium       | R$ 0,10/msg   |

**E-mail (MVP):** Parcelas vencendo em 24h, contratos expirando, relatório semanal.

**In-App (MVP):** Badge com contador, refresh manual (sem polling automático).

**WhatsApp Quick Link (MVP):** Frontend gera link `wa.me` com mensagem pré-preenchida.

**WhatsApp API (V2.0):** Automação via Twilio/MessageBird (custo/benefício após validação de mercado).

---

);

```

**Vantagens:**

- ✅ Zero custo (usa WhatsApp pessoal do planner)
- ✅ 1 clique para enviar
- ✅ Open rate ~90% (vs 20% e-mail)

**WhatsApp API Premium (V2.0):**

- Envio automático via Meta Business API
- Custo: R$ 0,10/msg + R$ 300/mês plano
- Apenas para planners no plano pago

**Status:**

- E-mail: Implementável em 1 sprint
- WhatsApp Quick Link: Implementável em 2 dias
- WhatsApp API: V2.0 (após validação de mercado)

---

## 5. Requisitos Não Funcionais

### RNF01: Arquitetura Headless ✅ **IMPLEMENTADO**

**Stack:** Django DRF (Cloud Run) + React (Vercel) + Neon PostgreSQL + Cloudflare R2 + Resend

**Vantagens:** Frontend/Backend independentes, múltiplos clientes (Web, Mobile, API), deploy separado.

---

### RNF02: Segurança e Autenticação ✅ **IMPLEMENTADO**

**JWT Stateless:** Access (24h) + Refresh (7d) com rotação automática
**Rate Limiting:** 100 req/min por IP
**HTTPS:** TLS automático (Cloud Run + Vercel)
**OIDC:** Service-to-service para Cloud Scheduler (zero secrets)

Ver BR-FUT05 em [BUSINESS_RULES.md](BUSINESS_RULES.md).

---

### RNF03: Service Layer Pattern ✅ **IMPLEMENTADO**

**Camadas:** Views (HTTP) → Serializers (I/O) → Services (lógica) → Models (integridade)

**Vantagens:** Testável, reutilizável, manutenível.

---

### RNF04: Deleção de Registros

> Soft delete foi removido do projeto. Deleções são gerenciadas pela Service Layer (hard delete com validações).

---

### RNF05: Chaves Híbridas ✅ **IMPLEMENTADO**

**Interno:** `BigAutoField` (JOINs rápidos)
**Público:** `UUIDField` com UUID v4 (segurança + merges)

---

### RNF06: Performance

**Metas:** GET < 200ms, Dashboard < 500ms, Batch < 5s (100 items)

**Estratégias:** Paginação (50/página), índices, `select_related()`, detector N+1 no CI

---

### RNF07: Documentação OpenAPI 3.0 ✅ **IMPLEMENTADO**

`/api/docs/` (Swagger UI) + `/api/redoc/` (ReDoc) + `/api/schema/` (JSON)

---

### RNF08: Mobile-First ✅ **DESIGN RESPONSIVO**

Tailwind CSS, breakpoints 320px/768px/1024px, botões ≥ 44px.

---

### RNF09: Continuidade de Negócio

**Backups:**

- **Neon PostgreSQL:** Backups diários automáticos (free tier)
- **Retenção:** 7 dias
- **Testes de restauração:** Trimestrais

**RTO/RPO:**

- **RTO:** < 8h | **RPO:** < 24h
- **Logs:** Cloud Run (30d retenção) + structured logging (JSON)

---

### RNF10: Observabilidade

**Erros:** Sentry (5k eventos/mês free) + Source maps + Slack alerts
**Logs:** Structured (JSON) com context (wedding_id, amount, etc)
**Métricas:** Cloud Run nativo (req/s, latency, memory)

**SEM (até 500+ usuários):** Prometheus/Grafana, APM, distributed tracing

---

## 6. Cobertura de Testes

| Camada                       | Cobertura | Justificativa           |
| ---------------------------- | --------- | ----------------------- |
| **Service Layer Financeira** | **100%**  | Cálculos críticos       |
| **Multitenancy (Filtros)**   | **100%**  | Isolamento (LGPD)       |
| **Models (Validações)**      | **80%**   | Integridade             |
| **Serializers/Views**        | **60%**   | Casos críticos          |
| **Global**                   | **≥ 75%** | Meta CI + detector N+1  |

---

## 7. Premissas e Restrições

### Infraestrutura

**Stack:** Django + DRF, PostgreSQL (Neon), React + Vite, Cloud Run + Vercel

**Custo:** R$ 0/mês (free tiers). Detalhes em [ARCHITECTURE.md](#) (a ser criado).

---

### Restrições

**R01 - Timeline:** MVP: 4 meses | V1.1: +2 meses | V2.0: +3 meses

**R02 - Idioma:** MVP: pt-BR | V2.0: i18n (en, es)

**R03 - Integrações:** Fora do MVP: Stripe, DocuSign

---

## 8. Roadmap (MoSCoW)

### Must Have (MVP - 4 meses)

**Sprint 1-4:** Models + Mixins + Validações + Testes (100% coverage financeiro)

**Sprint 5-8:** Serializers + ViewSets + Service Layer + Testes (100% coverage services)

**Sprint 9-12 (Features Críticas):**
Dashboard saúde financeira + Upload presigned URLs + Validações cross-wedding + Alertas e-mail

**Sprint 13-16 (Frontend + Deploy):**
Dashboard React + Formulários + Tabelas + Deploy Cloud Run/Vercel + Testes E2E (Cypress)

---

### Should Have (V1.1 - +2 meses)

- RF05: Automação OVERDUE (Cloud Scheduler + OIDC)
- RF15: Exportação .ics
- RF16: WhatsApp Quick Link
- Histórico de alterações (audit log)
- Dashboard avançado (gráficos)
- Exportação Excel/PDF
- Imutabilidade de parcelas pagas (BR-FUT01)

---

### Could Have (V2.0 - +3 meses)

- RF10: Pipeline de importação Excel (Mapper)
- RF16: WhatsApp API Premium (automação)
- Níveis de permissão (Editor, Auditor)
- Rating de fornecedores
- Assinatura digital (DocuSign)
- Gateway de pagamento (Stripe)
- Internacionalização (i18n)
- App mobile (React Native)

---

### Won't Have (Fora de escopo)

- ❌ Marketplace de fornecedores
- ❌ Sincronização bidirecional com Google Calendar
- ❌ Geração automática de contratos via templates
- ❌ CRM completo
- ❌ Gestão de equipe (múltiplos planners)

---

## 9. Métricas de Sucesso

**MVP será considerado sucesso se:**

1. ✅ **5 cerimonialistas** usam por 30+ dias
2. ✅ Redução de **50%** no tempo de controle financeiro (vs Excel)
3. ✅ Dashboard responde em **< 500ms** (p95)
4. ✅ **Zero** perda de dados (backups testados mensalmente)
5. ✅ **< 5 bugs críticos** no primeiro mês
6. ✅ **Pelo menos 1 cerimonialista** paga por plano premium (após V1.1)

**KPIs Técnicos:**

- Uptime: > 99.5%
- Latência API (p95): < 500ms
- Cobertura de testes: ≥ 75%
- Taxa de erro 5xx: < 0.1%

---

## 10. Decisões Técnicas Documentadas

### Por que Cloudflare R2 ao invés de AWS S3?

**R2:**

- ✅ 10GB grátis (S3: 5GB)
- ✅ **Zero egress costs** (S3 cobra USD 0,09/GB)
- ✅ S3-compatible API (usa boto3)

**Economia em escala:**

**Decisões técnicas detalhadas** (por que R2 vs S3, Neon vs Railway, OIDC vs secrets, Presigned URLs, Chaves híbridas, Service Layer) serão documentadas em [ADR/](#) (Architecture Decision Records - a ser criado).

---

## 11. Referências

- [BUSINESS_RULES.md](BUSINESS_RULES.md) - Regras de negócio consolidadas
- [ARCHITECTURE.md](ARCHITECTURE.md) - Decisões técnicas
- [ENVIRONMENT.md](ENVIRONMENT.md) - Configuração de ambiente

---

### Por que Service Layer ao invés de Fat Models/Serializers?

**Service Layer:**

- ✅ Lógica testável isoladamente
- ✅ Reutilizável (views/tasks/commands)
- ✅ Transações atômicas explícitas
- ✅ Separação de responsabilidades clara

**Fat Models:**

- ❌ Acoplamento alto
- ❌ Difícil de testar
- ❌ Lógica espalhada

---

## 12. Arquitetura de Deploy

```

┌─────────────┐ ┌──────────────┐ ┌─────────────┐
│ GitHub │────────▶│ Vercel │────────▶│ CDN Edge │
│(Repositório)│ │ (Frontend) │ │ (Global) │
└─────────────┘ └──────────────┘ └─────────────┘
│ │
│ │ HTTPS (JWT)
│ ▼
│ ┌──────────────┐
│ │ Cloud Run │◀────┐ OIDC
└───────────────▶│ (Backend) │ │
└──────────────┘ │
│ │
┌───────────┼────────────┴────────┐
▼ ▼ ▼ ▼
┌─────────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐
│ Neon │ │ R2 │ │ Resend │ │ Cloud │
│ PostgreSQL │ │ (PDFs) │ │ (Email) │ │Scheduler │
└─────────────┘ └─────────┘ └─────────┘ └──────────┘

```

**Fluxo de Request:**

1. Usuário acessa Vercel (frontend)
2. Frontend faz API call ao Cloud Run (JWT no header)
3. Cloud Run valida JWT e processa
4. Retorna JSON ao frontend
5. Frontend renderiza

**Automação (Cloud Scheduler):**

1. Scheduler dispara POST com OIDC token
2. Cloud Run valida service account
3. Executa task (update OVERDUE, alertas)
4. Logs estruturados para observabilidade

---

**Última atualização:** 1 de março de 2026
**Responsável:** Rafael
**Versão:** 6.1 - Remoção de SoftDelete, correção de links
**Próxima revisão:** Após conclusão do MVP

---

## Changelog

**v6.0 (08/02/2026):**

- ✅ Documentadas regras de negócio implementadas (tolerância zero, mixins)
- ✅ Adicionado RF05 (Automação OVERDUE com OIDC)
- ✅ Adicionado RF10 (Pipeline Excel - V2.0)
- ✅ Adicionado RF16 (WhatsApp Quick Link)
- ✅ Separação clara: Implementado vs Planejado
- ✅ Cobertura de testes estratificada (100% em lógica financeira)
- ✅ Decisões técnicas justificadas (OIDC, Presigned URLs, Service Layer)

**v5.0 (03/02/2026):**

- Separação de domínios de negócio
- Chaves primárias híbridas

**v4.1 (anterior):**

- Escopo acadêmico (centralização de dados)
```

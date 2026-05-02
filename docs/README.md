# 📚 Documentação do Wedding Management System

**Versão:** 6.1
**Última atualização:** 1 de março de 2026
**Status:** Em desenvolvimento (MVP)

---

## 📖 Estrutura da Documentação

Nossa documentação segue o princípio **"O QUÊ → POR QUE → COMO"**:

```
docs/
├── README.md                    ← Você está aqui (guia de navegação)
├── REQUIREMENTS.md              ← O QUÊ construir (funcionalidades)
├── BUSINESS_RULES.md            ← REGRAS de negócio (validações)
├── ARCHITECTURE.md              ← COMO construir (stack, padrões)
├── ENVIRONMENT.md               ← Configuração de ambiente
├── TROUBLESHOOTING.md           ← Resolução de problemas comuns

└── ADR/                         ← POR QUE decisões técnicas
    ├── 001-why-cloud-run.md
    ├── 002-why-neon.md
    ├── 003-why-r2.md
    ├── 004-presigned-urls.md
    ├── 005-oidc-scheduler.md
    ├── 006-service-layer.md
    ├── 007-hybrid-keys.md
    ├── 008-soft-delete.md
    ├── 009-multitenancy.md
    ├── 010-tolerance-zero.md
    ├── 011-basemodel-save-full-clean.md
    ├── 012-orval-contract-driven-frontend.md
    ├── 013-migrate-drf-to-ninja.md
    └── 016-pragmatic-multi-tenancy.md
```

---

## 🗺️ Rotas de Leitura por Perfil

### 👔 Product Manager / Stakeholder

**Objetivo:** Entender FUNCIONALIDADES e REGRAS de negócio

1. **[REQUIREMENTS.md](REQUIREMENTS.md)** (593 linhas) ⭐ **COMECE AQUI**
   - Problema e solução
   - Casos de uso (dashboard, financeiro, logística)
   - MVP vs funcionalidades futuras
   - Requisitos não-funcionais

2. **[BUSINESS_RULES.md](BUSINESS_RULES.md)** (839 linhas)
   - Regras core (autenticação, multitenancy, timestamps)
   - Regras financeiras (tolerância zero, parcelas)
   - Regras de logística (fornecedores, itens)
   - Regras futuras (notificações, relatórios)

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** (seção "Visão de Negócio")
   - Stack simplificado
   - Custos (R$0/mês MVP)

---

### 💻 Desenvolvedor (Backend/Frontend)

**Objetivo:** Implementar FEATURES e entender PADRÕES de código

1. **[REQUIREMENTS.md](REQUIREMENTS.md)** ⭐ **COMECE AQUI**
   - Funcionalidades do seu módulo (financeiro, logística)
   - User stories com exemplos práticos

2. **[BUSINESS_RULES.md](BUSINESS_RULES.md)**
   - Validações a implementar
   - Fórmulas de cálculo (parcelas, totais)
   - Estados e transições (PENDING → PAID → OVERDUE)

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** ⭐ **ESSENCIAL**
   - Service Layer Pattern (onde colocar lógica)
   - Mixins (BaseModel, WeddingOwnedMixin, SoftDeleteModel)
   - Configuração (Django, React, Docker)
   - Performance (N+1 detection, caching)

4. **ADR específicos:**
   - Backend: [006-service-layer](ADR/006-service-layer.md), [010-tolerance-zero](ADR/010-tolerance-zero.md)
   - Frontend: [004-presigned-urls](ADR/004-presigned-urls.md)
   - Autenticação: [005-oidc-scheduler](ADR/005-oidc-scheduler.md)

---

### 🏗️ Arquiteto / Tech Lead

**Objetivo:** Entender DECISÕES técnicas e TRADE-OFFS

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** ⭐ **COMECE AQUI**
   - Stack completo (Django, React, Neon, R2, Cloud Run)
   - Padrões de código (Service Layer, Soft Delete, Multitenancy)
   - Infraestrutura (Docker, CI/CD, Cloud Run config)
   - Segurança (JWT, OIDC, Rate Limiting)
   - Performance (JOINs, indexing, caching)
   - Monitoramento (Sentry, logs estruturados)

2. **ADR (Architecture Decision Records):** ⭐ **ESSENCIAL**
   - Infraestrutura:
     - [001-why-cloud-run](ADR/001-why-cloud-run.md): Serverless backend
     - [002-why-neon](ADR/002-why-neon.md): PostgreSQL serverless
     - [003-why-r2](ADR/003-why-r2.md): Storage zero egress
   - Padrões de código:
     - [006-service-layer](ADR/006-service-layer.md): Separação de concerns
     - [007-hybrid-keys](ADR/007-hybrid-keys.md): BigInt + UUID
     - [008-soft-delete](ADR/008-soft-delete.md): Exclusão seletiva
     - [009-multitenancy](ADR/009-multitenancy.md): Denormalização
     - [010-tolerance-zero](ADR/010-tolerance-zero.md): Precisão financeira
   - Segurança/Performance:
     - [004-presigned-urls](ADR/004-presigned-urls.md): Upload direto
     - [005-oidc-scheduler](ADR/005-oidc-scheduler.md): Service-to-service auth

3. **[BUSINESS_RULES.md](BUSINESS_RULES.md)**
   - Constraints críticas (tolerância zero, soft delete seletivo)

---

### 🧪 QA / Tester

**Objetivo:** Criar CASOS DE TESTE e VALIDAÇÕES

1. **[BUSINESS_RULES.md](BUSINESS_RULES.md)** ⭐ **COMECE AQUI**
   - Todas as regras são TESTÁVEIS
   - Fórmulas de validação
   - Estados válidos/inválidos

2. **[REQUIREMENTS.md](REQUIREMENTS.md)**
   - Fluxos de usuário (cenários de teste)
   - Requisitos não-funcionais (performance, segurança)

3. **ADR específicos:**
   - [010-tolerance-zero](ADR/010-tolerance-zero.md): Casos de teste financeiros
   - [006-service-layer](ADR/006-service-layer.md): Testabilidade de lógica
   - [009-multitenancy](ADR/009-multitenancy.md): Cross-wedding validation

---

## 📄 Detalhamento dos Documentos

### 1. [REQUIREMENTS.md](REQUIREMENTS.md) (593 linhas)

**O QUÊ construir**

- **Problema:** Planilhas desorganizadas, falta de controle financeiro
- **Solução:** Sistema web centralizado e automatizado
- **Funcionalidades:**
  - Dashboard (visão geral de finanças e tarefas)
  - Financeiro (categorias, itens, contratos, parcelas)
  - Logística (fornecedores, eventos, cronograma)
  - Futuro (notificações, relatórios, checklist)
- **Requisitos não-funcionais:**
  - Performance (<500ms API, <2s load)
  - Segurança (JWT, OIDC, OWASP)
  - Usabilidade (mobile-first, PWA)

**Quando ler:** Sempre antes de implementar nova feature

---

### 2. [BUSINESS_RULES.md](BUSINESS_RULES.md) (839 linhas)

**REGRAS de negócio (validações)**

- **BR-CORE:** Autenticação, multitenancy, timestamps, soft delete
- **BR-FIN:** Tolerância zero, status de parcelas, cálculos financeiros
- **BR-LOG:** Fornecedores, itens orçamentários, eventos
- **BR-SCH:** Tarefas agendadas (parcelas vencidas)
- **BR-FUT:** Notificações, relatórios, checklist (roadmap)

**Quando ler:** Ao implementar validações ou criar testes

---

### 3. [ARCHITECTURE.md](ARCHITECTURE.md)

**COMO construir (stack, padrões, infraestrutura)**

- **Visão geral:** Diagrama de arquitetura (Frontend → Backend → Database/Storage)
- **Stack tecnológico:**
  - Backend: Django 5.2 + Django Ninja 1.6 (Docker local, Cloud Run produção)
  - Frontend: React 19 + Vite 7 + TypeScript 5
  - Database: PostgreSQL (Docker) / SQLite (dev local)
  - Storage: Cloudflare R2 (planejado)
  - Email: Resend (planejado)
  - Monitoring: Sentry (planejado)

- **Padrões de código:**
  - Service Layer (lógica de negócio isolada)
  - Mixins (BaseModel, TenantModel, WeddingOwnedMixin)
  - Validação em cascata (Model → Serializer → Service)

- **Infraestrutura:**
  - Docker (desenvolvimento local)
  - Cloud Run (produção serverless)
  - GitHub Actions (CI/CD)

- **Segurança:** JWT (24h access + 7d refresh), OIDC, Rate Limiting
- **Performance:** N+1 detection, caching, indexing
- **Monitoramento:** Sentry, logs estruturados
- **Custos:** R$0/mês MVP, R$330/mês @ 500 users

**Quando ler:** Ao configurar ambiente ou implementar padrão

---

### 4. ADR/ (10 decisões arquiteturais)

**POR QUE decisões técnicas (contexto, alternativas, trade-offs)**

#### Infraestrutura

**[001-why-cloud-run.md](ADR/001-why-cloud-run.md)** (180 linhas)

- **Decisão:** Google Cloud Run para backend
- **Alternativas:** AWS Lambda, Railway, Heroku, DigitalOcean
- **Vantagens:** 2M req/month free, scale-to-zero, sem servidor gerenciado
- **Trade-offs:** Cold start (2-3s), PostgreSQL externo, GCP lock-in

**[002-why-neon.md](ADR/002-why-neon.md)** (200 linhas)

- **Decisão:** Neon PostgreSQL serverless
- **Alternativas:** Railway, AWS RDS, Supabase
- **Vantagens:** 3GB storage (3x Railway), branching (dev/staging), hibernation
- **Trade-offs:** Cold start (1-2s), menos maduro que RDS

**[003-why-r2.md](ADR/003-why-r2.md)** (120 linhas)

- **Decisão:** Cloudflare R2 para object storage
- **Alternativas:** AWS S3, Google Cloud Storage
- **Vantagens:** Zero egress cost (R$0 vs S3 R$1.80/mês), S3-compatible
- **Trade-offs:** Menos maduro, sem CDN integrado

---

#### Padrões de Código

**[004-presigned-urls.md](ADR/004-presigned-urls.md)** (200 linhas)

- **Decisão:** Upload direto com presigned URLs
- **Alternativas:** Upload via backend
- **Vantagens:** 50ms vs 5s, unlimited concurrent, minimal compute
- **Inclui:** Fluxo completo (diagrama + código backend + frontend)

**[005-oidc-scheduler.md](ADR/005-oidc-scheduler.md)** (180 linhas)

- **Decisão:** OIDC para Cloud Scheduler → Cloud Run
- **Alternativas:** API Key, IP Whitelist
- **Vantagens:** Zero secrets, auditável, rotação automática
- **Trade-offs:** GCP lock-in, complexidade setup

**[006-service-layer.md](ADR/006-service-layer.md)** (220 linhas)

- **Decisão:** Service Layer Pattern (separar lógica de Views/Serializers)
- **Alternativas:** Fat Serializer, Fat Model
- **Vantagens:** Testabilidade (unit tests sem mocks), reusabilidade, SRP
- **Trade-offs:** Mais arquivos, curva de aprendizado

**[007-hybrid-keys.md](ADR/007-hybrid-keys.md)** (180 linhas)

- **Decisão:** BigInt (interno) + UUID (público)
- **Alternativas:** UUID apenas, Integer apenas
- **Vantagens:** JOINs 3x mais rápidos (BigInt), segurança (UUID não sequencial)
- **Trade-offs:** Dois campos de identificação, +36 bytes por registro

**[008-soft-delete.md](ADR/008-soft-delete.md)** (200 linhas)

- **Decisão:** Soft delete SELETIVO (5 models COM, 3 models SEM)
- **Alternativas:** Hard delete em tudo, Soft delete em tudo
- **COM soft delete:** Wedding, Category, Item, Contract, Supplier (restauráveis)
- **SEM soft delete:** Installment, Event, Notification (volume alto/imutável)
- **Trade-offs:** Dois managers (objects vs all_objects), espaço em disco

**[009-multitenancy.md](ADR/009-multitenancy.md)** (200 linhas)

- **Decisão:** Multitenancy DENORMALIZADO (wedding_id em todos models)
- **Alternativas:** Schema-based, Normalizado (4 JOINs)
- **Vantagens:** Queries 93% mais rápidas (zero JOINs), escalabilidade horizontal
- **Trade-offs:** Denormalização (+8 bytes), validação cross-wedding

**[010-tolerance-zero.md](ADR/010-tolerance-zero.md)** (220 linhas)

- **Decisão:** Decimal com tolerância ZERO (ajuste na última parcela)
- **Alternativas:** Float com tolerância, Decimal com tolerância 0.01
- **Vantagens:** Precisão absoluta, auditoria sem discrepâncias, conformidade legal
- **Trade-offs:** Lógica de ajuste, última parcela com valor diferente

---

## 🔍 Busca Rápida

### Por Funcionalidade

| Funcionalidade            | Documento                          | Seção    |
| ------------------------- | ---------------------------------- | -------- |
| **Dashboard**             | [REQUIREMENTS.md](REQUIREMENTS.md) | RF-DASH  |
| **Categorias de despesa** | [REQUIREMENTS.md](REQUIREMENTS.md) | RF-FIN01 |
| **Contratos**             | [REQUIREMENTS.md](REQUIREMENTS.md) | RF-FIN03 |
| **Parcelas**              | [REQUIREMENTS.md](REQUIREMENTS.md) | RF-FIN04 |
| **Fornecedores**          | [REQUIREMENTS.md](REQUIREMENTS.md) | RF-LOG01 |
| **Cronograma**            | [REQUIREMENTS.md](REQUIREMENTS.md) | RF-LOG03 |

### Por Regra de Negócio

| Regra                       | Documento                              | Código    |
| --------------------------- | -------------------------------------- | --------- |
| **Tolerância zero**         | [BUSINESS_RULES.md](BUSINESS_RULES.md) | BR-FIN03  |
| **Status de parcelas**      | [BUSINESS_RULES.md](BUSINESS_RULES.md) | BR-FIN04  |
| **Soft delete seletivo**    | [BUSINESS_RULES.md](BUSINESS_RULES.md) | BR-CORE04 |
| **Multitenancy**            | [BUSINESS_RULES.md](BUSINESS_RULES.md) | BR-CORE02 |
| **Validação de fornecedor** | [BUSINESS_RULES.md](BUSINESS_RULES.md) | BR-LOG02  |

### Por Decisão Técnica

| Decisão                  | ADR                                             | Código  |
| ------------------------ | ----------------------------------------------- | ------- |
| **Service Layer**        | [006-service-layer](ADR/006-service-layer.md)   | ADR-006 |
| **Upload de arquivos**   | [004-presigned-urls](ADR/004-presigned-urls.md) | ADR-004 |
| **Chaves BigInt + UUID** | [007-hybrid-keys](ADR/007-hybrid-keys.md)       | ADR-007 |
| **Precisão financeira**  | [010-tolerance-zero](ADR/010-tolerance-zero.md) | ADR-010 |
| **Serverless backend**   | [001-why-cloud-run](ADR/001-why-cloud-run.md)   | ADR-001 |

---

## 🚀 Começando

### Para Implementar Nova Feature

1. **Leia [REQUIREMENTS.md](REQUIREMENTS.md):** Entenda a funcionalidade
2. **Leia [BUSINESS_RULES.md](BUSINESS_RULES.md):** Valide regras de negócio
3. **Consulte [ARCHITECTURE.md](ARCHITECTURE.md):** Aplique padrões de código
4. **Verifique ADR relevantes:** Entenda decisões técnicas

### Para Configurar Ambiente

1. **Leia [ARCHITECTURE.md](ARCHITECTURE.md) → "Infraestrutura"**
2. **Configure Docker:** `docker-compose up`
3. **Configure secrets:** Ver `ENVIRONMENT.md`

### Para Entender Decisão Técnica

1. **Leia [ARCHITECTURE.md](ARCHITECTURE.md):** Visão geral
2. **Aprofunde no ADR específico:** Contexto e trade-offs

---

## 🔄 Manutenção da Documentação

### Quando Atualizar

- **REQUIREMENTS.md:** Nova feature ou mudança de escopo
- **BUSINESS_RULES.md:** Nova validação ou mudança de regra
- **ARCHITECTURE.md:** Mudança de stack ou padrão
- **ADR:** Nova decisão técnica significativa

### Formato ADR

Cada ADR segue template:

1. **Status** (Aceito/Rejeitado/Deprecated)
2. **Contexto e Problema**
3. **Decisão**
4. **Justificativa** (comparação de alternativas)
5. **Trade-offs** (positivos, negativos, neutros)
6. **Consequências**
7. **Monitoramento** (métricas, alertas)
8. **Referências** (links para docs/papers)

---

## 📞 Contato

**Documentação mantida por:** Rafael
**Última revisão:** 1 de março de 2026
**Versão do sistema:** MVP em desenvolvimento

---

## 📌 Links Úteis

- [Estrutura do Projeto](../README.md)
- [Guia de Instalação](ENVIRONMENT.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Arquitetura](ARCHITECTURE.md)

---

**💡 Dica:** Use Ctrl+F (Cmd+F no Mac) para buscar keywords neste README e navegar rapidamente para o documento correto.

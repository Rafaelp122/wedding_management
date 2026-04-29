# 🏗️ Arquitetura Técnica - Wedding Management System

## Versão 2.0 - SaaS B2B e Multi-Eventos

> **Última atualização:** Abril 2026

---

## 1. Visão Geral (SaaS B2B)

O sistema utiliza um modelo de **Multi-tenancy Híbrido** para suportar agências de eventos:

1.  **Tenant Primário (Company):** O isolador de dados de alto nível. Usuários, Fornecedores e Clientes pertencem a uma empresa.
2.  **Tenant Secundário (Event):** O isolador de dados operacional. Orçamentos e Contratos são restritos a um evento específico.

### Arquitetura de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React 19 + Vite 7 + TypeScript 5                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Django 5.2 + Django Ninja 1.6                       │   │
│  │  - Camada de Serviços Especializada (ADR-016)        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                    ↕                      ↕
┌───────────────────────────┐  ┌──────────────────────────────┐
│   DATABASE LAYER          │  │   STORAGE LAYER              │
│  ┌────────────────────┐   │  │  ┌───────────────────────┐  │
│  │  Neon PostgreSQL   │   │  │  │  Cloudflare R2        │  │
│  └────────────────────┘   │  │  └───────────────────────┘  │
└───────────────────────────┘  └──────────────────────────────┘
```

---

## 2. Stack Técnico Detalhado

### 2.1 Backend (Django Ninja)
- **Estrutura de Apps:**
  - `tenants/`: Gestão de Empresas e Assinaturas.
  - `users/`: Autenticação e Perfis.
  - `events/`: Núcleo polimórfico (Event + WeddingDetail).
  - `finances/`: Controle financeiro isolado por evento.
  - `logistics/`: Contratos e Fornecedores isolados por empresa.
  - `scheduler/`: Compromissos (`Appointment`).

---

## 3. Padrões de Código e Arquitetura

### 3.1 Camada de Serviços (Service Layer)
Utilizamos o **Strategy Pattern (Handlers)** para lidar com múltiplos tipos de eventos sem herança rígida, garantindo o princípio Open/Closed:

```python
# EventService (Orquestrador) -> Delega para Handlers especializados
# WeddingHandler (Especializado) -> Cuida do que é específico de Casamentos
```

### 3.2 Mixins de Isolamento (Tenancy)

Os mixins de isolamento foram movidos para seus respectivos apps de domínio para evitar acoplamento circular no `core`:

**CompanyOwnedMixin (apps.tenants.mixins):**
Utilizado para dados que a agência compartilha globalmente (Ex: Fornecedores).
```python
class CompanyOwnedMixin(models.Model):
    company = models.ForeignKey('tenants.Company', on_delete=models.CASCADE)
```

**EventOwnedMixin (apps.events.mixins):**
Utilizado para dados operacionais restritos a um projeto específico (Ex: Despesas).
```python
class EventOwnedMixin(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
```

### 3.3 Event-Driven Architecture (Signals)
Para evitar o acoplamento forte entre os domínios (ex: `events` precisar conhecer as regras de `finances`), utilizamos o padrão **Publisher/Subscriber** nativo do Django (Signals).

**Efeitos Colaterais Documentados (Side-Effects):**
*   **Tenant Silencioso (`users` ➔ `tenants`):**
    Ao criar um novo usuário (`User`), o signal `create_user_company` gera automaticamente uma `Company` e a vincula a este usuário.
*   **Orçamento Automático (`events` ➔ `finances`):**
    Ao criar um Evento Especializado (ex: `WEDDING`), o signal `wedding_created` notifica o módulo financeiro, que imediatamente gera um `Budget` vazio e as `BudgetCategory` padrões para aquele evento.

> ⚠️ **Atenção em Testes:** Como os Signals rodam no mesmo processo, em testes que criam dados via Factories, é comum haver conflitos de integridade (ex: tentar criar um orçamento via factory quando o Signal já o criou). O uso de Mock (`patch`) ou a adequação do payload na factory (ex: `event_type="OTHER"`) são necessários para isolar os testes.

### 3.4 Chaves Híbridas
- **Interno:** `BigAutoField` para performance em JOINs.
- **Público:** `UUID4` para segurança e URLs amigáveis na API.

---

## 4. Banco de Dados e Performance

**Índices Estratégicos:**
- `idx_company_id`: Filtro primário de tenancy.
- `idx_event_id`: Filtro operacional.
- `idx_status`: Filtragem de fluxos de trabalho.

**Otimização:**
O uso de **Denormalização (ADR-009)** garante que queries de listagem financeira (`Expenses`) não precisem fazer JOIN com a tabela de Eventos ou Empresas, reduzindo a latência em até 90%.

---

## 5. Segurança
- **JWT:** Autenticação stateless com rotação de tokens.
- **OIDC:** Autenticação segura para tarefas agendadas (Cloud Scheduler).
- **Tenant Silencioso:** Garantimos que no cadastro, todo usuário receba uma `Company` automaticamente, blindando o sistema contra vazamento de dados desde o dia 1.

---

**Referências:** Consulte as **[ADRs](ADR/)** para o detalhamento de cada decisão técnica.

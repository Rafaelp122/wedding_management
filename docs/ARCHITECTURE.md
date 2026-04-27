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
Utilizamos herança de serviços para lidar com múltiplos tipos de eventos sem duplicar lógica:

```python
# EventService (Base) -> Cuida do que é comum (Status, Datas)
# WeddingService (Sub) -> Cuida do que é específico (Noivos, Cerimônia)
```

### 3.2 Mixins de Isolamento (Tenancy)

**CompanyOwnedMixin:**
Utilizado para dados que a agência compartilha globalmente.
```python
class CompanyOwnedMixin(models.Model):
    company = models.ForeignKey('tenants.Company', on_delete=models.CASCADE)
```

**EventOwnedMixin:**
Utilizado para dados operacionais restritos a um projeto.
```python
class EventOwnedMixin(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
```

### 3.3 Chaves Híbridas
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

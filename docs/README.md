# 📚 Documentação do Wedding Management System

**Versão:** 7.0 (SaaS B2B Readiness)
**Última atualização:** Abril 2026
**Status:** Em evolução arquitetural (ADR-016)

---

## 📖 Estrutura da Documentação

Nossa documentação segue o princípio **"O QUÊ → POR QUE → COMO"**:

```
docs/
├── README.md                    ← Você está aqui (guia de navegação)
├── REQUIREMENTS.md              ← O QUÊ construir (funcionalidades)
├── BUSINESS_RULES.md            ← REGRAS de negócio (validações)
├── ARCHITECTURE.md              ← COMO construir (stack, padrões)
├── ENVIRONMENT.md               ← Guia de Configuração (How-to)
├── TROUBLESHOOTING.md           ← Resolução de problemas comuns

└── ADR/                         ← POR QUE decisões técnicas
    ├── ...
    ├── 015-controller-dependency-injection.md
    └── 016-event-company-architecture.md  ← Nova base SaaS B2B
```

---

## 🗺️ Rotas de Leitura por Perfil

### 👔 Product Manager / Stakeholder

1. **[REQUIREMENTS.md](REQUIREMENTS.md)** ⭐ **COMECE AQUI**
   - Problema e solução (foco em agências e cerimonialistas)
2. **[BUSINESS_RULES.md](BUSINESS_RULES.md)**
   - Regras financeiras e de isolamento de dados
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** (seção "Visão de Negócio")

---

### 💻 Desenvolvedor (Backend/Frontend)

1. **[ENVIRONMENT.md](ENVIRONMENT.md)** ⭐ **ONBOARDING**
   - Como rodar o projeto localmente (Docker/Bare Metal)
2. **[REQUIREMENTS.md](REQUIREMENTS.md)**
   - Funcionalidades por domínio (Eventos, Finanças, Logística)
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** ⭐ **PADRÕES**
   - Service Layer, Mixins (`CompanyOwned`, `EventOwned`), Segurança
4. **Referência de API:**
   - [Swagger UI](http://localhost:8000/api/v1/docs) (Backend rodando localmente)
   - [Redoc](http://localhost:8000/api/v1/redoc)

---

### 🏗️ Arquiteto / Tech Lead

1. **[ADR-016](ADR/016-event-company-architecture.md)** ⭐ **CRÍTICO**
   - Entenda a mudança de Casamento para Eventos Genéricos e Tenancy por Empresa.
2. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - Stack completo e padrões de infraestrutura.
3. **ADR Históricas:**
   - [009-multitenancy](ADR/009-multitenancy.md) (Evoluída pela 016)
   - [010-tolerance-zero](ADR/010-tolerance-zero.md) (Precisão financeira)

---

## 🔍 Busca Rápida (Entidades Core)

| Entidade | Descrição | Regras de Isolamento |
|---|---|---|
| **Company** | O Tenant principal (Agência) | `CompanyOwnedMixin` |
| **Event** | O projeto (Casamento, Aniversário, etc.) | `EventOwnedMixin` |
| **WeddingDetail** | Dados específicos de casamentos | 1:1 com Event |
| **Appointment** | Compromisso de calendário | Vinculado ao Event |

---

## 🔄 Manutenção da Documentação

Seguimos o framework **Diátaxis**:
- **Tutoriais:** No `README.md` raiz (Quick Start).
- **How-to Guides:** Em `ENVIRONMENT.md` e `TROUBLESHOOTING.md`.
- **Referência:** Em `BUSINESS_RULES.md`, `ARCHITECTURE.md` e Swagger.
- **Explicação:** Em `ADR/` e seções teóricas do `ARCHITECTURE.md`.

---

**💡 Dica:** Use `/api/v1/docs` para testar os endpoints em tempo real e ver os payloads exatos de Request/Response.

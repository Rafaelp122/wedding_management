# 💍 Wedding Management System

Sistema completo de gestão de casamentos com arquitetura moderna **React SPA + Django Ninja API**.

Este repositório centraliza o controle financeiro, logístico e de cronograma para cerimonialistas profissionais, garantindo integridade de dados e automação de processos.

---

## 📖 Guia de Navegação

Nossa documentação segue o princípio Diátaxis. Escolha sua rota de leitura conforme seu perfil:

### 👔 Product Manager / Stakeholder
*Entenda o que o sistema faz e as regras de negócio.*
1. **[Requisitos (docs/REQUIREMENTS.md)](docs/REQUIREMENTS.md)**: Problema, solução e visão de produto.
2. **[Regras de Negócio (docs/BUSINESS_RULES.md)](docs/BUSINESS_RULES.md)**: Validações financeiras e operacionais.

### 💻 Desenvolvedor
*Configure o ambiente e entenda os padrões de implementação.*
1. **[Ambiente (docs/ENVIRONMENT.md)](docs/ENVIRONMENT.md)**: Guia de instalação (Docker/Local) e comandos `make`.
2. **[Arquitetura (docs/ARCHITECTURE.md)](docs/ARCHITECTURE.md)**: Visão técnica, Stack e padrões de código (Service Layer).
3. **[API & Frontend (docs/API.md)](docs/API.md)**: Como consumir a API e usar os hooks gerados.
4. **[Casos de Uso (docs/use-cases/)](docs/use-cases/index.md)**: Fluxos de tela e lógica funcional.

### 🏗️ Arquiteto / Tech Lead
*Entenda as decisões técnicas e trade-offs.*
1. **[ADR (Architecture Decision Records)](docs/ARCHITECTURE.md#9-referências)**: Por que escolhemos Cloud Run, Neon, R2, etc.

---

## 🛠 Tech Stack (Resumo)

- **Backend:** Django 5.2 + Django Ninja (API-First).
- **Frontend:** React 19 + TypeScript + Tailwind CSS + shadcn/ui.
- **Database:** PostgreSQL (Neon).
- **Infra:** Docker, Cloud Run, Cloudflare R2.

> 📖 **Detalhes completos da Stack:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🚀 Quick Start (Resumo)

```bash
cp .env.example .env  # Configure suas chaves
make up               # Inicie via Docker
make superuser        # Crie seu acesso admin
```

> 📖 **Guia Completo de Instalação:** [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)

---

## 📁 Estrutura do Projeto

```
wedding_management/
├── backend/                  # Django Ninja API
├── frontend/                # React SPA
├── docs/                    # Documentação técnica (Princípio Diátaxis)
├── .env                     # Variáveis de ambiente
├── Makefile                 # Automação de comandos
└── docker-compose.yml       # Orquestração de containers
```

---

## 🧪 Qualidade e Troubleshooting

- **Testes:** `make test`
- **Linter/Format:** `make lint` / `make format`
- **Problemas comuns:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📝 Licença
Projeto Integrador - FIRJAN SENAI São Gonçalo

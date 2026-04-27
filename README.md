# 💍 Wedding Management System

Sistema completo de gestão de eventos (com foco em casamentos) utilizando **React SPA + Django Ninja API**.

Este projeto demonstra uma arquitetura profissional **SaaS B2B**, permitindo o gerenciamento de múltiplos eventos sob o guarda-chuva de uma agência (Company).

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.10-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)

---

## 🚀 Quick Start (Tutorial)

Siga estes 3 passos para rodar o projeto em sua máquina local usando Docker:

### 1. Preparar o Ambiente
Crie o arquivo de variáveis de ambiente a partir do exemplo:
```bash
cp .env.example .env
```

### 2. Iniciar os Containers
O projeto utiliza Docker Compose para orquestrar o Backend, Frontend e Banco de Dados:
```bash
make up
```

### 3. Criar Acesso Inicial
Crie um superusuário para acessar o painel administrativo e a API:
```bash
make superuser
```

**Pronto! Acesse o sistema:**
- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Documentação da API (Swagger):** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

---

## 📖 Documentação Centralizada

Nossa documentação é organizada pelo framework **Diátaxis**:

| Documento | Conteúdo |
|---|---|
| **[Guia de Ambiente](docs/ENVIRONMENT.md)** | Comandos `make`, variáveis `.env` e Troubleshooting. |
| **[Regras de Negócio](docs/BUSINESS_RULES.md)** | Lógica financeira e validações críticas. |
| **[Arquitetura Técnica](docs/ARCHITECTURE.md)** | Padrões de código, infraestrutura e segurança. |
| **[ADR (Decisões)](docs/ADR/)** | Registro histórico de decisões arquiteturais. |

---

## 🏗️ Destaques da Engenharia

- **Isolamento B2B:** Multi-tenancy denormalizado por Empresa (`Company`).
- **Precisão Financeira:** Sistema de tolerância zero para parcelamento e contratos.
- **Contract-Driven API:** Sincronização automática entre Backend e Frontend via OpenAPI + Orval.
- **Service Layer:** Lógica de negócio 100% isolada das Views HTTP.

---

## 📝 Licença
Projeto Integrador - FIRJAN SENAI São Gonçalo

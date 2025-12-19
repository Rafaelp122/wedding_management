# Documentação Técnica - Wedding Management System

Bem-vindo à documentação técnica completa do sistema de gestão de casamentos.

---

## 📚 Índice

### 📦 Aplicações (Apps)

Cada app possui documentação técnica completa incluindo arquitetura, models, views, mixins, testes e exemplos de uso:

- [Weddings](apps/weddings.md) - Gestão de casamentos (núcleo do sistema) | Arquitetura híbrida Web + API
- [Contracts](apps/contracts.md) - Sistema de assinatura digital tripartite com auditoria completa
- [Items](apps/items.md) - Gestão de itens e produtos vinculados a contratos
- [Budget](apps/budget.md) - Controle orçamentário read-only baseado em itens
- [Scheduler](apps/scheduler.md) - Calendário de eventos integrado com FullCalendar
- [Users](apps/users.md) - Autenticação (Django Allauth) e perfis de usuário
- [Pages](apps/pages.md) - Páginas institucionais (home, sobre, contato)
- [Core](apps/core.md) - Utilitários e mixins compartilhados

### 🐳 Infraestrutura

- [Docker Setup](DOCKER.md) - Guia completo de Docker (dev, local, produção)
- [Deploy em Produção](PRODUCTION_DEPLOY.md) - Checklist e instruções de deployment

### 📖 Informações Gerais

- **Arquitetura**: Cada app documenta seus padrões e decisões de design
- **API REST**: Documentação completa em cada app (serializers, views, permissions)
- **Testes**: 364 testes (75% cobertura) - Ver README principal e documentação de cada app
- **Ambientes**: Local (SQLite), Docker (PostgreSQL), Produção (PostgreSQL + Nginx)

---

## 🚀 Começando

Se você é novo no projeto, recomendamos:

1. **Ler o [README principal](../README.md)** - Visão geral, instalação e execução
2. **Escolher um app** - Cada app tem documentação técnica detalhada
3. **Explorar a [estrutura Docker](DOCKER.md)** - Para entender os ambientes

---

## 📝 Convenções de Documentação

- **README.md nos apps**: Breve descrição (2-4 linhas) + link para `docs/apps/`
- **docs/apps/**: Documentação técnica completa de cada aplicação
- **Código autodocumentado**: Docstrings detalhadas em classes e métodos

---

## 🔄 Atualização

Esta documentação é atualizada continuamente.  
**Última atualização:** 18 de dezembro de 2025

# Documentação Técnica - Wedding Management System

Bem-vindo à documentação técnica completa do sistema de gestão de casamentos.

---

## 📚 Índice

### 🏗️ Arquitetura
- [Visão Geral da Arquitetura](architecture/overview.md)
- [Decisões de Design](architecture/design-decisions.md)
- [Fluxo de Dados](architecture/data-flow.md)
- [Padrões e Convenções](architecture/patterns.md)

### 📦 Aplicações (Apps)
- [Weddings](apps/weddings.md) - Gestão de casamentos (núcleo do sistema)
- [Contracts](apps/contracts.md) - Sistema de assinatura digital tripartite
- [Items](apps/items.md) - Gestão de itens e produtos
- [Budget](apps/budget.md) - Controle orçamentário
- [Scheduler](apps/scheduler.md) - Calendário e agendamento
- [Users](apps/users.md) - Autenticação e perfis de usuário
- [Pages](apps/pages.md) - Páginas institucionais
- [Core](apps/core.md) - Utilitários e componentes compartilhados

### 🔌 API
- [Visão Geral da API REST](api/overview.md)
- [Autenticação](api/authentication.md)
- [Endpoints](api/endpoints.md)
- [Serializers](api/serializers.md)

### 🧪 Testes
- [Guia de Testes](testing.md)
- [Estratégia de Testes](testing/strategy.md)
- [Cobertura](testing/coverage.md)

### 🐳 Infraestrutura
- [Docker Setup](DOCKER.md)
- [Deploy](deployment/README.md)
- [Variáveis de Ambiente](deployment/environment.md)

### 🛠️ Desenvolvimento
- [Setup do Ambiente](development/setup.md)
- [Guia de Contribuição](development/contributing.md)
- [Code Style](development/code-style.md)

---

## 🚀 Começando

Se você é novo no projeto, recomendamos começar por:

1. **[Visão Geral da Arquitetura](architecture/overview.md)** - Entenda a estrutura geral do sistema
2. **[Setup do Ambiente](development/setup.md)** - Configure seu ambiente de desenvolvimento
3. **Documentação do app que você vai trabalhar** - Cada app tem sua documentação detalhada

---

## 📝 Convenções de Documentação

- **README.md nos apps**: Breve descrição (2-4 linhas) + link para documentação completa
- **docs/apps/**: Documentação técnica detalhada de cada aplicação
- **docs/architecture/**: Decisões arquiteturais e padrões do sistema
- **docs/api/**: Documentação da API REST

---

## 🔄 Atualização

Esta documentação é atualizada continuamente. Última atualização: **27 de novembro de 2025**

Para contribuir com a documentação, consulte o [Guia de Contribuição](development/contributing.md).

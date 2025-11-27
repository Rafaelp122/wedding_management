# 💍 Wedding Management System

Sistema completo para gestão de casamentos desenvolvido como projeto final na **FIRJAN SENAI São Gonçalo**, baseado em uma demanda real do **SAGA SENAI**.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#)

---

## 📋 Sobre o Projeto

Sistema web desenvolvido para auxiliar cerimonialistas e organizadores de eventos na **gestão completa de casamentos**, oferecendo ferramentas integradas para orçamentos, contratos digitais, itens, agendamento e muito mais — tudo em um único lugar.

**Status:** 🚧 Em desenvolvimento ativo  
**Início:** Março 2025 | **Conclusão prevista:** Dezembro 2025

---

## ✨ Principais Funcionalidades

- 💒 **Gestão de Casamentos** - Cadastro completo de eventos com informações de noivos, data e local
- 💰 **Orçamento Inteligente** - Controle financeiro com categorização de despesas e acompanhamento de pagamentos
- 📝 **Contratos Digitais** - Sistema de assinatura digital tripartite com auditoria completa e geração de PDF
- 🛍️ **Gestão de Itens** - Lista dinâmica de produtos/serviços com status de aquisição
- 📅 **Calendário de Eventos** - Agenda visual com compromissos e lembretes
- 👥 **Autenticação Completa** - Sistema de usuários com Django Allauth
- 🌐 **API REST** - Endpoints para integrações externas

---

## 🛠 Tecnologias

**Backend:** Python 3.12, Django 5.2, Django REST Framework 3.16  
**Frontend:** HTML5, CSS3, JavaScript, HTMX, Bootstrap 5  
**Banco de Dados:** PostgreSQL (produção), SQLite (desenvolvimento)  
**Tarefas Assíncronas:** Celery 5.4 + Redis 7  
**Infraestrutura:** Docker, Docker Compose, Nginx  

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.12+
- Docker e Docker Compose (para ambiente containerizado)
- Git

### Opção 1: Docker Completo (Recomendado para Testes)

```bash
# Clone o repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# Execute com Docker Compose
docker-compose up --build

# Acesse: http://localhost:8000
```

### Opção 2: Ambiente Local (Desenvolvimento Rápido)

```bash
# Clone o repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver

# Acesse: http://localhost:8000
```

---

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Com cobertura
pytest --cov=apps --cov-report=html

# Testes específicos de um app
python manage.py test apps.contracts
```

---

## 📁 Estrutura do Projeto

```
wedding_management/
├── apps/                   # Aplicações Django
│   ├── budget/            # Gestão de orçamentos
│   ├── contracts/         # Contratos digitais
│   ├── core/              # Utilitários compartilhados
│   ├── items/             # Gestão de itens
│   ├── pages/             # Páginas institucionais
│   ├── scheduler/         # Calendário de eventos
│   ├── users/             # Autenticação e usuários
│   └── weddings/          # Gestão de casamentos
├── docs/                   # Documentação técnica detalhada
├── static/                # Arquivos estáticos
├── templates/             # Templates globais
├── docker-compose.yml     # Configuração Docker
└── manage.py             # CLI do Django
```

---

## 📚 Documentação

### Visão Geral
- 📖 [Arquitetura do Sistema](docs/architecture/overview.md)
- 🏗️ [Decisões de Design](docs/architecture/design-decisions.md)
- 🔄 [Fluxo de Dados](docs/architecture/data-flow.md)

### Por Aplicação
- 💒 [Weddings](docs/apps/weddings.md) - Gestão de casamentos
- 📝 [Contracts](docs/apps/contracts.md) - Sistema de assinatura digital
- 🛍️ [Items](docs/apps/items.md) - Gestão de itens
- 💰 [Budget](docs/apps/budget.md) - Controle orçamentário
- 📅 [Scheduler](docs/apps/scheduler.md) - Calendário de eventos
- 👥 [Users](docs/apps/users.md) - Autenticação e usuários
- 🌐 [Pages](docs/apps/pages.md) - Páginas institucionais
- 🔧 [Core](docs/apps/core.md) - Utilitários compartilhados

### Desenvolvimento
- 🐳 [Docker Setup](docs/DOCKER.md)
- 🧪 [Guia de Testes](docs/testing.md)
- 🔌 [API REST](docs/api.md)

---

## 👥 Equipe

Projeto desenvolvido por **Rafael Pimenta** como trabalho de conclusão do curso técnico na FIRJAN SENAI São Gonçalo.

**Orientação:** SAGA SENAI  
**Instituição:** FIRJAN SENAI São Gonçalo  

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🔗 Links Úteis

- [Documentação do Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

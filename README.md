# 💍 Wedding Management System

Sistema completo para gestão de casamentos desenvolvido como projeto final na **FIRJAN SENAI São Gonçalo**, baseado em uma demanda real do **SAGA SENAI**.

Este sistema auxilia cerimonialistas e organizadores de eventos na gestão completa de casamentos, oferecendo ferramentas integradas para orçamentos, contratos, itens, agendamento e muito mais — tudo em um único lugar.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## � Sumário

- [📊 Status do Projeto](#-status-do-projeto)
- [✨ Funcionalidades](#-funcionalidades)
- [🛠 Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [🚀 Como Executar o Projeto](#-como-executar-o-projeto)
  - [📦 Opção 1: Docker Completo](#-opção-1-docker-completo-recomendado-para-teste)
  - [🔧 Opção 2: Docker Híbrido](#-opção-2-docker-híbrido-recomendado-para-desenvolvimento)
  - [💻 Opção 3: Local Puro](#-opção-3-local-puro-desenvolvimento-rápido)
- [📚 Documentação Adicional](#-documentação-adicional)
  - [📖 Documentação Geral](#-documentação-geral)
  - [📦 Documentação por App](#-documentação-por-app)
- [🧪 Testes](#-testes)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🤝 Contribuindo](#-contribuindo)
- [👥 Equipe](#-equipe)
- [📄 Licença](#-licença)
- [🔗 Links Úteis](#-links-úteis)

---

## �📊 Status do Projeto

🚧 **Em desenvolvimento ativo**  
📅 Início: Março 2025 | Previsão de conclusão: Dezembro 2025

---

## ✨ Funcionalidades

### 📋 Módulos Implementados

- ✅ **Gestão de Usuários** (`apps/users/`)
  - Sistema de autenticação completo com Django Allauth
  - Perfis de usuário personalizados
  - Controle de acesso e permissões

- ✅ **Gestão de Casamentos** (`apps/weddings/`)
  - Cadastro completo de eventos
  - Informações de noivos, data, local
  - Vinculação com outros módulos

- ✅ **Orçamento** (`apps/budget/`)
  - Criação de orçamentos detalhados
  - Estimativas de custo por categoria (decoração, buffet, fotografia, etc)
  - Controle de pagamentos

- ✅ **Contratos** (`apps/contracts/`)
  - Armazenamento de contratos com fornecedores
  - Alertas de vencimento automáticos via Celery
  - Upload de documentos PDF

- ✅ **Gestão de Itens** (`apps/items/`)
  - Lista dinâmica de itens essenciais
  - Status de aquisição (pendente, adquirido, cancelado)
  - Categorização e fornecedores

- ✅ **Agendador/Calendário** (`apps/scheduler/`)
  - Visão cronológica de atividades
  - Eventos e compromissos
  - Lembretes automáticos

- ✅ **Páginas Institucionais** (`apps/pages/`)
  - Landing page
  - Formulário de contato
  - Páginas informativas

- ✅ **API REST** (Django REST Framework)
  - Endpoints para todas as funcionalidades
  - Serializers e viewsets completos
  - Autenticação via token

---

## 🛠 Tecnologias Utilizadas

### Backend
- **Python 3.12** - Linguagem principal
- **Django 5.2** - Framework web
- **Django REST Framework 3.16** - API REST
- **Celery 5.4** - Tarefas assíncronas e agendadas
- **Redis 7** - Cache e broker do Celery

### Frontend
- **Django Templates** - Sistema de templates
- **Django HTMX 1.23** - Interatividade moderna
- **Bootstrap 5** - Framework CSS
- **JavaScript** - Interações dinâmicas

### Banco de Dados
- **PostgreSQL 16** - Banco de dados principal (produção)
- **SQLite** - Desenvolvimento rápido (opcional)

### Infraestrutura
- **Docker & Docker Compose** - Containerização
- **Gunicorn 23** - WSGI server (produção)
- **Nginx** - Proxy reverso e arquivos estáticos
- **GitHub Actions** - CI/CD (planejado)

### Bibliotecas Adicionais
- **Django Allauth** - Autenticação completa
- **Pillow** - Processamento de imagens
- **xhtml2pdf** - Geração de PDFs
- **Sentry** - Monitoramento de erros (produção)

---

## 🚀 Como Executar o Projeto

Você pode executar o projeto de **3 formas diferentes**. Escolha a que melhor se adapta ao seu workflow:

### 📦 Opção 1: Docker Completo (Recomendado para teste)

Executa todos os serviços em containers (PostgreSQL, Redis, Django, Celery, Nginx).

```bash
# Clone o repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# Configure variáveis de ambiente
cp .env.example .env

# Inicie todos os serviços
docker compose up -d

# Acesse a aplicação
# http://localhost (via Nginx)
# http://localhost/admin (painel admin)
```

**Credenciais padrão:** admin / admin123 (altere no `.env`)

### 🔧 Opção 2: Docker Híbrido (Recomendado para desenvolvimento)

Executa apenas DB e Redis em Docker, Django roda localmente (hot-reload instantâneo).

```bash
# Clone o repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# Inicie apenas DB e Redis
docker compose -f docker-compose.local.yml up -d

# Crie e ative ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements/local.txt

# Configure variáveis de ambiente
cp .env.example .env

# Execute migrações
python manage.py migrate

# Crie superusuário
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver

# Acesse: http://localhost:8000
```

### 💻 Opção 3: Local Puro (Desenvolvimento rápido)

Executa tudo localmente sem Docker (SQLite).

```bash
# Clone o repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# Crie e ative ambiente virtual
python -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements/local.txt

# Configure para usar SQLite (edite .env)
cp .env.example .env
# Certifique-se que DEBUG=True

# Execute migrações
python manage.py migrate

# Crie superusuário
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver

# Acesse: http://localhost:8000
```

---

## 📚 Documentação Adicional

### 📖 Documentação Geral
- **[DOCKER.md](DOCKER.md)** - Guia completo de Docker, ambientes, troubleshooting, deploy
- **[Makefile](Makefile)** - Comandos úteis (`make help` para ver todos)
- **[docs/SENTRY_SETUP.md](docs/SENTRY_SETUP.md)** - Configuração do Sentry para monitoramento

### 📦 Documentação por App

Cada app possui documentação detalhada sobre arquitetura, testes, padrões e lições aprendidas:

| App | Descrição | README | Testes | Versão |
|-----|-----------|--------|--------|--------|
| **core** | Base compartilhada (mixins, utils, tasks, models) | [📄 README](apps/core/README.md) | 34 ✅ | Atual |
| **core/mixins** | Mixins reutilizáveis (auth, forms, views) | [📄 README](apps/core/mixins/README.md) | 30 ✅ | Atual |
| **weddings** | Gestão de casamentos (Web + API REST) | [📄 README](apps/weddings/README.md) | 60 ✅ | v3.0 |
| **items** | Itens de orçamento com contratos automáticos | [📄 README](apps/items/README.md) | 57 ✅ | v3.0 |
| **scheduler** | Calendário e eventos com FullCalendar | [📄 README](apps/scheduler/README.md) | 61 ✅ | v2.0 |
| **budget** | Visão consolidada de orçamentos | [📄 README](apps/budget/README.md) | 6 ✅ | v1.0 |
| **pages** | Landing page e formulário de contato | [📄 README](apps/pages/README.md) | 19 ✅ | v1.0 |
| **contracts** | Contratos com fornecedores (OneToOne com Item) | [📄 README](apps/contracts/README.md) | 13 ✅ | v1.0 |
| **users** | Autenticação e perfis (Allauth + API) | [� README](apps/users/README.md) | 36 ✅ | v2.0 |
| **templates** | Estrutura de templates e herança | [📄 README](templates/README.md) | - | - |

**Total de testes:** 382 passando ✅

**Breakdown por App:**
- Core: 34 ✅ | Weddings: 60 ✅ | Items: 57 ✅ | Scheduler: 61 ✅
- Budget: 6 ✅ | Pages: 19 ✅ | Contracts: 13 ✅ | Users: 36 ✅
- Mixins (core): 30 ✅

---

## 🧪 Testes

```bash
# Com Docker
docker compose exec web python manage.py test

# Ou com pytest e coverage
docker compose exec web pytest --cov=apps --cov-report=html

# Local
python manage.py test
pytest --cov=apps --cov-report=html
```

Relatório de cobertura disponível em `htmlcov/index.html`

---

## 📁 Estrutura do Projeto

```
wedding_management/
├── apps/                          # Aplicações Django
│   ├── users/                    # Autenticação e perfis
│   ├── weddings/                 # Gestão de casamentos
│   ├── budget/                   # Orçamentos
│   ├── contracts/                # Contratos
│   ├── items/                    # Itens do casamento
│   ├── scheduler/                # Calendário e eventos
│   ├── pages/                    # Páginas institucionais
│   └── core/                     # Funcionalidades compartilhadas
├── wedding_management/            # Configurações do projeto
│   ├── settings/                 # Settings por ambiente
│   │   ├── base.py              # Configurações base
│   │   ├── local.py             # Desenvolvimento
│   │   ├── production.py        # Produção
│   │   └── test.py              # Testes
│   ├── urls.py                   # URLs principais
│   └── wsgi.py                   # WSGI application
├── templates/                     # Templates HTML
├── static/                       # Arquivos estáticos
├── media/                        # Uploads de usuários
├── requirements/                  # Dependências Python
│   ├── base.txt                 # Comuns
│   ├── local.txt                # Desenvolvimento
│   ├── production.txt           # Produção
│   └── test.txt                 # Testes
├── docker-compose.yml            # Docker completo
├── docker-compose.local.yml      # Docker minimalista
├── Dockerfile                    # Imagem Docker
├── Makefile                      # Comandos úteis
├── manage.py                     # Django CLI
└── README.md                     # Este arquivo
```

---

## 🤝 Contribuindo

Este é um projeto acadêmico, mas contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 👥 Equipe

Projeto desenvolvido por alunos da **FIRJAN SENAI São Gonçalo** como trabalho de conclusão de curso.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🔗 Links Úteis

- [Documentação Django](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

**Desenvolvido com ❤️ na FIRJAN SENAI São Gonçalo**

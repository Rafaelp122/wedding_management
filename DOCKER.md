# 🐳 Guia Completo Docker - Wedding Management

## 📋 Índice
1. [Visão Geral](#-visão-geral)
2. [Diferença entre docker-compose.yml e docker-compose.local.yml](#-diferença-entre-os-arquivos-docker-compose)
3. [Pré-requisitos](#-pré-requisitos)
4. [Quick Start](#-quick-start)
5. [Gerenciamento de Ambientes](#-gerenciamento-de-ambientes)
6. [Comandos Comuns](#-comandos-comuns)
7. [Desenvolvimento Local Híbrido](#-desenvolvimento-local-híbrido)
8. [Monitoramento](#-monitoramento)
9. [Testes](#-testes)
10. [Troubleshooting](#-troubleshooting)
11. [Deploy para Produção](#-deploy-para-produção)

---

## 🔍 Visão Geral

Este projeto utiliza Docker Compose para orquestrar múltiplos serviços:

- **PostgreSQL 16**: Banco de dados
- **Redis 7**: Cache e broker do Celery
- **Django + Gunicorn**: Aplicação web
- **Celery Worker**: Tarefas em background
- **Celery Beat**: Tarefas agendadas
- **Nginx**: Proxy reverso e servidor de arquivos estáticos

---

## 📂 Diferença entre os arquivos docker-compose

### **docker-compose.yml** (Desenvolvimento Completo / Produção)

✅ **Contém TODOS os serviços:**
- PostgreSQL (porta 5433)
- Redis
- Django Web (com Gunicorn)
- Celery Worker
- Celery Beat
- Nginx

✅ **Ideal para:**
- Testar aplicação completa em containers
- Simular ambiente de produção
- Deploy em servidor
- Quando você quer tudo "containerizado"

✅ **Uso:**
```bash
docker compose up -d
# Acessa em: http://localhost (Nginx) ou http://localhost:8000 (Django direto)
```

### **docker-compose.local.yml** (Desenvolvimento Local Minimalista)

✅ **Contém APENAS serviços de apoio:**
- PostgreSQL (porta 5432)
- Redis
- Celery Worker (opcional)

❌ **NÃO contém:**
- Django Web (você roda localmente: `python manage.py runserver`)
- Nginx (acesso direto ao Django)

✅ **Ideal para:**
- Desenvolvimento ágil
- Debug facilitado (breakpoints funcionam normalmente)
- Hot-reload rápido do Django
- Economizar recursos do sistema
- Quando você quer editar código e ver mudanças instantaneamente

✅ **Uso:**
```bash
docker compose -f docker-compose.local.yml up -d
python manage.py runserver  # Django roda na sua máquina
# Acessa em: http://localhost:8000
```

### 💡 Resumo da Diferença

| Aspecto | docker-compose.yml | docker-compose.local.yml |
|---------|-------------------|-------------------------|
| **Django** | ✅ Container (Gunicorn) | ❌ Roda na máquina local |
| **PostgreSQL** | ✅ Porta 5433 | ✅ Porta 5432 |
| **Redis** | ✅ Container | ✅ Container |
| **Celery** | ✅ Worker + Beat | ✅ Só Worker |
| **Nginx** | ✅ Container | ❌ Não usa |
| **Uso** | Completo/Produção | Dev rápido |

---

## 📋 Pré-requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.10+ (para desenvolvimento local híbrido)
- Make (opcional, para comandos mais fáceis)

---

## 🚀 Quick Start

### 1. Clone e Configure

```bash
# Clone o repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# Copie o arquivo de ambiente
cp .env.example .env

# Edite o .env com suas configurações
nano .env
```

### 2. Escolha seu Modo de Desenvolvimento

#### **Opção A: Tudo em Docker (Completo)**

```bash
# Build e inicie todos os serviços
make build
make up

# Ou sem Make:
docker compose build
docker compose up -d
```

**Acesso:**
- Web: http://localhost (via Nginx)
- Admin: http://localhost/admin
  - Username: admin
  - Password: admin123 (altere no `.env`)

#### **Opção B: Desenvolvimento Local Híbrido (Recomendado para dev)**

```bash
# Inicie apenas DB e Redis
make local-up

# Ou sem Make:
docker compose -f docker-compose.local.yml up -d

# Em outro terminal, rode Django localmente
python manage.py migrate
python manage.py runserver

# (Opcional) Em outro terminal, rode Celery
celery -A wedding_management worker --loglevel=info
```

**Acesso:**
- Web: http://localhost:8000 (Django direto)
- Admin: http://localhost:8000/admin

---

## 🔄 Gerenciamento de Ambientes

### Ambientes Disponíveis

1. **Local** (`wedding_management.settings.local`)
   - DEBUG=True
   - SQLite ou PostgreSQL
   - Logs detalhados
   - Email no console
   - Menos seguro, mais verboso

2. **Production** (`wedding_management.settings.production`)
   - DEBUG=False
   - PostgreSQL obrigatório
   - HTTPS obrigatório
   - Email via SMTP
   - Segurança máxima

3. **Test** (`wedding_management.settings.test`)
   - Banco em memória
   - Velocidade máxima
   - Para testes apenas

### Como Trocar de Ambiente

#### **Método 1: Via arquivo .env** (Recomendado)

Edite o `.env`:

```bash
# Para desenvolvimento
DJANGO_SETTINGS_MODULE=wedding_management.settings.local

# Para produção
DJANGO_SETTINGS_MODULE=wedding_management.settings.production

# Para testes
DJANGO_SETTINGS_MODULE=wedding_management.settings.test
```

Depois reinicie os containers:

```bash
docker compose down
docker compose up -d
```

#### **Método 2: Editando docker-compose.yml**

Edite a seção `environment` nos serviços `web`, `celery_worker` e `celery_beat`:

```yaml
environment:
  - DJANGO_SETTINGS_MODULE=wedding_management.settings.production
```

#### **Método 3: Via linha de comando**

```bash
# Sobrescrever temporariamente
docker compose run -e DJANGO_SETTINGS_MODULE=wedding_management.settings.test web python manage.py test
```

### Ver Configuração Atual

```bash
docker compose exec web python -c "from django.conf import settings; print(f'Settings: {settings.SETTINGS_MODULE}'); print(f'DEBUG: {settings.DEBUG}')"
```

---

## 🛠 Comandos Comuns

### Usando Make (Recomendado)

```bash
make help              # Mostra todos os comandos disponíveis
make build             # Build das imagens Docker
make up                # Inicia todos os serviços
make down              # Para todos os serviços
make restart           # Reinicia todos os serviços
make logs              # Mostra logs de todos os serviços
make logs-web          # Mostra logs apenas do web
make logs-celery       # Mostra logs do Celery worker
make shell             # Abre Django shell
make bash              # Abre bash no container web
make migrate           # Executa migrações
make makemigrations    # Cria novas migrações
make createsuperuser   # Cria superusuário
make collectstatic     # Coleta arquivos estáticos
make test              # Executa testes
make test-coverage     # Executa testes com coverage
make clean             # Remove containers, volumes e orphans
make ps                # Mostra containers rodando
```

### Desenvolvimento Local (sem Docker completo)

```bash
make local-up          # Inicia apenas DB e Redis
make local-down        # Para DB e Redis
make runserver         # Roda Django localmente
make celery-worker     # Roda Celery worker localmente
make celery-beat       # Roda Celery beat localmente
```

### Usando Docker Compose Diretamente

```bash
# Gerenciamento básico
docker compose up -d                    # Inicia em background
docker compose down                     # Para os serviços
docker compose ps                       # Lista containers
docker compose logs -f web              # Logs em tempo real

# Comandos Django
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell
docker compose exec web python manage.py collectstatic

# Testes
docker compose exec web python manage.py test
docker compose exec web pytest
docker compose exec web pytest --cov=apps --cov-report=html
```

---

## 💻 Desenvolvimento Local Híbrido

Este modo permite rodar PostgreSQL e Redis em Docker, mas Django na sua máquina local.

### Vantagens

✅ Debug facilitado (breakpoints funcionam)  
✅ Hot-reload instantâneo  
✅ Menos recursos consumidos  
✅ Mais controle sobre o Django  
✅ Acesso direto aos logs  

### Configuração

```bash
# 1. Inicie apenas DB e Redis
docker compose -f docker-compose.local.yml up -d

# 2. Instale dependências (se ainda não fez)
pip install -r requirements/local.txt

# 3. Configure variáveis de ambiente
export DJANGO_SETTINGS_MODULE=wedding_management.settings.local

# 4. Execute migrações
python manage.py migrate

# 5. Rode o servidor
python manage.py runserver 0.0.0.0:8000
```

### Rodando Celery Localmente

```bash
# Terminal 1: Celery Worker
celery -A wedding_management worker --loglevel=info

# Terminal 2: Celery Beat (tarefas agendadas)
celery -A wedding_management beat --loglevel=info
```

### Parando Serviços Locais

```bash
docker compose -f docker-compose.local.yml down
```

---

## 📊 Monitoramento

### Visualizar Logs

```bash
# Todos os serviços
docker compose logs -f

# Serviço específico
docker compose logs -f web
docker compose logs -f celery_worker
docker compose logs -f celery_beat
docker compose logs -f nginx

# Últimas 100 linhas
docker compose logs --tail=100 web
```

### Status dos Serviços

```bash
make ps

# Ou:
docker compose ps

# Detalhado:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Acesso ao Banco de Dados

```bash
# PostgreSQL shell
docker compose exec db psql -U postgres -d wedding_management

# Ou via Django dbshell
docker compose exec web python manage.py dbshell

# Comandos úteis no psql:
# \dt               - Lista tabelas
# \d+ nome_tabela  - Descreve tabela
# \q               - Sair
```

### Acesso ao Redis

```bash
# Redis CLI
docker compose exec redis redis-cli

# Verificar chaves
docker compose exec redis redis-cli KEYS '*'

# Monitorar comandos em tempo real
docker compose exec redis redis-cli MONITOR
```

### Monitorar Celery

```bash
# Logs do worker
docker compose logs -f celery_worker

# Logs do beat
docker compose logs -f celery_beat

# Inspecionar tarefas ativas
docker compose exec celery_worker celery -A wedding_management inspect active

# Ver tarefas registradas
docker compose exec celery_worker celery -A wedding_management inspect registered

# Status dos workers
docker compose exec celery_worker celery -A wedding_management inspect stats
```

---

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
make test

# Ou:
docker compose exec web python manage.py test

# Teste específico
docker compose exec web python manage.py test apps.users.tests
docker compose exec web python manage.py test apps.users.tests.TestUserModel
```

### Testes com Pytest

```bash
# Todos os testes
docker compose exec web pytest

# Com cobertura
make test-coverage

# Ou:
docker compose exec web pytest --cov=apps --cov-report=html

# Teste específico
docker compose exec web pytest apps/users/tests/test_models.py
docker compose exec web pytest apps/users/tests/test_models.py::test_user_creation -v
```

### Ver Relatório de Cobertura

Após rodar `make test-coverage`, abra:

```bash
# O relatório HTML será gerado em htmlcov/
firefox htmlcov/index.html
# Ou:
xdg-open htmlcov/index.html
```

---

## 🚨 Troubleshooting

### Serviços não iniciam

```bash
# Verifique os logs
docker compose logs

# Rebuild sem cache
docker compose build --no-cache
docker compose up -d

# Verifique se as portas estão disponíveis
sudo netstat -tulpn | grep -E ':(80|443|5432|5433|6379|8000)'
```

### Erro de conexão com banco de dados

```bash
# Verifique se o DB está rodando
docker compose ps db

# Veja os logs do DB
docker compose logs db

# Reinicie o serviço
docker compose restart db

# Teste a conexão
docker compose exec db pg_isready -U postgres
```

### Arquivos estáticos não carregam

```bash
# Colete os arquivos estáticos
make collectstatic

# Ou:
docker compose exec web python manage.py collectstatic --noinput

# Verifique as permissões
docker compose exec web ls -la /app/staticfiles
```

### Erro de migração

```bash
# Verifique migrações pendentes
docker compose exec web python manage.py showmigrations

# Force a migração
docker compose exec web python manage.py migrate --run-syncdb

# Fake migration (use com cuidado!)
docker compose exec web python manage.py migrate --fake nome_app
```

### Container reiniciando constantemente

```bash
# Veja os logs
docker compose logs web

# Entre no container (se estiver rodando)
docker compose exec web bash

# Ou force um shell sem executar o comando
docker compose run --rm web bash
```

### Resetar tudo e começar do zero

```bash
# Para e remove tudo
make clean

# Ou:
docker compose down -v --remove-orphans

# Remove também as imagens
docker compose down -v --remove-orphans --rmi all

# Rebuild completo
docker compose build --no-cache
docker compose up -d
```

### Porta já em uso

Se a porta 80, 8000 ou 5432 estiver em uso:

```bash
# Descubra qual processo está usando
sudo lsof -i :8000
sudo lsof -i :80
sudo lsof -i :5432

# Mate o processo (substitua PID)
sudo kill -9 PID

# Ou altere a porta no docker-compose.yml:
# ports:
#   - "8001:8000"  # Mudou de 8000 para 8001
```

---

## 🚀 Deploy para Produção

### Checklist Pré-Deploy

- [ ] Configurar SECRET_KEY segura (50+ caracteres aleatórios)
- [ ] Configurar ALLOWED_HOSTS com domínios reais
- [ ] Configurar email SMTP (EMAIL_HOST, EMAIL_PORT, etc)
- [ ] Configurar certificados SSL para HTTPS
- [ ] Configurar Sentry para monitoramento (opcional)
- [ ] Revisar todas as variáveis no .env
- [ ] Fazer backup do banco de dados
- [ ] Testar em ambiente de staging primeiro
- [ ] Desabilitar DEBUG (DEBUG=False)
- [ ] Configurar senhas fortes para PostgreSQL
- [ ] Configurar firewall e security groups

### Exemplo de .env para Produção

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=wedding_management.settings.production
SECRET_KEY=sua-chave-super-secreta-com-50-caracteres-aleatorios-aqui
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Database
POSTGRES_DB=wedding_production
POSTGRES_USER=wedding_user
POSTGRES_PASSWORD=senha-super-segura-e-complexa-aqui
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis & Celery
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-aplicativo-gmail

# Superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@seudominio.com
DJANGO_SUPERUSER_PASSWORD=senha-super-segura-para-admin

# Sentry (Opcional - Monitoramento de erros)
SENTRY_DSN=https://seu-dsn@sentry.io/projeto
```

### Passos de Deploy

```bash
# 1. No servidor, clone o repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# 2. Configure o .env para produção
cp .env.example .env
nano .env  # Edite com valores de produção

# 3. Build das imagens
docker compose build

# 4. Inicie os serviços
docker compose up -d

# 5. Verifique o status
docker compose ps
docker compose logs -f web

# 6. Crie superuser (se necessário)
docker compose exec web python manage.py createsuperuser

# 7. Backup do banco
docker compose exec db pg_dump -U postgres wedding_production > backup_$(date +%Y%m%d).sql
```

### Atualizações em Produção

```bash
# 1. Pull do código atualizado
git pull origin main

# 2. Rebuild se necessário
docker compose build

# 3. Pare e inicie os serviços
docker compose down
docker compose up -d

# 4. Execute migrações
docker compose exec web python manage.py migrate

# 5. Colete estáticos
docker compose exec web python manage.py collectstatic --noinput

# 6. Verifique logs
docker compose logs -f web
```

### Backup Automatizado

Adicione ao crontab do servidor:

```bash
# Backup diário às 2h da manhã
0 2 * * * cd /caminho/para/wedding_management && docker compose exec -T db pg_dump -U postgres wedding_production | gzip > /backups/wedding_$(date +\%Y\%m\%d).sql.gz
```

---

## 📝 Estrutura do Projeto

```
wedding_management/
├── docker-compose.yml              # Setup completo (dev/prod)
├── docker-compose.local.yml        # Setup mínimo (dev local)
├── Dockerfile                      # Imagem Django
├── entrypoint.sh                   # Script de inicialização
├── Makefile                        # Atalhos de comandos
├── .env                            # Variáveis de ambiente (não versionar!)
├── .env.example                    # Template de variáveis
├── .dockerignore                   # Arquivos ignorados no build
├── nginx/                          # Configuração Nginx
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
├── requirements/                   # Dependências Python
│   ├── base.txt                   # Comuns
│   ├── local.txt                  # Desenvolvimento
│   ├── production.txt             # Produção
│   └── test.txt                   # Testes
├── wedding_management/             # Configurações Django
│   └── settings/
│       ├── __init__.py
│       ├── base.py                # Configurações base
│       ├── local.py               # Dev local
│       ├── production.py          # Produção
│       └── test.py                # Testes
└── apps/                          # Apps Django
    ├── users/
    ├── weddings/
    ├── budget/
    ├── contracts/
    └── ...
```

---

## 🔗 Links Úteis

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

---

## 💡 Dicas Finais

1. **Use `docker-compose.local.yml` para desenvolvimento diário** - É mais rápido e eficiente
2. **Use `docker-compose.yml` para testar em ambiente similar à produção**
3. **Sempre faça backup do banco antes de migrations grandes**
4. **Use `.env` para variáveis sensíveis, nunca commite este arquivo**
5. **Configure Sentry em produção para monitorar erros**
6. **Use `make` para comandos mais rápidos**
7. **Rode testes regularmente: `make test-coverage`**
8. **Verifique logs com frequência: `make logs`**

---

**Última atualização:** Novembro 2025

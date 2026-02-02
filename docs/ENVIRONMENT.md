# 🔐 Guia de Configuração de Ambiente

## Visão Geral

O sistema utiliza variáveis de ambiente para configuração sensível e específica do ambiente. **Nunca commite o arquivo `.env` no Git!**

### ⚡ Tecnologias de Build

- **BuildKit:** Habilitado automaticamente via Makefile para builds otimizados com cache
- **UV Package Manager:** Gerenciador ultra-rápido (10-100x mais rápido que pip)
- **Multi-stage Docker builds:** 4 stages (base → builder → development → production)
- **Dependency Management:** pyproject.toml (PEP 621) + uv.lock para reprodutibilidade

## Setup Rápido

```bash
# 1. Criar arquivo .env
make env-setup

# 2. Gerar SECRET_KEY segura (usa Python secrets.token_urlsafe)
make secret-key

# 3. Copiar SECRET_KEY gerada e colar no .env
nano .env  # ou seu editor preferido

# 4. Iniciar containers (build + up + migrations + logs)
make up

# 5. Criar superusuário (login com email)
make superuser
```

**Nota:** O sistema usa **email como USERNAME_FIELD**, não username.

## Variáveis de Ambiente

### 🔑 Django Core

| Variável        | Obrigatória | Padrão                | Descrição                                               |
| --------------- | ----------- | --------------------- | ------------------------------------------------------- |
| `SECRET_KEY`    | ✅ Sim      | -                     | Chave criptográfica Django. Gerar com `make secret-key` |
| `DEBUG`         | Não         | `True`                | Modo debug. **SEMPRE `False` em produção!**             |
| `ALLOWED_HOSTS` | Prod        | `localhost,127.0.0.1` | Hosts permitidos (separados por vírgula)                |

### 🗄️ Database

| Variável      | Obrigatória | Padrão         | Descrição                                           |
| ------------- | ----------- | -------------- | --------------------------------------------------- |
| `DB_ENGINE`   | Não         | `postgresql`   | Engine do banco (`postgresql` ou `sqlite3`)         |
| `DB_NAME`     | Não         | `wedding_db`   | Nome do banco de dados                              |
| `DB_USER`     | Não         | `wedding_user` | Usuário do PostgreSQL                               |
| `DB_PASSWORD` | Não         | `wedding_pass` | Senha do PostgreSQL                                 |
| `DB_HOST`     | Não         | `db`           | Host do banco (`db` para Docker, `localhost` local) |
| `DB_PORT`     | Não         | `5432`         | Porta do PostgreSQL                                 |

### 🔐 JWT Authentication

| Variável                        | Obrigatória | Padrão | Descrição                            |
| ------------------------------- | ----------- | ------ | ------------------------------------ |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | Não         | `15`   | Duração do token de acesso (minutos) |
| `REFRESH_TOKEN_LIFETIME_DAYS`   | Não         | `7`    | Duração do token de refresh (dias)   |

### 🌐 CORS & Security

| Variável               | Obrigatória | Padrão                      | Descrição                                            |
| ---------------------- | ----------- | --------------------------- | ---------------------------------------------------- |
| `CORS_ALLOWED_ORIGINS` | Não         | `http://localhost:5173,...` | Origens permitidas para CORS (separadas por vírgula) |

### 📧 Email (Produção)

| Variável              | Obrigatória | Padrão           | Descrição             |
| --------------------- | ----------- | ---------------- | --------------------- |
| `EMAIL_BACKEND`       | Não         | `console`        | Backend de email      |
| `EMAIL_HOST`          | Prod        | `smtp.gmail.com` | Host SMTP             |
| `EMAIL_PORT`          | Prod        | `587`            | Porta SMTP            |
| `EMAIL_USE_TLS`       | Prod        | `True`           | Usar TLS              |
| `EMAIL_HOST_USER`     | Prod        | -                | Email do remetente    |
| `EMAIL_HOST_PASSWORD` | Prod        | -                | Senha ou App Password |

### 🔴 Redis & Celery (Futuro)

| Variável                | Obrigatória | Padrão                 | Descrição             |
| ----------------------- | ----------- | ---------------------- | --------------------- |
| `REDIS_HOST`            | Não         | `redis`                | Host do Redis         |
| `REDIS_PORT`            | Não         | `6379`                 | Porta do Redis        |
| `CELERY_BROKER_URL`     | Não         | `redis://redis:6379/0` | URL do broker Celery  |
| `CELERY_RESULT_BACKEND` | Não         | `redis://redis:6379/0` | Backend de resultados |

### 📊 Monitoring (Opcional)

| Variável                    | Obrigatória | Padrão        | Descrição                                 |
| --------------------------- | ----------- | ------------- | ----------------------------------------- |
| `SENTRY_DSN`                | Não         | -             | DSN do Sentry para monitoramento de erros |
| `SENTRY_ENVIRONMENT`        | Não         | `development` | Ambiente Sentry                           |
| `SENTRY_TRACES_SAMPLE_RATE` | Não         | `0.1`         | Taxa de amostragem de traces              |

## Ambientes

### 🛠️ Desenvolvimento (Docker)

```dotenv
SECRET_KEY=sua-chave-gerada-aqui
DEBUG=True
DB_HOST=db
DB_NAME=wedding_db
DB_USER=wedding_user
DB_PASSWORD=wedding_pass
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 🖥️ Desenvolvimento Local (sem Docker)

```dotenv
SECRET_KEY=sua-chave-gerada-aqui
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 🚀 Produção

```dotenv
SECRET_KEY=chave-super-segura-gerada-com-make-secret-key
DEBUG=False
ALLOWED_HOSTS=seudominio.com,api.seudominio.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=wedding_prod
DB_USER=wedding_prod_user
DB_PASSWORD=senha-forte-aleatoria
DB_HOST=db-server.example.com
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://seudominio.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@seudominio.com
EMAIL_HOST_PASSWORD=app-password-aqui
SENTRY_DSN=https://your-sentry-dsn-here
SENTRY_ENVIRONMENT=production
```

## Comandos Úteis

```bash
# Gerar nova SECRET_KEY
make secret-key

# Configurar .env inicial
make env-setup

# Verificar configuração Django
docker compose exec backend python manage.py check

# Ver configurações ativas
docker compose exec backend python manage.py diffsettings

# Shell Django para debug
make shell
```

## Segurança

### ✅ Boas Práticas

1. **NUNCA** commite o arquivo `.env` no Git
2. Use `make secret-key` para gerar SECRET_KEY única e aleatória
3. Sempre `DEBUG=False` em produção
4. Use HTTPS em produção (nunca HTTP)
5. Configure `ALLOWED_HOSTS` corretamente em produção
6. Use senhas fortes para banco de dados em produção
7. Habilite CORS apenas para origens confiáveis
8. Rotacione SECRET_KEY periodicamente em produção

### ⚠️ Checklist Pré-Deploy

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` única e complexa
- [ ] `ALLOWED_HOSTS` configurado
- [ ] Banco de dados em servidor dedicado
- [ ] CORS restrito a domínios específicos
- [ ] Email configurado corretamente
- [ ] Monitoramento (Sentry) ativado
- [ ] Backup automático do banco de dados
- [ ] Logs centralizados configurados

## Troubleshooting

### Erro: "SECRET_KEY not set"

```bash
# Gere uma nova chave
make secret-key

# Adicione ao .env
echo "SECRET_KEY=chave-gerada-aqui" >> .env
```

### Erro: "connection refused" (Database)

Verifique se o serviço do banco está rodando:

```bash
docker compose ps
docker compose logs db
```

Se usando Docker, certifique-se que `DB_HOST=db`.

### Erro: "Module not found" após adicionar pacote

**Causa:** Adicionou pacote no `pyproject.toml` mas não rebuilou o container.

```bash
# 1. Atualizar uv.lock
make reqs

# 2. Rebuild container (com cache, rápido ~10-15s)
make build
```

### Build muito lento

**Causa:** Usando `make rebuild` (--no-cache) desnecessariamente.

```bash
# Use make build (com cache) no dia-a-dia
make build  # ~10-15s

# Use make rebuild APENAS se cache estiver corrompido
make rebuild  # ~77s (refaz tudo)
```

### Hot reload não funciona

**Verificar:**

1. Volumes montados corretamente no docker-compose.yml
2. Container em modo development (target: development)
3. Logs do container: `make back-logs` ou `make front-logs`

**Django hot reload:**

```bash
# Deve aparecer nos logs:
# "Watching for file changes with StatReloader"
```

**Vite HMR:**

```bash
# Deve aparecer nos logs:
# "VITE v7.3.1  ready in XXXms"
# "HMR connected"
```

### CORS Errors no Frontend

Adicione a origem do frontend em `CORS_ALLOWED_ORIGINS`:

```dotenv
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Referências

- [Django Settings Best Practices](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [12 Factor App](https://12factor.net/)
- [OWASP Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)

# 🔐 Guia de Configuração de Ambiente

> **Nunca commite o arquivo `.env` no Git!**

## Configuração Inicial

```bash
cp .env.example .env  # Crie o arquivo de ambiente
make secret-key       # Gere uma SECRET_KEY segura
nano .env             # Edite e adicione a SECRET_KEY
```

**Importante:** O sistema usa **email** como login, não username.

---

## Variáveis de Ambiente

### Obrigatórias

| Variável     | Descrição                                           | Como gerar        |
| ------------ | --------------------------------------------------- | ----------------- |
| `SECRET_KEY` | Chave criptográfica Django                          | `make secret-key` |
| `DB_HOST`    | Host do banco (`db` para Docker, `localhost` local) | -                 |

### Opcionais (Desenvolvimento)

| Variável                        | Padrão                      | Descrição                                   |
| ------------------------------- | --------------------------- | ------------------------------------------- |
| `DEBUG`                         | `True`                      | Modo debug (**SEMPRE `False` em produção**) |
| `DB_NAME`                       | `wedding_db`                | Nome do banco de dados                      |
| `DB_USER`                       | `wedding_user`              | Usuário do PostgreSQL                       |
| `DB_PASSWORD`                   | `wedding_pass`              | Senha do PostgreSQL                         |
| `DB_PORT`                       | `5432`                      | Porta do PostgreSQL                         |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `15`                        | Duração do JWT (minutos)                    |
| `REFRESH_TOKEN_LIFETIME_DAYS`   | `7`                         | Duração do refresh token (dias)             |
| `CORS_ALLOWED_ORIGINS`          | `http://localhost:5173,...` | Origens permitidas (separadas por vírgula)  |

### Produção Apenas

| Variável              | Descrição                            |
| --------------------- | ------------------------------------ |
| `ALLOWED_HOSTS`       | Domínios permitidos (ex: `app.com`)  |
| `EMAIL_HOST`          | Servidor SMTP (ex: `smtp.gmail.com`) |
| `EMAIL_HOST_USER`     | Email remetente                      |
| `EMAIL_HOST_PASSWORD` | Senha ou App Password                |
| `SENTRY_DSN`          | URL do Sentry para logs de erro      |

---

## Exemplos de Configuração

### Docker (Desenvolvimento)

```dotenv
SECRET_KEY=sua-chave-gerada-aqui
DEBUG=True
DB_HOST=db
```

### Local (sem Docker)

```dotenv
SECRET_KEY=sua-chave-gerada-aqui
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_HOST=localhost
```

### Produção

```dotenv
SECRET_KEY=chave-super-segura-64-caracteres
DEBUG=False
ALLOWED_HOSTS=seudominio.com,api.seudominio.com
DB_HOST=db-server.example.com
DB_PASSWORD=senha-forte-aleatoria
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=noreply@seudominio.com
EMAIL_HOST_PASSWORD=app-password-aqui
SENTRY_DSN=https://your-sentry-dsn
```

---

## Comandos de Gestão

### Docker

```bash
make up              # Inicia sistema completo
make migrate         # Aplica migrações
make superuser       # Cria usuário admin
make shell           # Abre Django shell
make logs            # Ver logs de todos os serviços
```

### Local (sem Docker)

```bash
make local-install   # Setup inicial (.venv + dependências)
source backend/.venv/bin/activate
make local-run       # Inicia Django
make local-migrate   # Aplica migrações
make front-dev       # Inicia Vite
```

### Gerenciamento de Pacotes

```bash
# Backend - adicionar pacote Python
make back-install pkg=requests

# Frontend - adicionar pacote npm
make front-install pkg=lodash

# Atualizar lockfile após editar pyproject.toml
make reqs
```

### Banco de Dados

```bash
make makemigrations  # Criar migrações
make migrate         # Aplicar migrações
make db-reset        # ⚠️ APAGA TUDO E RECRIA
```

### Qualidade de Código

```bash
make lint            # Verificar problemas (Ruff)
make format          # Formatar código automaticamente
make test            # Executar testes
make test-cov        # Testes com cobertura
```

---

## Segurança e Boas Práticas

### ✅ Checklist Pré-Deploy

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` única e complexa (64+ caracteres)
- [ ] `ALLOWED_HOSTS` configurado com domínios reais
- [ ] Banco de dados com senha forte
- [ ] CORS restrito a domínios específicos
- [ ] Email SMTP configurado
- [ ] Monitoramento (Sentry) ativado
- [ ] Backups automáticos configurados

### ⚠️ Nunca Faça

- Commitar `.env` no Git
- Usar `DEBUG=True` em produção
- Deixar `ALLOWED_HOSTS=*`
- Usar senhas fracas no banco de dados
- Expor SECRET_KEY em logs ou mensagens de erro

---

## Referências

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [12 Factor App](https://12factor.net/)
- [OWASP Django Security](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)

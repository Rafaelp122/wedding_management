# 🔧 Guia de Troubleshooting

## Erros de Configuração

### "SECRET_KEY not set"

```bash
make secret-key       # Gera uma chave
nano .env             # Adicione SECRET_KEY=<chave-gerada>
```

### "connection refused" (Database)

**Causa:** PostgreSQL não está rodando ou `DB_HOST` incorreto

```bash
docker compose ps     # Verificar se container 'db' está UP
docker compose logs db

# Para Docker: DB_HOST=db
# Para local: DB_HOST=localhost
```

### CORS Errors no Frontend

**Causa:** Frontend não está na lista de origens permitidas

```dotenv
# .env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Erros de Build

### "Module not found" após adicionar pacote

**Causa:** Adicionou no `pyproject.toml` mas não atualizou o lockfile/container

```bash
make reqs            # Atualiza uv.lock
make build           # Rebuilda container
```

### Build extremamente lento

**Causa:** Usando `make rebuild` (sem cache) desnecessariamente

```bash
# ✅ Use no dia-a-dia (com cache)
make build           # ~10-15s

# ❌ Use APENAS se cache corrompido
make rebuild         # ~77s
```

### "uv lock failed"

**Causa:** Dependências incompatíveis no `pyproject.toml`

```bash
docker compose exec backend uv lock --verbose
# Ajuste as versões conflitantes no pyproject.toml
```

### Cache do BuildKit corrompido

```bash
docker builder prune -af   # Limpa cache
make build                 # Rebuild
```

---

## Erros de Execução

### Hot reload não funciona

**Verificar:**

1. Volumes montados no `docker-compose.yml`
2. Container em `target: development`
3. Logs do container

```bash
make back-logs       # Django deve mostrar "StatReloader"
make front-logs      # Vite deve mostrar "HMR connected"
```

### Migrações não aplicadas

```bash
docker compose ps               # Container backend rodando?
make migrate                    # Aplica migrações
docker compose logs backend     # Ver erros de migração
```

### "Port 8000 already in use"

```bash
make down            # Para todos os containers
make up              # Reinicia
```

---

## Erros de Banco de Dados

### "relation does not exist"

**Causa:** Migrations não aplicadas

```bash
make migrate
```

### Resetar banco completamente

**⚠️ APAGA TODOS OS DADOS**

```bash
make db-reset        # Deleta + recria + migra
make superuser       # Cria novo admin
```

---

## Erros de Celery (quando implementado)

### Tasks não executam

**Causa:** Worker não rodando ou fila travada

```bash
docker compose logs celery     # Ver logs do worker
make restart-celery            # Reinicia worker
```

### "Connection refused" no Redis

```bash
docker compose ps redis        # Redis rodando?
docker compose logs redis
```

---

## Erros de Testes

### Testes falhando por banco de dados

```bash
# Garantir que test database está limpo
pytest --create-db

# Rodar testes isoladamente
pytest apps/items/tests/test_models.py -v
```

### Cobertura baixa inesperada

```bash
# Ver quais linhas não estão cobertas
make test-cov
# Abre htmlcov/index.html no navegador
```

---

## Problemas de Performance

### API respondendo lento

**Diagnóstico:**

```python
# Ative o Django Debug Toolbar em desenvolvimento
# Procure por queries N+1

# Adicione select_related/prefetch_related
Wedding.objects.select_related('planner').all()
```

### Container usando muita memória

```bash
docker stats                   # Ver uso de recursos
docker system prune -a         # Limpar containers/images antigos
```

---

## Comandos de Diagnóstico

```bash
# Verificar configuração Django
docker compose exec backend python manage.py check

# Ver todas as configurações ativas
docker compose exec backend python manage.py diffsettings

# Shell Django para debug
make shell

# Ver logs de todos os serviços
make logs

# Testar conexão com banco
docker compose exec backend python manage.py dbshell
```

---

## Quando Pedir Ajuda

Antes de abrir um issue/pedir suporte, colete:

1. **Logs completos:**

   ```bash
   make logs > logs.txt
   ```

2. **Versões:**

   ```bash
   docker --version
   docker compose version
   python --version
   ```

3. **Arquivo `.env`** (REMOVA SECRET_KEY antes de compartilhar!)

4. **Comando exato que causou erro**

5. **Output do erro completo** (não apenas a última linha)

---

## Referências

- [Documentação Django](https://docs.djangoproject.com/)
- [Docker Compose Troubleshooting](https://docs.docker.com/compose/faq/)
- [UV Issues](https://github.com/astral-sh/uv/issues)

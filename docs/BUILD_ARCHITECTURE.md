# 🏗️ Arquitetura de Build e Dependências

## Visão Geral

O projeto utiliza tecnologias modernas para otimizar velocidade de build, reprodutibilidade e gestão de dependências.

## Gerenciamento de Dependências

### Backend: pyproject.toml + uv.lock

**pyproject.toml** (PEP 621 - padrão moderno Python):

```toml
[project]
dependencies = [
    "django>=5.2.9,<5.3",
    "djangorestframework>=3.16.1,<3.17",
    # ...
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.4,<9.0",
    "ruff>=0.7.4,<0.8",
    # ...
]
```

**uv.lock** (lockfile com hashes SHA256):

- Gerado automaticamente por `uv lock`
- 66 pacotes resolvidos (diretos + transitivos)
- Garante versões exatas em todos os ambientes
- **Deve ser commitado no git** (como package-lock.json no Node.js)

### UV Package Manager

[UV](https://github.com/astral-sh/uv) - Gerenciador ultra-rápido escrito em Rust:

**Vantagens:**

- ⚡ **10-100x mais rápido** que pip
- 🔒 Resolução de dependências determinística
- 💾 Cache agressivo e eficiente
- 🦀 Performance nativa (Rust)

**Comandos:**

```bash
# Instalar pacote e atualizar uv.lock
make back-install pkg=requests

# Apenas atualizar uv.lock (após editar pyproject.toml)
make reqs

# No container (manual)
docker compose exec backend uv lock
docker compose exec backend uv pip install --system nome-pacote
```

### Frontend: package.json + package-lock.json

Padrão NPM tradicional:

- `package.json` - Dependências diretas
- `package-lock.json` - Lockfile (commitado no git)
- Gerenciado por `npm ci` nos builds

## Multi-Stage Docker Builds

### Estratégia de 4 Stages

#### Stage 1: Base

```dockerfile
FROM python:3.11-slim AS base
# - Instala dependências de runtime (postgresql-client, libpq5)
# - Copia binário UV oficial
# - Usa cache mount do BuildKit para apt-get
```

#### Stage 2: Builder

```dockerfile
FROM base AS builder
# - Instala dependências de compilação (gcc, libpq-dev)
# - Exporta uv.lock para requirements.txt temporário
# - Instala pacotes Python com uv pip install --system
```

#### Stage 3: Development

```dockerfile
FROM base AS development
# - Herda do base (não do builder - mais leve)
# - Copia apenas pacotes Python instalados
# - Monta código via volume (hot reload)
# - Roda com Django runserver
```

#### Stage 4: Production

```dockerfile
FROM python:3.11-slim AS production
# - Imagem limpa sem dependências de build
# - Copia pacotes do builder
# - Roda como non-root user (segurança)
# - Usa Gunicorn com múltiplos workers
```

### BuildKit

**Habilitado automaticamente** via Makefile:

```makefile
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

**Features utilizadas:**

- `--mount=type=cache` - Cache persistente de apt-get e UV
- Layer caching inteligente
- Builds paralelos

## Performance de Build

### Tempos Típicos

**Com cache (make build):**

- Primeira vez: ~77s
- Rebuilds subsequentes: ~10-15s
- Apenas código mudou: 0s (hot reload)

**Sem cache (make rebuild):**

- Sempre: ~77s
- Não use no dia-a-dia!

### Otimizações Implementadas

1. **Cache mount do BuildKit:**

   ```dockerfile
   RUN --mount=type=cache,target=/var/cache/apt \
       apt-get update && apt-get install -y postgresql-client
   ```

   - Apt-get não baixa pacotes novamente
   - Economiza ~40s em rebuilds

2. **UV com cache:**

   ```dockerfile
   RUN --mount=type=cache,target=/root/.cache/uv \
       uv export --frozen --no-dev | uv pip install --system
   ```

   - UV reutiliza wheels baixados
   - Economiza ~8s em rebuilds

3. **Separação de stages:**
   - Development não inclui gcc/libpq-dev (~200MB menor)
   - Production não inclui ferramentas de dev

4. **Layer caching:**
   - pyproject.toml copiado antes do código
   - Dependências só reinstalam se pyproject.toml mudar

## Workflow de Dependências

### Adicionar Pacote Python

```bash
# 1. Editar backend/pyproject.toml
[project]
dependencies = [
    "requests>=2.31.0,<3.0",  # <- Adicionar aqui
]

# 2. Atualizar lockfile
make reqs

# 3. Rebuild container
make build

# 4. Verificar instalação
docker compose exec backend python -c "import requests; print(requests.__version__)"
```

### Adicionar Pacote npm

```bash
# 1. Instalar automaticamente
make front-install pkg=lodash

# 2. Rebuild container
make build
```

### Remover Pacote

```bash
# Python: Remover do pyproject.toml -> make reqs -> make build
# npm: Remover do package.json -> make build
```

## CI/CD - GitHub Actions

### Otimizações no Pipeline

**Backend CI:**

```yaml
- name: Install UV
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.cargo/bin" >> $GITHUB_PATH

- name: Install Ruff (version from pyproject.toml)
  run: uv pip install --system "ruff>=0.7.4,<0.8"
```

**Benefícios:**

- Usa mesma versão de Ruff que desenvolvimento local
- UV acelera instalação de dependências
- Cache de UV compartilhado entre builds

## Reprodutibilidade

### Garantias

✅ **pyproject.toml + uv.lock commitados:**

- Todos os desenvolvedores usam mesmas versões
- CI/CD usa mesmas versões
- Produção usa mesmas versões

✅ **Docker multi-stage:**

- Desenvolvimento e produção compartilham base
- Dependências de runtime idênticas

✅ **BuildKit determinístico:**

- Layers de cache consistentes
- Builds reproduzíveis

### Teste de Reprodutibilidade

```bash
# Em máquina 1
make rebuild
docker compose exec backend pip freeze > /tmp/freeze1.txt

# Em máquina 2 (mesmo commit)
make rebuild
docker compose exec backend pip freeze > /tmp/freeze2.txt

# Deve ser idêntico
diff /tmp/freeze1.txt /tmp/freeze2.txt
```

## Troubleshooting de Build

### "Module not found" após adicionar pacote

**Causa:** Esqueceu de atualizar uv.lock ou rebuildar.

**Solução:**

```bash
make reqs    # Atualiza uv.lock
make build   # Rebuilda container
```

### Build lento mesmo com cache

**Diagnóstico:**

```bash
# Ver camadas sendo cacheadas
DOCKER_BUILDKIT=1 docker compose build --progress=plain

# Procurar por linhas sem "CACHED"
```

**Possíveis causas:**

- Arquivo `.dockerignore` ausente ou incorreto
- Ordem de COPY no Dockerfile (código antes de dependências)
- Cache do BuildKit corrompido

**Solução:**

```bash
# Limpar cache do BuildKit
docker builder prune -af

# Rebuild
make build
```

### Erro "uv lock failed"

**Causa:** Dependências incompatíveis no pyproject.toml.

**Solução:**

```bash
# Ver erro detalhado
docker compose exec backend uv lock --verbose

# Ajustar versões no pyproject.toml
```

## Boas Práticas

### ✅ Fazer

- Commitar `pyproject.toml`, `uv.lock`, `package-lock.json`
- Usar `make build` (com cache) para rebuilds
- Testar em ambiente limpo antes de commit
- Documentar dependências opcionais

### ❌ Evitar

- Não commitar `.env` ou arquivos secretos
- Não usar `make rebuild` desnecessariamente
- Não editar `uv.lock` manualmente
- Não fazer `pip install` direto no container (usar pyproject.toml)
- Não usar versões exatas sem range (ex: `django==5.2.9` → `django>=5.2.9,<5.3`)

## Referências

- [UV Documentation](https://github.com/astral-sh/uv)
- [PEP 621 - pyproject.toml](https://peps.python.org/pep-0621/)
- [Docker BuildKit](https://docs.docker.com/build/buildkit/)
- [Multi-stage builds best practices](https://docs.docker.com/build/building/multi-stage/)

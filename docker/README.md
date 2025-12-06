# 🐳 Docker Configuration

Esta pasta contém todos os arquivos de configuração Docker do projeto.

## 📁 Arquivos

### Dockerfiles

- **`Dockerfile`** - Imagem de produção com multi-stage build (411MB)
  - Otimizada para deploy
  - Remove ferramentas de compilação da imagem final
  - 49.6% menor que a imagem de desenvolvimento

- **`Dockerfile.dev`** - Imagem de desenvolvimento (816MB)
  - Mantém gcc e ferramentas de desenvolvimento
  - Ideal para desenvolvimento em containers

### Docker Compose Files

- **`docker-compose.yml`** - Ambiente de desenvolvimento completo
  - Todos os serviços em containers
  - Usa `Dockerfile.dev`
  - Hot reload habilitado

- **`docker-compose.local.yml`** - Desenvolvimento híbrido
  - Apenas PostgreSQL e Redis em containers
  - Django roda localmente
  - Mais rápido para desenvolvimento

- **`docker-compose.prod.yml`** - Produção
  - Usa `Dockerfile` com multi-stage build
  - Nginx como proxy reverso
  - Configurações otimizadas para produção

## 🚀 Como Usar

### Desenvolvimento Completo

```bash
# Da raiz do projeto
docker compose -f docker/docker-compose.yml up -d

# Acessar logs
docker compose -f docker/docker-compose.yml logs -f web

# Parar
docker compose -f docker/docker-compose.yml down
```

### Desenvolvimento Híbrido (Recomendado)

```bash
# Da raiz do projeto
docker compose -f docker/docker-compose.local.yml up -d

# Rodar Django localmente
python manage.py runserver
```

### Produção

```bash
# Build e deploy
docker compose -f docker/docker-compose.prod.yml up -d --build

# Verificar status
docker compose -f docker/docker-compose.prod.yml ps
```

## 📊 Comparação de Imagens

| Dockerfile | Tamanho | Uso | Build Tools |
|------------|---------|-----|-------------|
| `Dockerfile` (prod) | 411MB | Produção | ❌ Removidos |
| `Dockerfile.dev` | 816MB | Desenvolvimento | ✅ Incluídos |

**Redução**: 49.6% menor em produção!

## 📚 Documentação Completa

Para mais detalhes, consulte: [../docs/DOCKER.md](../docs/DOCKER.md)

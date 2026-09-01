# ADR-017: Infraestrutura de Tarefas Assíncronas e Agendamentos com Django Tasks, Huey e Valkey

## Status
Aceito

## Data
Fevereiro 2026

## Decisores
Rafael, Antigravity AI

## Contexto

O sistema necessitava de uma solução para processamento de tarefas em segundo plano (uploads, notificações, eventos entre domínios) e agendamento de tarefas periódicas (como a atualização diária de parcelas vencidas e manutenção).

Requisitos fundamentais definidos para a infraestrutura:
1. **Zero Lock-In**: A aplicação não deve estar fortemente acoplada a nenhuma biblioteca de worker ou provedor de nuvem específico.
2. **Zero Custo Ocioso 24/7 em Produção**: O ambiente de produção no Google Cloud Run opera em modo Serverless (escala até zero). Não devem existir containers de worker ou instâncias de Redis rodando 24 horas por dia sem tráfego.
3. **Paridade e Produtividade Local**: No ambiente de desenvolvimento local (`docker-compose`), o desenvolvedor deve ter um ecossistema rápido e eficiente baseado em containers.

## Decisão

Adotaremos a **API nativa `django.tasks` do Django 6.0 (DEP 0014)** aliada ao **Huey** e **Valkey 8** em desenvolvimento local, e uma **Arquitetura On-Demand (Serverless)** em produção com **GCP Cloud Scheduler Batch (OIDC)**.

### Componentes Arquiteturais

1. **Camada de Aplicação (`django.tasks` - Django 6.0)**:
   - A lógica da aplicação utiliza **exclusivamente** a API nativa do Django 6.0 (`from django.tasks import task` e `my_task.enqueue()`).
   - A injeção de dependência da engine/executor é realizada via configuração (`TASKS["default"]` no `settings.py`).

2. **Ambiente de Desenvolvimento Local**:
   - **Engine / Worker**: **Huey** (`huey.contrib.djhuey.backend.HueyBackend`), executado via `python manage.py run_huey`.
   - **Message Broker & Cache**: **Valkey 8** (`valkey/valkey:8-alpine`), substituto 100% open-source e compatível com a API do Redis.
     - `DB 0`: Fila de mensagens do Huey.
     - `DB 1`: Cache do Django (`CACHES["default"]` via `RedisCache`).

3. **Ambiente de Testes Automatizados (`pytest`)**:
   - Backend síncrono `django.tasks.backends.immediate.ImmediateBackend`. Nenhuma dependência externa de container ou worker nos testes unitários.

4. **Ambiente de Produção (GCP Cloud Run)**:
   - **Tarefas sob Demanda**: `DatabaseTasksBackend` ou `CloudTasksBackend`. Execução descartável sem manter workers ligados 24/7.
   - **Tarefas Agendadas (Crons / Batch Diário)**: Um único agendador no **GCP Cloud Scheduler** faz uma requisição HTTP POST diária autenticada via **OIDC** (conforme [ADR-005](005-oidc-scheduler.md)) para a rota `/api/v1/internal/cron/daily-batch/`. O Cloud Run processa em lote em milissegundos e escala de volta para zero.

### Estrutura no Docker Compose (`docker-compose.yml`)

```yaml
  valkey:
    image: valkey/valkey:8-alpine
    container_name: wedding_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    networks:
      - wedding_network

  worker:
    build:
      context: ./backend
      target: development
    container_name: wedding_worker
    env_file:
      - .env
    command: python manage.py run_huey
    depends_on:
      db:
        condition: service_healthy
      valkey:
        condition: service_started
    networks:
      - wedding_network
```

## Consequências

### Positivas :material-check-circle:
- **Zero Lock-In**: O código do projeto usa apenas a interface padrão do Django 6.0.
- **Zero Custo Ocioso**: Produção no Cloud Run roda 100% On-Demand.
- **Cache + Tasks Unificados**: Valkey 8 atende tanto a fila de tarefas quanto o cache do backend em dev local.
- **Economia no GCP**: Cloud Scheduler Batch dispara apenas 1 requisição diária segura por OIDC.

### Negativas / Riscos :material-close-circle:
- Necessidade de manter o token OIDC validado no endpoint de cron diário em produção.

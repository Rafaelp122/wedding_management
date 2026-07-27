# ADR-017: Infraestrutura de Tarefas Assíncronas com Celery + Redis

## Status
Proposto

## Contexto

O sistema atual opera de forma puramente síncrona — toda requisição HTTP é processada
do início ao fim dentro do ciclo de vida da request. Isso limita três cenários
arquiteturais já identificados:

1. **Upload de arquivos em background**: O usuário faz upload de um PDF de contrato,
   mas o processamento (scan de vírus, extração de metadados, geração de thumbnail)
   não deveria bloquear a resposta HTTP.

2. **Arquitetura orientada a eventos via signals**: Múltiplos domínios (`weddings`,
   `finances`, `logistics`, `scheduler`) precisam reagir a eventos entre si de forma
   desacoplada. Exemplo: ao criar um casamento, o domínio `finances` deve criar
   automaticamente o orçamento e categorias padrão — sem que `weddings` conheça
   `finances`.

3. **Tarefas periódicas (cron)**: O comando `mark_overdue_installments` precisa
   executar diariamente para marcar parcelas vencidas como `OVERDUE`. Hoje ele é um
   management command sem mecanismo de agendamento.

## Alternativas Consideradas

### Cloud Run Jobs + Cloud Scheduler

- **Prós**: Simples para tarefas periódicas, sem infra adicional, custo baixo
  (cobra por execução).
- **Contras**: Não atende cenários sob demanda (upload em background, eventos entre
  domínios). Exigiria soluções diferentes para cada caso (Cloud Tasks para tarefas sob
  demanda + Cloud Scheduler para periódicas), fragmentando a stack.

### Cloud Tasks (GCP)

- **Prós**: Gerenciado, escala automaticamente, garantia de entrega.
- **Contras**: Integração com Django exige código customizado significativo.
  Ecossistema menos maduro que Celery para o universo Python/Django.

### Celery + Redis (escolhido)

- **Prós**: Resolve os três cenários com uma única stack. Ecossistema maduro no
  Django (django-celery-results, django-celery-beat). Suporte nativo a retry,
  rate-limiting, priorização de filas. Comunidade extensa.
- **Contras**: Adiciona 2-3 containers ao deploy e um serviço de Redis (custo
  adicional no GCP).

## Decisão

Adotaremos **Celery + Redis** como infraestrutura de tarefas assíncronas.

### Arquitetura

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ frontend │───▶│ backend  │───▶│  Redis   │───▶│  worker   │
│          │    │ (gunicorn)│   │ (broker) │    │ (celery)  │
└──────────┘    └──────────┘    └──────────┘    └───────────┘
                     │                                  │
                     │ (signals disparam)               │ (processa)
                     ▼                                  ▼
               ┌──────────┐                      ┌───────────┐
               │ Domain A │                      │  upload   │
               │  signal  │                      │  R2/S3    │
               └──────────┘                      └───────────┘
                     │
                     │ task.delay()
                     ▼
               ┌──────────┐    ┌──────────┐
               │ Domain B │    │  beat    │
               │ (worker) │    │ (cron)   │
               └──────────┘    └──────────┘
```

### Componentes

| Componente | Container | Função |
|---|---|---|
| **Redis 7 Alpine** | `redis` | Message broker — fila de tarefas |
| **Celery Worker** | `worker` | Processa tarefas assíncronas (upload, eventos) |
| **Celery Beat** | `beat` | Agendador de tarefas periódicas (cron) |

O Worker e o Beat **compartilham o mesmo código e imagem Docker** do backend —
apenas o entrypoint (`CMD`) difere.

### Configuração Django (`config/settings/base.py`)

```python
# Celery
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"
```

### docker-compose.yml (acréscimos)

```yaml
  redis:
    image: redis:7-alpine
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
    env_file: .env
    volumes:
      - ./backend:/app
      - /app/.venv
    command: celery -A config worker -l info
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - wedding_network

  beat:
    build:
      context: ./backend
      target: development
    container_name: wedding_beat
    env_file: .env
    volumes:
      - ./backend:/app
      - /app/.venv
    command: celery -A config beat -l info
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - wedding_network
```

### Estrutura de Tasks

```
backend/apps/core/tasks.py        # Tasks compartilhadas (upload, manutenção)
backend/apps/weddings/tasks.py    # Tasks do domínio weddings
backend/apps/finances/tasks.py    # Tasks do domínio finances
# ... etc por app
```

### Exemplo: Upload de arquivo em background

```python
# apps/core/tasks.py
from celery import shared_task

@shared_task
def process_uploaded_contract(contract_uuid: str) -> None:
    contract = Contract.objects.get(uuid=contract_uuid)
    # 1. Scan de vírus
    # 2. Extrair metadados do PDF
    # 3. Gerar thumbnail para preview
    pass
```

```python
# apps/logistics/services/contract_service.py (adaptado)
@staticmethod
def upload_file(company, instance, uploaded_file):
    instance.pdf_file.save(uploaded_file.name, uploaded_file, save=True)
    process_uploaded_contract.delay(str(instance.uuid))
    return instance
```

### Exemplo: Comunicação entre domínios via signal + task

```python
# apps/weddings/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.tasks import setup_wedding_budget

@receiver(post_save, sender=Wedding)
def on_wedding_created(sender, instance, created, **kwargs):
    if created:
        setup_wedding_budget.delay(
            str(instance.company.uuid), str(instance.uuid)
        )
```

### Exemplo: Tarefa periódica (substitui management command)

```python
# apps/finances/tasks.py
from celery import shared_task

@shared_task
def mark_overdue_installments() -> int:
    today = date.today()
    updated = Installment.objects.filter(
        status=Installment.StatusChoices.PENDING,
        due_date__lt=today,
    ).update(status=Installment.StatusChoices.OVERDUE)
    return updated
```

```python
# config/celery.py
app.conf.beat_schedule = {
    "mark-overdue-installments": {
        "task": "apps.finances.tasks.mark_overdue_installments",
        "schedule": crontab(hour=2, minute=0),  # diário às 02:00
    },
}
```

### Estratégia de Redis no GCP

Duas opções, por ordem de preferência:

1. **Sidecar no Cloud Run** (recomendado para MVP): Redis efêmero rodando como
   container auxiliar no mesmo serviço Cloud Run. Custo zero adicional (usa a
   mesma instância Cloud Run). Sem persistência — adequado para fila de tarefas
   (Celery tem retry nativo).

2. **Cloud Memorystore** (produção): Serviço gerenciado de Redis. Custa ~$35/mês
   na instância mínima. Oferece persistência e alta disponibilidade.

### Plano de Rollout

| Fase | Atividade |
|---|---|
| **Fase 1** | Instalar dependências (`celery`, `redis`), criar `config/celery.py`, configurar `CELERY_BROKER_URL` |
| **Fase 2** | Adicionar containers `redis`, `worker`, `beat` ao `docker-compose.yml` |
| **Fase 3** | Migrar `mark_overdue_installments` de management command para Celery Beat task |
| **Fase 4** | Criar `process_uploaded_contract` task e adaptar `ContractService.upload_file` |
| **Fase 5** | Implementar signals desacoplados entre domínios (weddings → finances, etc.) |
| **Fase 6** | Configurar Redis sidecar no Cloud Run (produção) |

## Consequências

- **Positivas**:
    - Upload de arquivos não bloqueia mais a resposta HTTP.
    - Domínios se comunicam de forma desacoplada via signals + tasks.
    - Tarefas periódicas executam automaticamente, sem depender de Cloud Scheduler.
    - Stack unificada para tarefas sob demanda e agendadas.
    - Infra preparada para futuras necessidades assíncronas (envio de emails,
      webhooks, relatórios, notificações).

- **Negativas**:
    - +3 containers no ambiente de desenvolvimento local.
    - Custo adicional de Redis no GCP em produção (~$35/mês com Memorystore, ou $0
      com sidecar).
    - Curva de aprendizado para o time (conceitos de Celery: tasks, retries, rates).
    - Debugging mais complexo (erros acontecem no worker, fora da request HTTP).

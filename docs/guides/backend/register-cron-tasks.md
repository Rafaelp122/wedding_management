# Como Registrar e Usar Tarefas Agendadas (Daily Batch Cron)

Este guia prático explica como criar e registrar rotinas de manutenção no sistema de agendamento em lote (**Daily Batch Cron**), conforme a [ADR-017](../../architecture/adr/017-async-task-infrastructure.md) e [ADR-005](../../architecture/adr/005-oidc-scheduler.md).

---

## 1. Âmbito do `CronRegistry`

O `cron_registry` padrão é dedicado exclusivamente a **tarefas de execução em lote diário (Daily Batch)** executadas uma vez ao dia (ex: 02:00 AM).

### Decisão Arquitetural: Quando usar o `CronRegistry` vs Novo Job Terraform

| Necessidade do Sistema | Solução Recomendada | Exemplo de Uso |
| :--- | :--- | :--- |
| **Manutenção Diária** | `@cron_registry.register("nome")` | Atualizar parcelas vencidas, limpar tokens expirados. |
| **Ação Pesada do Usuário** | `minha_tarefa.enqueue()` (`django.tasks`) | Exportar relatórios em PDF, importar arquivos Excel. |
| **Frequência Diferente** (ex: a cada 5 min ou de hora em hora) | Novo Endpoint + `@require_oidc_auth` + Job no Terraform | Conciliação de webhooks bancários de hora em hora. |

---

## 2. Passo a Passo para Criar uma Tarefa Cron Diária

### Passo 1: Criar ou editar o arquivo `cron.py` no app de destino
No diretório do seu app de domínio (ex: `apps/finances/cron.py` ou `apps/logistics/cron.py`), crie o arquivo `cron.py` e utilize o decorator `@cron_registry.register`.

```python
import logging
from apps.core.cron import cron_registry

logger = logging.getLogger(__name__)


@cron_registry.register(
    "nome_unico_da_tarefa",
    description="Descrição clara da rotina de manutenção realizada por esta função.",
)
def run_minha_rotina_diaria() -> str:
    """
    Executa a rotina de manutenção diária do módulo.
    Retorna uma string com o resumo da execução.
    """
    # Exemplo: chamar um serviço de domínio ou management command
    # registros_processados = MeuDomainService.processar_rotina_diaria()
    return "Rotina diária executada com sucesso."
```

---

### Passo 2: Registro Automático via Autodiscovery
O sistema possui **Autodiscovery de Crons** configurado no `CoreConfig.ready()` (`apps/core/apps.py`).

O Django varre automaticamente todos os `INSTALLED_APPS` procurando por arquivos `cron.py` no boot da aplicação. **Não é necessário importar o arquivo manualmente no `apps.py` do seu aplicativo.**

---

## 3. Tarefas Pesadas vs Tarefas Curtas (Timeout HTTP)

Para manter a resposta da requisição leve e evitar timeouts de requisição no Cloud Run (timeout de 300s):

1. **Tarefas Curtas (Queries SQL rápidas)**: Podem rodar diretamente de forma síncrona dentro da função decorada com `@cron_registry.register`.
2. **Tarefas Pesadas (Geração de PDFs, relatórios extensos, envios massivos)**: A função decorada deve fazer o dispatch assíncrono via `.enqueue()` utilizando a API nativa `django.tasks` (Django 6.0) e retornar imediatamente:

```python
from django.tasks import task
from apps.core.cron import cron_registry


@task
def processar_relatorios_pesados_async() -> None:
    # Lógica pesada em background
    ...


@cron_registry.register("disparar_relatorios_diarios", description="Agenda relatórios pesados")
def cron_disparar_relatorios() -> str:
    processar_relatorios_pesados_async.enqueue()
    return "Processamento assíncrono enfileirado com sucesso."
```

---

## 4. Testando o Endpoint Localmente

O lote de tarefas agendadas é disparado no endpoint `/api/v1/internal/cron/daily-batch/`.
Em desenvolvimento local ou testes, utilize o token `dev-cron-token`:

```bash
curl -X POST http://localhost:8000/api/v1/internal/cron/daily-batch/ \
  -H "Authorization: Bearer dev-cron-token" \
  -H "Content-Type: application/json"
```

### Resposta Esperada com Sucesso (HTTP 200 OK)
```json
{
  "status": "completed",
  "timestamp": "2026-08-08T02:00:00.000000",
  "tasks": [
    {
      "task": "mark_overdue_installments",
      "status": "success",
      "message": "Parcelas vencidas verificadas e atualizadas com sucesso.",
      "executed_at": "2026-08-08T02:00:00.123456"
    }
  ]
}
```

### Resposta quando Ocorrer Falha em Alguma Tarefa (HTTP 207 Multi-Status)
Se qualquer tarefa do lote lançar uma exceção:
* O erro é automaticamente enviado ao **Sentry** (`sentry_sdk.capture_exception`).
* O endpoint responde **HTTP 207 Multi-Status** com `"status": "completed_with_errors"`, garantindo que o GCP Cloud Scheduler e alertas de monitoramento identifiquem a falha.

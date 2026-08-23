# Como Criar e Disparar Tarefas em Segundo Plano (Background Tasks)

> **Módulo:** [async-tasks-architecture](../../architecture/concepts/async-tasks-architecture.md) | [register-cron-tasks](register-cron-tasks.md)
> **Código:** `backend/apps/<modulo>/tasks.py`

---

Este guia prático ensina passo a passo como declarar, enfileirar e testar **Tarefas em Segundo Plano (Async Tasks)** no backend do sistema utilizando a API nativa `django.tasks` (Django 6.0 DEP 0014).

---

## 1. Como Declarar uma Tarefa em Segundo Plano

Em qualquer módulo de domínio no backend (ex: `apps/reporting/tasks.py`, `apps/logistics/tasks.py`, `apps/finances/tasks.py`), crie ou edite o arquivo `tasks.py` e utilize o decorator `@task()` do Django:

```python
# backend/apps/logistics/tasks.py
import logging
from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def process_contract_pdf_task(contract_id: str) -> None:
    """Processa o arquivo PDF do contrato em segundo plano.

    Args:
        contract_id: UUID do contrato em formato string.
    """
    logger.info("Iniciando processamento assíncrono do contrato uuid=%s", contract_id)

    # 1. Recuperar a instância do banco de dados
    from apps.logistics.models import Contract
    contract = Contract.objects.get(uuid=contract_id)

    # 2. Executar o processamento pesados (I/O, OCR, geração de PDF, etc.)
    # ...

    logger.info("Processamento concluído com sucesso para o contrato uuid=%s", contract_id)
```

---

## 2. Como Disparar a Tarefa a partir de Serviços ou Endpoints

Para enfileirar a execução em segundo plano a partir de um método de serviço (`services.py`) ou endpoint da API (`api.py`), utilize o método `.enqueue()`:

```python
# backend/apps/logistics/services.py
from apps.logistics.tasks import process_contract_pdf_task

class ContractService:

    @staticmethod
    def upload_contract(company, wedding, name, file_obj):
        # 1. Cria a entidade no banco de dados e salva o arquivo no storage
        contract = Contract.objects.create(...)

        # 2. Dispara a tarefa em segundo plano sem bloquear a requisição HTTP!
        process_contract_pdf_task.enqueue(contract_id=str(contract.uuid))

        # 3. Retorna imediatamente (HTTP 201 Created em ~50ms)
        return contract
```

---

## 3. Regras de Ouro & Boas Práticas

> [!IMPORTANT]
> **1. Passe Apenas Tipos Primitivos no `.enqueue()`**:
> **NUNCA** passe instâncias vivas de modelos do ORM (ex: `process_task.enqueue(contract)`). Objetos do Django ORM não podem ser serializados de forma confiável para a fila. Passe apenas identificadores primitivos (`str`, `int`, `UUID`) como `str(contract.uuid)`.

> [!TIP]
> **2. Idempotência e Resiliência**:
> A tarefa em background pode ser reexecutada em caso de falha de rede. Certifique-se de que reexecutar a função com o mesmo parâmetro não duplique dados no banco.

> [!NOTE]
> **3. Notificação de Conclusão**:
> Ao término da tarefa em background, utilize o `NotificationService.create_notification` ou `create_async_notification` para informar o usuário sobre o resultado da operação.

---

## 4. Testes e Execução em Cada Ambiente

### A. Desenvolvimento Local (`docker-compose`)
No ambiente local, a fila de mensagens é gerenciada pelo container `wedding_redis` (**Valkey 8**) e consumida pelo worker `wedding_worker` (**Huey**):
```bash
# O worker roda automaticamente no container docker:
python manage.py run_huey
```

### B. Testes Automatizados (`pytest`)
Nos testes automatizados com Pytest, a engine utiliza o `ImmediateBackend` síncrono em memória. Você pode asserir o efeito colateral no banco ou verificar a chamada da tarefa:

```python
# backend/apps/logistics/tests/test_services.py
import pytest
from unittest.mock import patch
from apps.logistics.services import ContractService

@pytest.mark.django_db
def test_upload_contract_dispatches_task(user):
    with patch("apps.logistics.tasks.process_contract_pdf_task.enqueue") as mock_enqueue:
        contract = ContractService.upload_contract(user.company, ...)

        assert mock_enqueue.called
        assert mock_enqueue.call_args[1]["contract_id"] == str(contract.uuid)
```

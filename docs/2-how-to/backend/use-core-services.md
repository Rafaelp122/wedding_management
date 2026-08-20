# Como Usar e Criar Serviços de Infraestrutura (Core Infrastructure Services)

Este guia explica como utilizar os **Serviços de Infraestrutura (Core Services)** localizados em `backend/apps/core/services/` e como criar novas integrações de infraestrutura utilizando a arquitetura **Protocol + Factory + Injeção de Dependência**.

---

## 1. O que são Serviços de Infraestrutura?

Ao contrário dos **Domain Services** (`apps/<domain>/services.py`), que tratam de regras de negócio e persistência de modelos multi-tenant, os **Core Infrastructure Services** (`apps/core/services/<service>/`) encapsulam a integração com adaptadores externos, nuvem, storage e I/O.

### Serviços de Infraestrutura Atuais:
* **Storage**: `StorageService` (`CloudflareR2StorageService`) — Gerencia URLs pré-assinadas para uploads no R2/S3.
* **Autenticação OIDC**: `OIDCVerifier` (`GCPOIDCVerifier` / `MockOIDCVerifier`) — Validação criptográfica de tokens OIDC do Cloud Scheduler.

---

## 2. Como Consumir um Serviço de Infraestrutura no Código

**Regra Fundamental**: Nunca instancie classes concretas diretamente (ex: `GCPOIDCVerifier()` ou `CloudflareR2StorageService()`). Use sempre as **funções Factory** (`get_<service>()`).

### Exemplo 1: Consumindo o `StorageService`

```python
from apps.core.services import get_storage_service

# Obter a instância ativa (injetada pela Factory)
storage_service = get_storage_service()

# Gerar URL pré-assinada de upload (PUT)
upload_url = storage_service.generate_presigned_put_url(
    bucket="wedding-contracts",
    object_key="contracts/123/contrato.pdf",
    content_type="application/pdf",
    expires_in=900,
)

# Upload direto de bytes gerados em memória (ex: relatórios PDF/Excel)
saved_key = storage_service.upload_bytes(
    bucket="wedding-reports",
    object_key="reports/company-id/wedding-id/relatorio.pdf",
    data=b"%PDF-...",
    content_type="application/pdf",
)

# Gerar URL pré-assinada de download seguro (GET)
download_url = storage_service.generate_presigned_get_url(
    bucket="wedding-reports",
    object_key=saved_key,
    expires_in=3600,
)
```

### Exemplo 2: Consumindo o `OIDCVerifier` no Decorator

```python
from apps.core.services import get_oidc_verifier

# Obter o verificador ativo conforme o ambiente (Mock em dev/testes, GCP em prod)
verifier = get_oidc_verifier()
claims = verifier.verify_token(token_string)
```

---

## 3. Passo a Passo para Criar um Novo Serviço de Infraestrutura

Caso precise adicionar uma nova integração (ex: envio de e-mails via SendGrid, integração SMS/WhatsApp, etc.):

### Estrutura de Pastas Obrigatória
Crie uma subpasta em `backend/apps/core/services/<novo_servico>/`:

```text
apps/core/services/<novo_servico>/
├── __init__.py    # Exporta o Protocol, Implementações e a Factory
├── base.py        # Protocol (Interface Abstrata via typing.Protocol)
├── factory.py     # Função Injetora get_<novo_servico>()
├── provider.py    # Implementação Concreta de Produção
└── mock.py        # Implementação Mock para Dev e Pytest
```

### Passo 1: Definir o Protocolo (`base.py`)
```python
from typing import Protocol


class EmailService(Protocol):
    """Protocolo de interface para envio de e-mails transacionais."""

    def send_email(self, to_email: str, subject: str, body_html: str) -> bool:
        """Envia um e-mail transacional."""
        ...
```

### Passo 2: Implementar os Provedores Concreto e Mock (`provider.py` e `mock.py`)
```python
# mock.py
import logging

logger = logging.getLogger(__name__)


class MockEmailService:
    """Implementação Mock para ambiente local e testes."""

    def send_email(self, to_email: str, subject: str, body_html: str) -> bool:
        logger.info("[MOCK EMAIL] Para: %s | Assunto: %s", to_email, subject)
        return True
```

### Passo 3: Criar a Factory (`factory.py`)
```python
from django.conf import settings
from .base import EmailService
from .mock import MockEmailService
from .provider import SendGridEmailService


def get_email_service() -> EmailService:
    """Injeta a implementação de e-mail com base no ambiente."""
    if getattr(settings, "DEBUG", False) or getattr(settings, "TESTING", False):
        return MockEmailService()
    return SendGridEmailService()
```

### Passo 4: Exportar em `apps/core/services/__init__.py`
Adicione o novo serviço na exportação global de `apps/core/services/__init__.py`.

---

## 4. Benefícios dessa Arquitetura

1. **Zero Lock-In**: Trocar o provedor de nuvem ou storage exige apenas criar uma nova classe e alterar a Factory.
2. **Testes Rápidos e Isolados**: O Pytest injeta automaticamente as versões `Mock` via Factory, executando em milissegundos sem chamadas de rede externas.
3. **Tipagem Estrita**: O uso de `typing.Protocol` garante validação estrita no `mypy`.

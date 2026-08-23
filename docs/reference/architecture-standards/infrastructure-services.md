# Especificação Técnica de Serviços de Infraestrutura (Core Infrastructure Services)

Esta especificação define o padrão arquitetural para os **Serviços de Infraestrutura (Infrastructure Services)** localizados em `backend/apps/core/services/`.

---

## 1. Nomenclatura e Diferenciação Conceitual

No **Wedding Management System**, distinguimos estritamente dois tipos de serviços:

| Conceito | Localização | Responsabilidade | Exemplos |
| :--- | :--- | :--- | :--- |
| **Domain Services** | `apps/<domain>/services.py` | Regras de negócio, casos de uso, validação multitenant e persistência de modelos. | `InstallmentService`, `ContractService` |
| **Infrastructure Services** | `apps/core/services/<service>/` | Integrações com serviços externos, nuvem, storage, autenticação de infra e I/O. | `StorageService` (R2), `OIDCVerifier` (GCP) |

> **Nota**: O nome `services` dentro de `apps/core/services/` é o padrão da indústria em Clean Architecture e DDD para encapsular adaptadores de infraestrutura reutilizáveis (*Adapters / Gateways*).

---

## 2. Padrão de Design (Protocol + Factory + Provider)

Todo Serviço de Infraestrutura deve seguir a estrutura de 4 componentes:

```text
apps/core/services/<service>/
├── __init__.py    # Exporta o Protocol, Implementações e a Factory
├── base.py        # Protocol (Interface Abstrata via typing.Protocol)
├── factory.py     # Função Injetora de Dependência (get_<service>())
├── gcp.py         # Implementação de Produção (ex: GCPOIDCVerifier, CloudflareR2)
└── mock.py        # Implementação de Testes / Dev Local (ex: MockOIDCVerifier)
```

### Exemplo de Estrutura

#### 1. Interface / Protocol (`base.py`)
```python
from typing import Any, Protocol


class OIDCVerifier(Protocol):
    def verify_token(self, token: str) -> dict[str, Any]:
        ...
```

#### 2. Injeção de Dependência via Factory (`factory.py`)
```python
from django.conf import settings
from .base import OIDCVerifier
from .gcp import GCPOIDCVerifier
from .mock import MockOIDCVerifier


def get_oidc_verifier() -> OIDCVerifier:
    """Injeta a implementação adequada conforme o ambiente."""
    if settings.DEBUG or getattr(settings, "TESTING", False):
        return MockOIDCVerifier()
    return GCPOIDCVerifier()
```

---

## 3. Diretrizes de Uso nos Handlers e Decorators

1. **Injeção Obrigatória**: Nunca instancie classes concretas (`GCPOIDCVerifier()`) diretamente em controladores ou decorators. Utilize sempre a função factory (`get_oidc_verifier()`).
2. **Testabilidade**: Nos testes Pytest, a factory injetará automaticamente a versão `Mock`, garantindo execução veloz e isolada sem chamadas de rede externas.

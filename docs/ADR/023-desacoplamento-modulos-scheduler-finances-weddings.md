# ADR-023: Desacoplamento dos Módulos Core (Weddings, Scheduler e Finances)

**Status:** Proposto
**Data:** Julho 2026
**Decisor:** (a definir)

---

## Contexto e Problema

Durante a refatoração do fluxo de detalhes de casamento, identificamos imports inline (lazy imports no Python) nos services de `weddings` e `finances` que importam módulos de `scheduler`. Estes imports foram introduzidos para evitar supostos erros de importação cíclica.

Os imports inline estão localizados em:

| Arquivo | Linha | Import |
|---|---|---|
| `weddings/services/wedding_service.py` | 353 | `from apps.scheduler.services import EventService` |
| `weddings/services/wedding_service.py` | 74 | `from apps.scheduler.models import Task` |
| `weddings/services/wedding_service.py` | 73 | `from apps.finances.models import Installment` |
| `finances/services/installment_service.py` | 665 | `from apps.scheduler.services import EventService` |
| `finances/services/installment_service.py` | 618 | `from apps.scheduler.models import Event` |
| `finances/services/installment_service.py` | 636 | `from apps.scheduler.models import Event` |

Além disso, o app `weddings` acumula responsabilidades de dashboard e relatórios que consultam modelos de `finances`, `scheduler` e `logistics` — 58% do código de services em `weddings` é query em domínios alheios.

---

## Análise de Dependências

Uma análise aprofundada do código revelou que **não há ciclo de importação em tempo de carga** entre os módulos. O grafo de dependências é direcionado:

```
weddings ──→ scheduler (EventService, Task)
weddings ──→ finances  (Budget, Installment)
scheduler ──→ weddings (Wedding model — import direto)
scheduler ──→ finances (NENHUM import Python — apenas FK string-based)
finances  ──→ weddings (Wedding model — import direto)
finances  ──→ scheduler (EventService, Event — APENAS inline imports)
```

As FKs entre modelos (ex: `Event.source_installment = ForeignKey("finances.Installment")`) são resolvidas pelo Django via string reference, não por imports Python. Portanto, não há ciclo de importação em tempo de carga para o par `scheduler` ↔ `finances`. O acoplamento arquitetural entre os domínios permanece, mas é gerenciado por interfaces de serviço.

Os imports inline foram introduzidos por precaução desnecessária.

---

## Decisão

Adotaremos as seguintes abordagens, listadas em ordem de implementação:

### 1. Mover `_apply_template_events` para scheduler

A função `_apply_template_events` em `weddings/services/wedding_service.py` cria eventos de cronograma no scheduler — ela pertence ao domínio de scheduler, não de weddings.

**Ação:** Criar `EventService.apply_template()` em `scheduler/services/events.py` com a mesma lógica. Remover a função de `weddings`. O `WeddingService.create()` passa a criar apenas o casamento, sem side-effects de calendário.

### 2. Mover criação/deleção de eventos de pagamento para scheduler

As funções `_create_payment_events`, `_delete_payment_events_for_expense` e `_delete_payment_event_for_single` em `finances/services/installment_service.py` manipulam eventos do scheduler — pertencem ao scheduler.

**Ação:** Criar `EventService.create_payment_event()`, `EventService.delete_payment_events_for_expense()` e `EventService.delete_payment_event()` em `scheduler/services/events.py`. O `InstallmentService` passa a importar `EventService` com top-level import (sem risco de ciclo, conforme análise acima).

### 3. Criar camada de orquestração em weddings

O fluxo de criação de casamento com template envolve dois domínios. A orquestração explícita deve viver numa camada neutra dentro do próprio app iniciador.

**Ação:** Criar `weddings/services/orchestration.py` com a função `create_wedding()` que chama `WeddingService.create()` seguido de `EventService.apply_template()`. O `api.py` chama a orquestração, não o service de domínio diretamente.

```python
# Exemplo: weddings/services/orchestration.py
@transaction.atomic
def create_wedding(*, company, payload):
    wedding = WeddingService.create(company=company, payload=payload)
    template_name = payload.model_dump(exclude_unset=True).get("template")
    if template_name is not None:
        EventService.apply_template(
            company=company, wedding=wedding, template_name=template_name
        )
    return wedding
```

> **⚠️ Warning:** `backend/apps/weddings/api/weddings.py` at line 74 calls `WeddingService.create()` directly. If `_apply_template_events` is removed from `WeddingService.create()` (as proposed in item 1), the API endpoint will create weddings without template events. Update `api.py` to call `orchestration.create_wedding()` instead.

### 4. Extrair DashboardService + summaries para app reporting

O `DashboardService` e os três summary services (`FinancialSummaryService`, `TaskSummaryService`, `ContractSummaryService`) em `weddings/services/summaries/` consultam modelos de todos os outros apps e agregam métricas do tenant inteiro — não são responsabilidade de weddings.

**Ação:** Criar `backend/apps/reporting/` com a mesma estrutura:

```
reporting/
├── __init__.py
├── apps.py
└── services/
    ├── __init__.py
    ├── dashboard_service.py
    └── summaries/
        ├── __init__.py
        ├── financial.py
        ├── task.py
        └── contract.py
```

Os arquivos são movidos sem alteração de lógica. O `DashboardService` continua importando modelos de outros apps — isso é aceitável para uma camada de reporting, que por definição cruza domínios.

### 5. Não implementar (rejeitado)

| Abordagem | Motivo da rejeição |
|---|---|
| Django Signals para eventos de domínio | Torna o fluxo implícito, difícil de debugar e testar. A solução com orquestração explícita + métodos dedicados no scheduler cobre os mesmos casos sem indireção. |
| Read Models / DTOs para dashboard | Overkill para um monólito. O dashboard é uma camada de leitura que cruza domínios por natureza — imports diretos a modelos são aceitáveis e mais simples. |
| Use cases em `core/use_cases/` | Camada adicional desnecessária para um caso unilateral (weddings → scheduler). Mantemos a orquestração em `weddings/services/orchestration.py`. |

---

## Estrutura Final Esperada

```
backend/apps/
├── weddings/
│   ├── services/
│   │   ├── __init__.py             # Exporta WeddingService + orchestration
│   │   ├── wedding_service.py      # SEM _apply_template_events
│   │   ├── orchestration.py        # NOVO: create_wedding use case
│   │   └── summaries/              # REMOVIDO (movido para reporting)
│   └── ...
├── scheduler/
│   ├── services/
│   │   ├── events.py               # + apply_template(), + create_payment_event(), + delete_payment_*()
│   │   └── templates.py            # Inalterado
│   └── ...
├── finances/
│   ├── services/
│   │   └── installment_service.py  # SEM inline imports; importa EventService top-level
│   └── ...
└── reporting/                       # NOVO
    └── services/
        ├── __init__.py
        ├── dashboard_service.py     # Movido de weddings
        └── summaries/
            ├── financial.py
            ├── task.py
            └── contract.py
```

---

## Consequências

**Positivas:**
- Remoção de todos os 6 imports inline no código de produção.
- `weddings` deixa de importar `scheduler` completamente (o `orchestration.py` faz a ponte).
- `finances` importa `scheduler` com top-level import, sem risco de ciclo.
- Separação clara entre regras de negócio (`weddings`, `finances`, `scheduler`) e queries de leitura (`reporting`).
- Facilidade de testar cada service de forma isolada.

**Negativas:**
- Criação de um novo app (`reporting`) que precisa ser registrado em `INSTALLED_APPS`.
- Movimentação de arquivos existentes requer atualização de imports em `api.py`, `__init__.py`, e `tests/`.
- Aumento de uma camada de indireção no fluxo de criação de casamento (api → orchestration → services).

---

## Alternativas Consideradas

### Manter como está

Os imports inline funcionam e o sistema compila. Porém, violam as regras de typing do projeto (mypy não consegue type-check um import inline), dificultam a leitura e criam uma falsa sensação de que "circular imports são um problema iminente".

### Signals / Event Bus

Substituir chamadas diretas por signals do Django ou um event bus customizado. Rejeitado porque: (a) torna o fluxo implícito — não dá mais para saber quem chama o quê sem rastrear registros de signal, (b) dificulta testes unitários, (c) adiciona complexidade desnecessária para um caso que se resolve com orquestração explícita.

### Use cases em core/use_cases/

Criar uma camada neutra em `core/` para toda orquestração cross-app. Rejeitado porque: (a) introduz uma camada nova que ninguém conhece, (b) `core/` hoje tem shortcuts, exceptions e mixins — colar use cases muda o propósito do pacote, (c) a orquestração é unilateral (sempre weddings inicia), então manter no app iniciador é mais simples e mais descoberta naturalmente.

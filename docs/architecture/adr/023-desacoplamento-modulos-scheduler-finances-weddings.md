# ADR-023: Desacoplamento dos Módulos Core e Extração do Módulo Reporting

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟢 Vigente
> **Data:** Agosto 2026
> **Decisor:** Rafael
> **Relacionados:** [ADR-006: Service Layer Pattern](006-service-layer.md) · [ADR-016: Pragmatic Multi-Tenancy](016-pragmatic-multi-tenancy.md) · [ADR-030: Rich Domain Model e Service Layer](030-rich-domain-model-service-layer.md)

---

## 1. Contexto e Problema

O app `weddings` acumulava responsabilidades de dashboard e resumos analíticos que consultam modelos de `finances`, `scheduler` e `logistics` — mais de 50% do código de visualização e resumo em `weddings` realizava queries agregadas em domínios alheios.

Além disso, a evolução da aplicação para suportar relatórios consolidados em formatos PDF e Excel (Issue #339) exige um módulo neutro e dedicado a relatórios analíticos, evitando sobrecarregar o domínio transacional de casamentos.

---

## 2. Análise de Dependências

Uma análise aprofundada do código revelou que não há ciclo de importação em tempo de carga entre os módulos. O grafo de dependências entre domínios é direcionado:

```
weddings ──→ scheduler (EventService, Task)
weddings ──→ finances  (Budget, Installment)
scheduler ──→ weddings (Wedding model — import direto)
finances  ──→ weddings (Wedding model — import direto)
reporting ──→ weddings, finances, scheduler, logistics (leitura agregada via Selectors)
```

As FKs entre modelos são resolvidas pelo Django via string reference (`"finances.Installment"`), sem acoplamento de carga.

---

## 3. Decisão

Adotamos a extração de um novo módulo neutro `apps/reporting` seguindo os padrões CQRS e Query Selectors do projeto:

### 3.1 Extração do App Reporting (`apps/reporting`)

Criamos o app `backend/apps/reporting/` para concentrar as consultas de agregação analítica, KPIs de dashboard e geração de relatórios:

```
backend/apps/reporting/
├── __init__.py
├── apps.py                          # Configuração ReportingConfig
├── schemas.py                       # Schemas de visualização/dashboard
├── api.py                           # Rotas /api/v1/dashboard/
├── selectors/
│   ├── __init__.py                  # Re-exporta selectors de reporting
│   ├── dashboard_selectors.py       # Agregação global de KPIs do tenant
│   └── summaries/
│       ├── __init__.py              # Re-exporta summary selectors
│       ├── contract.py              # ContractSummarySelector
│       ├── financial.py             # FinancialSummarySelector
│       └── task.py                  # TaskSummarySelector
├── services.py                      # Camada de serviços para relatórios
└── tests/
    ├── __init__.py
    ├── test_apis.py
    └── test_dashboard_selectors.py
```

### 3.2 Padrão CQRS e Leitura Cross-Domain

- Os `selectors/` em `apps/reporting` consultam os modelos dos domínios (`Wedding`, `Budget`, `Installment`, `Task`, `Contract`) estritamente via `.objects.for_tenant(company)`.
- O controller (`api.py`) delega 100% das leituras aos selectors.
- A camada de `services.py` do `reporting` fica reservada para operações complexas de mutação/geração pesada de arquivos binários (PDF / Excel).

### 3.3 Rejeição de Camada Adicional de Orquestração

Avaliou-se a criação de uma subcamada de orquestração (`orchestration.py`) no app `weddings`. Essa abordagem foi **rejeitada** por adicionar indireção e complexidade desnecessárias para um fluxo transacional simples no monólito. As mutações permanecem diretamente nos respectivos services (`WeddingService`, `EventService`, etc.).

---

## 4. Alternativas Rejeitadas

| Abordagem | Motivo da rejeição |
|---|---|
| Camada de Orquestração (`orchestration.py`) | Indireção e complexidade desnecessárias para o monólito. Chamadas diretas de serviço atendem adequadamente o fluxo. |
| Django Signals para eventos de domínio | Torna o fluxo implícito e difícil de rastrear e debugar. |
| Manter dashboard em `weddings` | Mantém alto acoplamento do domínio de casamentos com modelos de finanças, logística e agenda. |

---

## 5. Consequências

### Positivas
- Desacoplamento do app `weddings`, que passa a focar estritamente no ciclo de vida e dados do casamento.
- Domínio `reporting` passa a ser a base oficial e reutilizável para agregadores de métricas e futura geração de relatórios PDF/Excel.
- Total isolamento de testes unitários e de integração de métricas.

### Negativas e mitigações
- **Novo app em `INSTALLED_APPS`:** Organização modular clara compensa o custo marginal de registro no Django.
- **Atualização de imports:** Imports de selectors centralizados em `reporting/selectors/` evitam quebras de compatibilidade.

---

## 6. Referências

1. [ADR-006: Service Layer Pattern](006-service-layer.md)
2. [ADR-016: Pragmatic Multi-Tenancy (Row-Level)](016-pragmatic-multi-tenancy.md)
3. [ADR-030: Rich Domain Model e Service Layer](030-rich-domain-model-service-layer.md)

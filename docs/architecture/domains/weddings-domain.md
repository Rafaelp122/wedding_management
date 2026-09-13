# Domínio de Casamentos & Gestão de Cerimônias (Weddings)

> **Categoria:** Domínios de Arquitetura (Bounded Contexts)
> **Relacionados:** [Ciclo de Vida do Casamento](../business-rules/weddings/wedding-status-lifecycle.md) · [Templates de Cronograma](../business-rules/weddings/wedding-schedule-templates.md) · [ADR-030: Rich Domain Model](../adr/030-rich-domain-model-service-layer.md) · [ADR-006: Service Layer](../adr/006-service-layer.md) · [ADR-011: BaseModel save com full_clean](../adr/011-basemodel-save-full-clean.md) · [ADR-023: Desacoplamento de Módulos](../adr/023-desacoplamento-modulos-scheduler-finances-weddings.md) · [Modelos Base & Padrões Core](../../reference/models/core-models.md)

---

## 1. Visão Geral do Domínio

O domínio de **Weddings** é o agregador central de operações de toda a plataforma. Ele representa o evento do casamento em si, definindo a identidade dos noivos, data, local, capacidade estimada de convidados, status de planejamento e o modelo inicial de cronograma (*template*).

Todos os demais domínios operacionais (`Finances`, `Logistics`, `Scheduler`, `Reporting`) orbitam em torno da entidade `Wedding`, herdando o pertencimento através do mixin `WeddingOwnedMixin`.

---

## 2. Diagrama ERD e Máquina de Estados de Status

```mermaid
erDiagram
    Company ||--o{ Wedding : "gerencia (CASCADE)"
    Wedding ||--o| Budget : "possui orçamento mestre (CASCADE)"
    Wedding ||--o{ Contract : "possui contratos (PROTECT)"
    Wedding ||--o{ Event : "agenda eventos (CASCADE)"
    Wedding ||--o{ Task : "possui checklist (CASCADE)"

    Wedding {
        bigint id PK
        uuid uuid UK "Identificador Público"
        bigint company_id FK "Company (Tenant Owner)"
        string groom_name "Nome do Noivo"
        string bride_name "Nome da Noiva"
        date date "Data do Evento (Futura na criação)"
        string location "Local do Casamento"
        integer expected_guests "Estimativa de Convidados"
        string status "IN_PROGRESS | COMPLETED | CANCELED"
        string template "Template de Cronograma Aplicado"
        datetime created_at
        datetime updated_at
    }
```

```mermaid
stateDiagram-v2
    [*] --> IN_PROGRESS : Criação do Casamento (data >= hoje)

    IN_PROGRESS --> COMPLETED : Marcar como Concluído (exige data <= hoje)
    IN_PROGRESS --> CANCELED : Cancelar Casamento

    CANCELED --> IN_PROGRESS : Reativar Planejamento
    COMPLETED --> [*] : Arquivado com Sucesso
    CANCELED --> [*] : Encerrado
```

---

## 3. Tabela de Entidades e Invariantes de Persistência

| Entidade / Componente | Papel Arquitetural | Campos & Chaves | Invariantes de Persistência & Regras de Negócio |
| :--- | :--- | :--- | :--- |
| **`Wedding`** | Rich Domain Model (`TenantModel`) | `groom_name` (max 100), `bride_name` (max 100), `date` (DateField), `location` (max 255), `expected_guests` (PositiveInt, nullable), `status` (`StatusChoices`), `template` (string, nullable) | **Máquina de Estados (ADR-030):** Métodos de ciclo de vida `complete()`, `cancel()`, `reopen()` e `transition_to()`.<br/>**Regra de Conclusão (BR-W01):** Um casamento só pode ser concluído se `date <= timezone.now().date()`.<br/>**Proteção de Deleção (BR-W03):** Bloqueio de exclusão em cascata se existirem contratos ou despesas protegidos (`ProtectedError`). |
| **`WeddingQuerySet`** | Camada de Consulta Otimizada | `search()`, `by_status()`, `with_metrics()` | Anota de forma eficiente contagens de tarefas incompletas, parcelas atrasadas e total orçado sem incorrer em problemas de N+1 queries. |
| **`WeddingService`** | Casos de Uso e Orquestração | `create()`, `update()`, `complete()`, `cancel()`, `delete()` | **Transações Atômicas:** Métodos decorados com `@transaction.atomic`.<br/>**Orquestração de Casos de Uso:** Delega regras de transição para a entidade e coordena efeitos colaterais como templates de eventos (`_apply_template_events`). |

---

## 4. Contratos de Código e Implementação

As implementações de código-fonte seguem a diretriz pragmática da [ADR-030](../adr/030-rich-domain-model-service-layer.md):

- **Modelo de Domínio Rico:** [`apps/weddings/models.py`](../../../backend/apps/weddings/models.py) (`Wedding`) encapsula a máquina de estados, propriedades de domínio e validação no `clean()`.
- **Casos de Uso e Serviços:** [`apps/weddings/services.py`](../../../backend/apps/weddings/services.py) (`WeddingService`) orquestra transações atômicas, resolução de tenant e aplicação de templates.
- **Seletores de Leitura CQRS:** [`apps/weddings/selectors.py`](../../../backend/apps/weddings/selectors.py) (`wedding_list_selector`, `wedding_get_selector`) concentra queries otimizadas com anotações de métricas.
- **Validação de Entrada (Pydantic):** [`apps/weddings/schemas.py`](../../../backend/apps/weddings/schemas.py) (`WeddingIn`, `WeddingPatchIn`) garante fail-fast na borda da API para campos obrigatórios, sanitização de espaços e limites de caracteres.

---

## 5. Mapeamento de Camadas (Fullstack)

### Camada de Backend (`backend/apps/weddings/`)
- **Modelos:** `Wedding` em `models.py`.
- **Managers:** `WeddingQuerySet` em `managers.py`.
- **Services:** `WeddingService` e `_apply_template_events` em `services.py`.
- **Selectors:** `wedding_list_selector`, `wedding_get_selector`, `critical_weddings_selector` em `selectors.py`.
- **Endpoints:** `api.py` com rotas `/weddings/` (CRUD completo).

### Camada de Frontend (`frontend/src/features/weddings/`)
- **Páginas:** `WeddingsListPage.tsx`, `WeddingDetailPage.tsx`.
- **Componentes:** `WeddingHeader.tsx`, `WeddingOverview.tsx`, `WeddingDetailTabs.tsx`, `WeddingsTable.tsx`, `WeddingFilters.tsx`.
- **Dialogs:** `CreateWeddingDialog.tsx`, `EditWeddingDialog.tsx`, `DeleteWeddingDialog.tsx`.
- **Estado Global & Hooks:** `useWeddingStore`, `useWeddingsPage`, `useWeddingDetail`.

---

## 6. Links e Regras de Negócio Associadas

- [Ciclo de Vida e Transições de Status do Casamento](../business-rules/weddings/wedding-status-lifecycle.md)
- [Templates de Cronograma e Cerimônia](../business-rules/weddings/wedding-schedule-templates.md)
- [ADR-006: Service Layer](../adr/006-service-layer.md)
- [ADR-011: BaseModel save com full_clean](../adr/011-basemodel-save-full-clean.md)
- [ADR-023: Desacoplamento de Módulos](../adr/023-desacoplamento-modulos-scheduler-finances-weddings.md)
- [Modelos Base & Padrões Core](../../reference/models/core-models.md)
- [Finances Domain](finances-domain.md)
- [Scheduler Domain](scheduler-domain.md)

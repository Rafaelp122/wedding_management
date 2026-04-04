# Entity Relationship Diagram (Conceitual)

Este diagrama demonstra os dados transacionais de negócio presentes no banco de dados e as relações diretas entre eles, evidenciando o quão centralizadora é a entidade `Wedding`.

```mermaid
erDiagram
    USER ||--o{ WEDDING : "creates / manages"
    WEDDING ||--o{ BUDGET : "has"
    WEDDING ||--o{ BUDGET_CATEGORY : "restricts"
    WEDDING ||--o{ EXPENSE : "records"
    WEDDING ||--o{ CONTRACT : "signs"
    WEDDING ||--o{ SUPPLIER : "books"
    WEDDING ||--o{ ITEM : "demands"
    WEDDING ||--o{ EVENT : "schedules"

    BUDGET ||--o{ BUDGET_CATEGORY : "split into"
    BUDGET_CATEGORY ||--o{ EXPENSE : "categorizes"
    BUDGET_CATEGORY ||--o{ ITEM : "allocates"

    SUPPLIER ||--o{ CONTRACT : "provides"
    CONTRACT ||--o| EXPENSE : "anchors financially"
    CONTRACT ||--o{ ITEM : "includes"

    EXPENSE ||--|{ INSTALLMENT : "broken into"
    INSTALLMENT ||--o| EVENT : "triggers payment schedule"
```

> Nota: Este não é o esquema SQL estrito; no sistema em produção aplicam-se estratégias de desnormalização defensiva através do uso de `WeddingOwnedMixin` nas entidades para segurança multi-tenant (onde várias das pontas ligam ativamente de volta a `Wedding`).

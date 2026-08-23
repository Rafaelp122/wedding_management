# Domínios da Plataforma (MOC)

Este índice centraliza a especificação de domínio de cada bounded context do **Wedding Management System**.

---

## Mapeamento de Bounded Contexts

| Domínio | Especificação | Responsabilidade Principal |
| :--- | :--- | :--- |
| **Core** | [core-domain](core-domain.md) | Entidades base, auditoria, tenancy e soft-delete. |
| **Dashboard** | [dashboard-domain](dashboard-domain.md) | Agregação de KPIs executivos e visão consolidada. |
| **Reporting** | [reporting-domain](reporting-domain.md) | Relatórios financeiros, contratuais e de cronograma. |
| **Finances** | [finances-domain](finances-domain.md) | Orçamentos, despesas, parcelamentos e integridade contábil. |
| **Logistics** | [logistics-domain](logistics-domain.md) | Fornecedores, contratos, itens e upload de PDFs via R2. |
| **Scheduler** | [scheduler-domain](scheduler-domain.md) | Eventos de agenda, tarefas e motor de recorrência. |
| **Tenants** | [tenants-domain](tenants-domain.md) | Isolamento multi-tenant por empresa/assessoria. |
| **Users** | [users-domain](users-domain.md) | Autenticação, perfis e controle de acesso (RBAC). |
| **Weddings** | [weddings-domain](weddings-domain.md) | Ciclo de vida dos casamentos e templates de cronograma. |
| **Notifications** | [notifications-domain](notifications-domain.md) | Notificações in-app e alertas do sistema. |

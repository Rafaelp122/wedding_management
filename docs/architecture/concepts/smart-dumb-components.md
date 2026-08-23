# Arquitetura: Padrão Smart/Dumb Components

> **Módulo:** [smart-dumb-components](smart-dumb-components.md) | [frontend-reference](../../reference/frontend/index.md)
> **ADR de Referência:** ADR-024

---

## Visão Geral

Para garantir alta manutenibilidade, desacoplamento e facilidade de testes unitários no React, os componentes de UI são divididos em **Smart Components (Containers)** e **Dumb Components (Presenters/Views)**.

---

## Comparativo Estrutural

| Característica | Smart Components (Containers) | Dumb Components (Presenters/Views) |
| :--- | :--- | :--- |
| **Localização** | `src/features/<modulo>/pages/` ou `containers/` | `src/features/<modulo>/components/` |
| **Responsabilidade** | Consumir hooks do Orval, TanStack Query, React Router e Zustand Stores. | Renderização pura de JSX/HTML e estilos CSS/Tailwind. |
| **Efeitos de Rede** | SIM (dispara requisições API e mutações). | NÃO (sem chamadas HTTP ou side-effects). |
| **Comunicação** | Passa dados processados e handlers via props para a View. | Recebe props fortemente tipadas e dispara callbacks do pai. |
| **Testabilidade** | Testados via E2E ou integração com MSW. | Testes unitários puros, rápidos e síncronos com Vitest + RTL. |

---

## Exemplo Prático de Separação

- **Smart Component:** `FinancesDistributionContainer.tsx` — busca os dados de orçamento com `useFinancesBudgetsList()` e passa a lista processada.
- **Dumb Component:** `FinancesDistributionChart.tsx` — recebe `data: CategoryDistribution[]` e renderiza o gráfico PieChart sem dependências de rede.

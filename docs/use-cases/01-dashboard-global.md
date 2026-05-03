# 📊 Dashboard Global

## Estrutura de Navegação

```
Sidebar → 📊 Global
```

Primeira tela ao entrar no sistema. Visão geral de **todos os casamentos** da empresa.

---

## UC10: Visualizar Dashboard Global

| Campo | Descrição |
|-------|-----------|
| **ID** | UC10 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista acessa o sistema |
| **Prioridade** | ⭐⭐⭐⭐⭐ Essencial |
| **Complexidade** | ⭐⭐⭐⭐☆☆ |

### Fluxo Principal: Dashboard Geral

1. Cerimonialista faz login
2. Sistema exibe dashboard global com:

```
📊 VISÃO GERAL DA EMPRESA
┌────────────────────────────────────┐
│ Casamentos Ativos:      12         │
│ Faturamento Total:      R$ 450k   │
│ Parcelas a Vencer (7d): R$ 32k    │
│ Eventos essa Semana:    5          │
└────────────────────────────────────┘

📈 FLUXO DE CAIXA (PRÓXIMOS 4 MESES)
├─ Jun/2026:  R$ 45.000  ████████████
├─ Jul/2026:  R$ 38.000  ██████████░░
├─ Ago/2026:  R$ 22.000  ██████░░░░░░
└─ Set/2026:  R$ 15.000  ████░░░░░░░░

⏰ PRÓXIMOS VENCIMENTOS
├─ 💒 Ana & João - Buffet Master - 15/06 - R$ 5.000
├─ 💒 Maria & Pedro - Fotos Arte - 20/06 - R$ 2.500
└─ ⚠️ Carla & Luiz - Floricultura - VENCE HOJE - R$ 800

📈 CASAMENTOS EM ANDAMENTO
├─ 💒 Ana & João       - 15/12/2026 - 68% do orçamento
├─ 💒 Maria & Pedro    - 20/01/2027 - 45% do orçamento
└─ 💒 Carla & Luiz     - 10/06/2026 - 92% do orçamento
```

3. Cerimonialista pode clicar em qualquer casamento para ir aos detalhes
4. Cerimonialista pode clicar em qualquer parcela para ir ao financeiro

---

### Regras de Negócio

- Performance: dashboard < 500ms
- Dados atualizados em tempo real (sem cache)
- Cerimonialista vê apenas dados de sua empresa

---

## Relacionamentos com Outros Módulos

| Dado | Origem |
|------|--------|
| Casamentos ativos | `02-casamentos.md` - UC01: Listagem com status IN_PROGRESS |
| Faturamento total | `03-financeiro.md` - Soma de orçamentos dos casamentos ativos |
| Fluxo de caixa (4 meses) | `03-financeiro.md` - UC04: Parcelas PENDING agrupadas por mês |
| Parcelas a vencer | `03-financeiro.md` - UC04: Parcelas PENDING com vencimento ≤ 7 dias |
| Próximos eventos | `05-calendario.md` - UC08: Eventos dos próximos 7 dias |

---

**Última atualização:** 2 de maio de 2026
**Versão:** 1.1 - Fluxo de caixa adicionado
**Módulo:** Global
**Voltar:** [index.md](./index.md)

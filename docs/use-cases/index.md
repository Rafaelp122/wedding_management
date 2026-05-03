# 🎯 Casos de Uso - Wedding Management System

## Persona

| Ator | Descrição |
|------|-----------|
| **Cerimonialista** | Profissional que organiza casamentos para clientes. Gerencia orçamentos, fornecedores, prazos e documentos. |

---

## 🧭 Mapa de Navegação

```
┌───────────────────────────────────────────────────────────┐
│                     WEDDING MANAGEMENT                    │
├──────────────────────┬────────────────────────────────────┤
│      SIDEBAR         │            PÁGINA ATIVA            │
│                      │                                    │
│  📊 Global           │  → Dashboard Global                │
│                      │    (todos os casamentos)           │
│  💒 Casamentos       │  → Listagem de Casamentos          │
│  🤝 Fornecedores     │  → Listagem de Fornecedores        │
│  📅 Calendário       │  → Calendário Geral                │
│                      │                                    │
│  ── Ao clicar em um casamento ──                         │
│                      │                                    │
│  📋 Geral            │  → Dashboard do Casamento          │
│  💰 Financeiro       │  → Orçamento + Categorias          │
│                      │     + Despesas + Parcelas          │
│  📦 Logística        │  → Fornecedores + Itens            │
│                      │     + Documentos                   │
│  📅 Cronograma       │  → Calendário do Casamento         │
└──────────────────────┴────────────────────────────────────┘
```

### Hierarquia de Telas

```
Sidebar (Global)
├── 📊 Dashboard Global       → 01-dashboard-global.md
├── 💒 Casamentos             → 02-casamentos.md
│     └── [Clica no casamento]
│           ├── 📋 Geral       → Dashboard do casamento (UC10)
│           ├── 💰 Financeiro  → 03-financeiro.md (UC02, UC03, UC04)
│           ├── 📦 Logística   → 04-logistica.md (UC05, UC06, UC07)
│           └── 📅 Cronograma  → 05-calendario.md (UC08)
├── 🤝 Fornecedores           → 04-logistica.md (UC05 - visão global)
└── 📅 Calendário             → 05-calendario.md (UC08 - visão global)
```

---

## 🧩 Relacionamento entre Módulos

```
Global (Dashboard)
  │
  ├── Casamento 1
  │     ├── Financeiro (Orçamento → Categorias → Despesas → Parcelas)
  │     ├── Logística (Fornecedores → Itens → Documentos)
  │     │     └── Sincronização Automática: Documento → Despesa (UC07→UC03)
  │     └── Cronograma (Eventos → Alertas)
  │
  ├── Casamento 2
  │     └── ...
  │
  └── Fornecedores (compartilhados entre casamentos)
```

### Automações Cross-Módulo

| Gatilho | Ação | Redução de Trabalho |
|---------|------|---------------------|
| Upload de Documento (UC07) | Botão "Gerar Despesa" pré-preenche formulário | Elimina redigitação |
| Criação de Casamento (UC01) | Template popula cronograma com prazos | Elimina criação manual de eventos |
| Parcela Vencida (UC04) | Alerta automático in-app + email (UC09) | Elimina acompanhamento manual |

---

## 📐 Transições de Status

### Casamento
```
CREATED → IN_PROGRESS → COMPLETED
                      → CANCELED
```

### Parcela
```
PENDING → PAID
       → OVERDUE (automático se data passou)
       → PAID (pago após vencer)
```

### Item
```
PENDING → IN_PROGRESS → DONE
```

### Documento
```
ACTIVE → EXPIRED (automático se expiration_date passou)
```

---

## 📈 Matriz de Priorização

| UC | Nome | Esforço | Valor | Prioridade |
|----|------|---------|-------|------------|
| UC01 | Gerenciar Casamentos | ⭐⭐ | ⭐⭐⭐⭐⭐ | **1** |
| UC03 | Gerenciar Despesas | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **2** |
| UC04 | Gerenciar Parcelas | ⭐⭐ | ⭐⭐⭐⭐⭐ | **3** |
| UC10 | Dashboard do Casamento | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **4** |
| UC02 | Gerenciar Categorias | ⭐⭐ | ⭐⭐⭐⭐☆ | **5** |
| UC05 | Gerenciar Fornecedores | ⭐⭐ | ⭐⭐⭐⭐☆ | **6** |
| UC08 | Gerenciar Cronograma | ⭐⭐⭐ | ⭐⭐⭐⭐☆ | **7** |
| UC09 | Alertas e Notificações | ⭐⭐⭐ | ⭐⭐⭐⭐☆ | **8** |
| UC06 | Gerenciar Itens | ⭐⭐ | ⭐⭐⭐☆☆ | **9** |
| UC07 | Gerenciar Documentos | ⭐⭐⭐ | ⭐⭐⭐☆☆ | **10** |
| UC11 | Exportar Relatórios | ⭐⭐ | ⭐⭐⭐☆☆ | **11** |

---

## 🗺️ Roadmap Sugerido

### Sprint 1-2 (MVP Essencial)
```
UC01 → Gerenciar Casamentos (CRUD)
UC02 → Gerenciar Categorias
UC03 → Criar Despesas com Parcelamento
UC04 → Registrar Pagamento de Parcelas
```

### Sprint 3-4 (Valor para o Cerimonialista)
```
UC10 → Dashboard do Casamento
UC05 → Gerenciar Fornecedores
UC08 → Gerenciar Cronograma
✦ Sincronização Documento → Despesa (UC07 → UC03)
```

### Sprint 5-6 (Automação e Controle)
```
UC09 → Alertas e Notificações
UC06 → Gerenciar Itens
UC07 → Gerenciar Documentos
✦ Templates de Cronograma na criação de casamento
UC11 → Exportar Relatórios
```

---

**Última atualização:** 2 de maio de 2026
**Versão:** 1.1
**Próximo:** [01-dashboard-global.md](./01-dashboard-global.md)

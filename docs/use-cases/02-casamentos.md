# 💒 Gestão de Casamentos

## Estrutura de Navegação

```
Sidebar → 💒 Casamentos → [Clica no casamento] → Abas internas
                                                     ├── 📋 Geral
                                                     ├── 💰 Financeiro
                                                     ├── 📦 Logística
                                                     └── 📅 Cronograma
```

---

## UC01: Gerenciar Casamentos

| Campo | Descrição |
|-------|-----------|
| **ID** | UC01 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista fecha contrato com novo cliente |
| **Prioridade** | ⭐⭐⭐⭐⭐ Essencial |
| **Complexidade** | ⭐⭐☆☆☆☆ |

### Fluxo Principal: Criar Casamento

1. Cerimonialista acessa "Novo Casamento"
2. Sistema exibe formulário com campos:
   - Nome do evento (ex: "Ana & João")
   - Data do casamento
   - Local
   - Número estimado de convidados
   - **Template de Cronograma (opcional):**
     - "Casamento Religioso" (12 meses de prazos)
     - "Casamento na Praia" (6 meses de prazos)
     - "Civil + Buffet" (3 meses de prazos)
     - "Começar do zero"
3. Cerimonialista preenche, seleciona template (ou não) e confirma
4. Sistema valida data futura
5. Sistema cria casamento com status `IN_PROGRESS`
6. **Se template selecionado:** Sistema popula automaticamente o cronograma com eventos padrão ajustados à data do casamento:
   ```
   📅 Exemplo: Template "Casamento Religioso" para 15/12/2026
   ├─ 15/01/2026 (-11m) → Definir Igreja/Local
   ├─ 15/03/2026 (-9m)  → Contratar Buffet
   ├─ 15/06/2026 (-6m)  → Fechar Fotografia
   ├─ 15/09/2026 (-3m)  → Prova de Vestido
   ├─ 15/11/2026 (-1m)  → Confirmar Convidados
   └─ 15/12/2026 (Dia)  → 🎊 Casamento
   ```
7. Sistema redireciona para dashboard do casamento (aba 📋 Geral)

### Fluxo Alternativo: Editar Casamento

1. Cerimonialista abre um casamento
2. Navega até informações básicas
3. Altera data, local, convidados
4. Sistema valida consistência:
   - Se data no passado e status COMPLETED → permite
   - Se data alterada → recalcula prazos do cronograma
5. Sistema salva alterações

### Fluxo Alternativo: Cancelar Casamento

1. Cerimonialista acessa "Cancelar Casamento"
2. Sistema alerta: "Isto irá cancelar todos os orçamentos, despesas e documentos vinculados"
3. Cerimonialista confirma
4. Sistema marca como `CANCELED`
5. Sistema mantém dados para consulta (não deleta)

### Fluxo Alternativo: Visualizar Listagem

1. Cerimonialista acessa "Casamentos" na sidebar
2. Sistema exibe lista com:
   - Nome do evento e casal
   - Data do casamento
   - Status
   - Progresso financeiro (X% do orçamento)
3. Cerimonialista pode filtrar por status ou data

---

### 📋 Aba "Geral" (Dashboard do Casamento)

Ao clicar em um casamento, a primeira aba exibe:

```
💒 Casamento: Ana & João
📅 Data: 15/12/2026 | 📍 Local: Fazenda Esperança | 👥 150 convidados

📊 SAÚDE FINANCEIRA
┌──────────────────────────────────┐
│ Orçado:      R$ 100.000  ████████ │
│ Contratado:  R$ 85.000   ██████░░ │
│ Pago:        R$ 45.000   ████░░░░ │
│ Restante:    R$ 55.000           │
└──────────────────────────────────┘

📈 POR CATEGORIA
├─ Decoração:   R$ 20k / R$ 25k (80%)
├─ Buffet:      R$ 35k / R$ 40k (87%)
└─ Fotografia:  R$ 10k / R$ 15k (67%)

⏰ PRÓXIMOS VENCIMENTOS
├─ Buffet Master - 15/06 - R$ 5.000
├─ Fotos Arte - 20/06 - R$ 2.500
└─ ⚠️ Floricultura Bella - VENCE HOJE - R$ 800

📈 FLUXO DE CAIXA (PRÓXIMOS 4 MESES)
├─ Jun/2026:  R$ 8.000   ████████████
├─ Jul/2026:  R$ 12.000  ████████████
├─ Ago/2026:  R$ 5.000   ██████░░░░░░
└─ Set/2026:  R$ 3.000   ████░░░░░░░░
```

---

### Critérios de Aceitação

- [ ] Data futura é validada na criação
- [ ] Casamento cancelado mantém dados para consulta
- [ ] Cerimonialista vê apenas seus casamentos (multi-tenancy)
- [ ] Template de cronograma popula eventos automaticamente na criação
- [ ] Dashboard do casamento carrega em < 500ms com 500 despesas
- [ ] Gráficos mostram orçado vs realizado
- [ ] Fluxo de caixa mostra saídas nos próximos 4 meses

---

## Regras de Negócio

- `BR-W01`: Só pode marcar COMPLETED se data já passou
- `BR-SEC01`: Cerimonialista só vê seus próprios casamentos
- Data deve ser futura na criação

---

## Relacionamentos com Outros Módulos

| Aba | Módulo |
|-----|--------|
| 💰 Financeiro | `03-financeiro.md` - Orçamento, categorias, despesas, parcelas |
| 📦 Logística | `04-logistica.md` - Fornecedores, itens, documentos |
| 📅 Cronograma | `05-calendario.md` - Eventos do casamento |

---

## Diagrama de Transições de Status

```
IN_PROGRESS → COMPLETED
            → CANCELED
```

---

**Última atualização:** 2 de maio de 2026
**Versão:** 1.1 - Templates de cronograma + fluxo de caixa
**Módulo:** Casamentos
**Voltar:** [index.md](./index.md)

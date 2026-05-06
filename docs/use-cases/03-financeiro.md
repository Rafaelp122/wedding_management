# 💰 Módulo Financeiro

## Estrutura de Navegação

```
💒 Casamento → Aba 💰 Financeiro
                ├── Orçamento (visão geral)
                ├── Categorias de Orçamento
                ├── Despesas
                └── Parcelas
```

---

## UC02: Gerenciar Categorias de Orçamento

| Campo | Descrição |
|-------|-----------|
| **ID** | UC02 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista precisa organizar orçamento por áreas |
| **Prioridade** | ⭐⭐⭐⭐⭐ Essencial |
| **Complexidade** | ⭐⭐☆☆☆☆ |

### Fluxo Principal: Criar Categoria

1. Cerimonialista acessa "Financeiro" do casamento
2. Visualiza visão geral do orçamento com categorias existentes
3. Clica em "Nova Categoria"
4. Sistema exibe formulário:
   - Nome da categoria
   - Valor orçado (allocated_budget)
5. Cerimonialista preenche e confirma
6. Sistema cria categoria vinculada ao Budget do casamento
7. Sistema recalcula total orçado do casamento

### Fluxo Alternativo: Editar Categoria

1. Cerimonialista altera valor orçado de uma categoria
2. Sistema valida: novo valor pode ser menor que total de despesas já lançadas na categoria
3. Se for menor → sistema alerta: "Existem R$ X em despesas lançadas. Deseja ajustar?"
4. Cerimonialista confirma ou ajusta

### Fluxo Alternativo: Excluir Categoria (Proteção de Dados)

1. Cerimonialista tenta excluir uma categoria
2. Sistema verifica se existem despesas vinculadas a esta categoria
3. **Se houver despesas** → sistema BLOQUEIA exclusão e exibe:
   - "Esta categoria possui R$ X em despesas. Reatribua as despesas para outra categoria antes de excluir."
4. **Se não houver despesas** → sistema permite exclusão
5. Cerimonialista reatribui as despesas para outra categoria e tenta novamente

### Regras de Negócio

- `BR-F04`: Cada categoria tem allocated_budget (orçado)
- `BR-F06`: Categoria com despesas NÃO pode ser excluída — deve reatribuir primeiro
- Categoria pertence a 1 Budget, que pertence a 1 Wedding
- Total orçado = soma de todas as categorias

---

## UC03: Gerenciar Despesas

| Campo | Descrição |
|-------|-----------|
| **ID** | UC03 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista precisa registrar um gasto |
| **Prioridade** | ⭐⭐⭐⭐⭐ Essencial |
| **Complexidade** | ⭐⭐⭐☆☆☆ |

### Fluxo Principal: Criar Despesa com Parcelamento

1. Cerimonialista acessa "Despesas" de um casamento (sub-tab Despesas)
2. Clica em "Nova Despesa"
3. Sistema exibe formulário:
   - Nome da despesa (obrigatório) — identificador principal
   - Descrição (opcional) — detalhamento adicional
   - Categoria
   - Contrato (opcional)
   - Valor estimado
   - Valor realizado
   - Número de parcelas (mínimo 1, default 1)
   - Data de vencimento da primeira parcela (default hoje)
4. Cerimonialista preenche e confirma
5. Sistema cria a Expense com 1+ parcelas
6. Sistema **auto-gera as parcelas** com:
   - Cálculo exato do valor de cada parcela
   - Ajuste automático na última parcela se houver resto (BR-F01)
   - Datas de vencimento sequenciais (30 dias entre cada)
7. Sistema exibe despesa na tabela com status **Pendente**

### Fluxo Alternativo: Editar Despesa

1. Cerimonialista clica em ⋮ → "Editar" na tabela de despesas
2. Sistema exibe formulário pré-preenchido com: nome, descrição, contrato, valores
3. Opcional: alterar número de parcelas → dispara remanejamento (ver UC04)
4. Se houver parcelas pagas → campos de valor e parcelas são bloqueados

### Fluxo Alternativo: Excluir Despesa

1. Cerimonialista clica em ⋮ → "Excluir" na tabela
2. Sistema exibe diálogo de confirmação exigindo digitar o nome da despesa
3. Ao confirmar, todas as parcelas são removidas em cascata

### Fluxo Alternativo: Visualizar Detalhes da Despesa

1. Cerimonialista clica na linha da despesa na tabela
2. Sistema abre modal com:
   - Nome da despesa e status (Pendente/Parcial/Quitada)
   - Categoria, contrato vinculado, descrição
   - Barra de progresso: X/Y parcelas marcadas como pagas
   - Tabela de parcelas com: número, valor, vencimento, status
   - Botão "Marcar como Pago" em cada parcela pendente
   - Botão "Remanejar" para alterar número de parcelas

### Fluxo Alternativo: Gerar Despesa a partir de Documento

1. Cerimonialista está na aba Logística, visualizando um documento
2. Clica em "Gerar Despesa"
3. Sistema pré-preenche formulário da despesa com:
   - Valor de referência do documento
   - Fornecedor vinculado ao documento
   - Categoria sugerida (cerimonialista confirma)
4. Cerimonialista ajusta e confirma
5. Sistema cria a Expense com parcelas auto-geradas
6. Sistema vincula a Expense ao Documento de origem
7. **Benefício:** Cerimonialista não cadastra a mesma informação duas vezes

### Regras de Negócio

- `BR-F01`: Soma das parcelas = actual_amount (tolerância zero)
- `BR-F07`: Toda despesa tem no mínimo 1 parcela
- `BR-F08`: Remanejamento de parcelas só se nenhuma estiver paga
- `BR-F09`: Status da despesa é derivado das parcelas (Pending → Partial → Settled)
- `BR-F10`: Nome da despesa é obrigatório; descrição é opcional
- `BR-F06`: Parcelas pagas são imutáveis
- Expense vinculada a BudgetCategory e Wedding

---

## UC04: Gerenciar Parcelas

| Campo | Descrição |
|-------|-----------|
| **ID** | UC04 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista precisa controlar pagamentos |
| **Prioridade** | ⭐⭐⭐⭐☆ Importante |
| **Complexidade** | ⭐⭐⭐☆☆☆ |

### Fluxo Principal: Marcar Parcela como Paga

1. Cerimonialista acessa o modal de detalhes da despesa
2. Visualiza tabela de parcelas com: número, valor, vencimento, status
3. Clica "Marcar como Pago" em uma parcela pendente/vencida
4. Sistema marca parcela como `PAID` com `paid_date = hoje` (BR-F06)
5. Sistema revalida Tolerância Zero na despesa pai
6. Status da despesa é recalculado automaticamente:
   - Todas pagas → `SETTLED` (Quitada)
   - Algumas pagas → `PARTIALLY_PAID` (Parcial)
7. Modal permanece aberto para o cerimonialista marcar outras parcelas

### Fluxo Alternativo: Marcação em Lote (via lista de vencimentos)

1. Cerimonialista visualiza o card "Próximos Vencimentos" no dashboard do casamento
2. Clica "Marcar como Pago" diretamente em uma parcela listada
3. Sistema processa e recarrega a lista

### Fluxo Alternativo: Parcela Vencida

1. Comando `mark_overdue_installments` (execução diária) varre parcelas
2. Parcela com `due_date < hoje` e `status = PENDING` → marcada `OVERDUE`
3. No frontend, parcelas `OVERDUE` exibem badge vermelho + ícone de alerta
4. Cerimonialista pode marcar como paga normalmente (pagamento em atraso)

### Fluxo Alternativo: Remanejar Parcelas

1. Cerimonialista abre o modal de detalhes da despesa
2. Clica em "Remanejar" ao lado do título "Parcelas"
3. Sistema expande formulário inline: novo número de parcelas, nova data da 1ª
4. **Validação:** se houver alguma parcela `PAID` → botão "Remanejar" não aparece
5. Se nenhuma paga: cerimonialista preenche e clica "Aplicar"
6. Sistema deleta parcelas existentes e regera com o novo número (BR-F08)
7. Tudo em uma transação atômica

### Fluxo Alternativo: Ajustar Parcela Individual

1. Cerimonialista pode ajustar data/valor de uma parcela futura (não paga)
2. `PATCH /installments/{uuid}/adjust/` — endpoint dedicado
3. Validações:
   - Parcela `PAID` não pode ser ajustada
   - Data não pode ser anterior à parcela anterior

### Regras de Negócio

- Parcelas `PAID` não podem ser alteradas (BR-F06)
- `OVERDUE` gerado automaticamente via comando diário (BR-F05)
- Remanejamento bloqueado se houver parcelas pagas (BR-F08)
- Ordem cronológica das parcelas deve ser mantida no ajuste

---

## Critérios de Aceitação

### UC02: Criar Categoria
- [ ] Categoria vinculada ao Budget do casamento
- [ ] Total orçado recalculado automaticamente
- [ ] Alerta ao reduzir orçamento abaixo do gasto
- [ ] Bloqueio ao excluir categoria com despesas vinculadas
- [ ] Opção de reatribuir despesas para outra categoria antes de excluir

### UC03: Criar Despesa com Parcelamento
- [ ] Parcelas geradas somam EXATAMENTE o valor total
- [ ] Última parcela ajustada automaticamente se houver resto
- [ ] Vincular a categoria de orçamento é obrigatório
- [ ] Fornecedor e documento são opcionais
- [ ] Despesa pode ser gerada a partir de um Documento da Logística (pré-preenchido)

### UC04: Registrar Pagamento
- [ ] Parcela marcada como PAID
- [ ] Saldo da categoria atualizado
- [ ] Parcela paga não pode ser alterada
- [ ] Parcela vencida marcada OVERDUE automaticamente

---

## Diagrama de Transições de Status

### Parcela
```
PENDING → PAID
       → OVERDUE (automático se data passou)
       → PAID (pago após vencer)
```

---

## Relacionamentos com Outros Módulos

| Relação | Módulo |
|---------|--------|
| Despesa ← Documento (opcional) | `04-logistica.md` - UC07 |
| Despesa → Fornecedor (opcional) | `04-logistica.md` - UC05 |
| Dashboard do Casamento | `02-casamentos.md` - Aba Geral |

---

**Última atualização:** 4 de maio de 2026
**Versão:** 1.2 - Sprint 1: CRUD despesas + marcar como pago + remanejar + name/description
**Módulo:** Financeiro
**Voltar:** [index.md](./index.md)

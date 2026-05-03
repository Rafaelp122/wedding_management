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

1. Cerimonialista acessa "Despesas" de uma categoria
2. Clica em "Nova Despesa"
3. Sistema exibe formulário:
   - Descrição
   - Categoria (pré-selecionada)
   - Fornecedor (vinculado ou novo)
   - Valor total (actual_amount)
   - Número de parcelas
   - Data de vencimento da primeira parcela
   - Documento de referência (opcional - ver UC07)
4. Cerimonialista preenche e confirma
5. Sistema cria a Expense
6. Sistema **auto-gera as parcelas** com:
   - Cálculo exato do valor de cada parcela
   - Ajuste automático na última parcela se houver resto
   - Datas de vencimento sequenciais
7. Sistema exibe despesa com parcelas geradas

### Fluxo Alternativo: Despesa sem Vinculação (Avulsa)

1. Cerimonialista cria despesa sem fornecedor ou documento
2. Sistema permite (gastos avulsos como estacionamento, táxi)
3. Parcelamento funciona da mesma forma

### Fluxo Alternativo: Editar Despesa

1. Cerimonialista altera valor ou número de parcelas
2. Sistema valida: se alguma parcela já foi paga → recalcula apenas parcelas futuras
3. Se todas pagas → não permite alteração (BR-FUT01)

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
- `BR-L03`: Auto-geração de parcelas com ajuste automático na última
- `BR-FUT01`: Parcelas pagas são imutáveis
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

### Fluxo Principal: Registrar Pagamento

1. Cerimonialista acessa parcelas de uma despesa
2. Visualiza grid com: vencimento, valor, status, dias até vencer
3. Clica "Pagar" em uma parcela
4. Sistema marca parcela como `PAID`
5. Sistema atualiza saldo da categoria

### Fluxo Alternativo: Parcela Vencida

1. Parcela com data de vencimento passada e status ≠ PAID
2. Sistema marca automaticamente como `OVERDUE`
3. Cerimonialista recebe notificação (in-app + email)
4. Cerimonialista pode pagar ou renegociar

### Fluxo Alternativo: Ajustar Parcela

1. Cerimonialista altera data de vencimento de parcela futura
2. Sistema valida: não pode alterar para antes da parcela anterior
3. Sistema permite alterar valor de parcela futura
4. Se alterar valor: sistema recalcula parcelas seguintes

### Regras de Negócio

- Parcelas `PAID` não podem ser alteradas
- `OVERDUE` gera alerta automático (BR-FUT05)
- Ordem cronológica das parcelas deve ser mantida

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

**Última atualização:** 2 de maio de 2026
**Versão:** 1.1 - Proteção de categoria + sincronização Documento→Despesa
**Módulo:** Financeiro
**Voltar:** [index.md](./index.md)

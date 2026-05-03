# 📄 Módulo de Relatórios

## Estrutura de Navegação

```
💒 Casamento → Aba 📋 Geral → Botão "Exportar Relatório"
```

---

## UC11: Exportar Relatórios

| Campo | Descrição |
|-------|-----------|
| **ID** | UC11 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista precisa apresentar informações para o cliente |
| **Prioridade** | ⭐⭐⭐☆☆ Médio |
| **Complexidade** | ⭐⭐☆☆☆☆ |

### Fluxo Principal: Relatório Financeiro para Cliente

1. Cerimonialista acessa o dashboard de um casamento (aba Geral)
2. Clica em "Exportar Relatório"
3. Seleciona tipo: "Resumo Financeiro para Cliente"
4. Sistema gera relatório em PDF com:
   - Informações básicas do casamento (data, local, convidados)
   - Tabela de gastos por categoria
   - Gráfico orçado vs realizado
   - Status de pagamentos (total pago, a pagar)
   - Próximos vencimentos
5. Sistema faz download do PDF

### Fluxo Alternativo: Relatório para Controle Interno

1. Cerimonialista seleciona tipo: "Planilha de Controle"
2. Sistema gera arquivo Excel com:
   - Todas as despesas detalhadas
   - Fornecedores e valores
   - Status de cada parcela
   - Categorias de orçamento
3. Sistema faz download do Excel

### Formatos Suportados

| Formato | Finalidade | Conteúdo |
|---------|-----------|----------|
| **PDF** | Apresentação para cliente | Resumo visual, gráficos, sem margem do planner |
| **Excel** | Controle interno do planner | Detalhamento completo, todas as despesas |

### Regras de Negócio

- Relatório PDF não exibe valores de margem/lucro do cerimonialista
- Relatório contém apenas dados do casamento selecionado
- Excel pode conter dados completos para edição
- Dados exportados respeitam multi-tenancy

---

## Critérios de Aceitação

- [ ] PDF gerado com layout profissional e apresentável
- [ ] Excel gerado com colunas organizadas para edição
- [ ] Relatório não exibe margem do cerimonialista
- [ ] Download inicia em menos de 3 segundos
- [ ] Dados apenas do casamento selecionado

---

## Relacionamentos com Outros Módulos

| Relação | Módulo |
|---------|--------|
| Dados financeiros exportados | `03-financeiro.md` - UC02, UC03, UC04 |
| Dados do casamento | `02-casamentos.md` - UC01 |
| Dashboard com botão de exportar | `02-casamentos.md` - Aba Geral |

---

**Última atualização:** 2 de maio de 2026
**Versão:** 1.0
**Módulo:** Relatórios
**Voltar:** [index.md](./index.md)

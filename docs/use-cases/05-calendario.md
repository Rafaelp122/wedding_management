# 📅 Módulo de Cronograma e Alertas

## Estrutura de Navegação

```
Sidebar → 📅 Calendário → Calendário GLOBAL (eventos de todos os casamentos)

💒 Casamento → Aba 📅 Cronograma → Calendário específico do casamento
```

---

## UC08: Gerenciar Cronograma

| Campo | Descrição |
|-------|-----------|
| **ID** | UC08 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista precisa organizar prazos |
| **Prioridade** | ⭐⭐⭐⭐☆ Importante |
| **Complexidade** | ⭐⭐⭐☆☆☆ |

### Fluxo Principal: Calendário Global

1. Cerimonialista acessa "Calendário" na sidebar
2. Sistema exibe calendário com eventos de **todos** os casamentos
3. Cada evento é colorido por casamento e por tipo
4. Cerimonialista pode:
   - Filtrar por casamento
   - Filtrar por tipo de evento

### Fluxo Principal: Criar Evento no Cronograma

1. Cerimonialista acessa "Cronograma" de um casamento
2. Visualiza calendário com eventos do casamento
3. Clica em "Novo Evento"
4. Sistema exibe formulário:
   - Título (ex: "Prova de vestido", "Reunião com buffet")
   - Data e hora
   - Descrição
   - Tipo: `MEETING`, `DEADLINE`, `DELIVERY`, `PAYMENT`
5. Cerimonialista preenche e confirma
6. Sistema salva evento vinculado ao casamento
7. Sistema exibe no calendário

### Fluxo Alternativo: Evento Recorrente

1. Cerimonialista marca evento como "semanal" ou "mensal"
2. Sistema replica o evento nas datas seguintes

### Regras de Negócio

- Eventos pertencem a 1 casamento
- Eventos gerados automaticamente por parcelas (PAYMENT)
- Tipos de evento permitem filtro visual
- Eventos `DEADLINE` e `PAYMENT` geram alertas automáticos

---

## UC09: Receber Alertas e Notificações

| Campo | Descrição |
|-------|-----------|
| **ID** | UC09 |
| **Ator** | Cerimonialista |
| **Gatilho** | Prazo se aproximando ou atraso |
| **Prioridade** | ⭐⭐⭐⭐☆ Importante |
| **Complexidade** | ⭐⭐⭐☆☆☆ |

### Fluxo Principal: Alerta de Parcela a Vencer

1. Sistema identifica parcelas com vencimento em ≤ 7 dias
2. Sistema envia email para cerimonialista:
   - "3 parcelas vencem esta semana: Fornecedor A (R$ 500), B (R$ 1.200), C (R$ 300)"
3. Sistema exibe notificação in-app (badge + lista)

### Fluxo Alternativo: Parcela Vencida (OVERDUE)

1. Sistema identifica parcelas com data de vencimento passada e status ≠ PAID
2. Sistema marca automaticamente como `OVERDUE`
3. Sistema envia alerta in-app + email
4. Cerimonialista acessa e paga ou renegocia

### Fluxo Alternativo: Documento a Vencer

1. Sistema identifica documentos com expiration_date em ≤ 30 dias
2. Sistema envia alerta: "Documento X vence em Y dias"
3. Conteúdo inclui disclaimer: "Consulte seu advogado para renovação"

### Canais de Notificação

| Canal | Prioridade | Conteúdo |
|-------|-----------|----------|
| **In-App (Badge)** | Imediato | Contador de alertas na sidebar |
| **Email** | Diário | Resumo de vencimentos do dia |
| **WhatsApp Link** | Manual | Link wa.me com mensagem pré-preenchida |

### Regras de Negócio

- `BR-FUT05`: Automação OVERDUE atualiza parcelas vencidas
- Notificações agrupadas por urgência
- Cerimonialista configura frequência (diária/semanal)

---

## Critérios de Aceitação

### UC08: Cronograma
- [ ] Calendário global mostra eventos de todos os casamentos
- [ ] Calendário do casamento mostra apenas eventos daquele casamento
- [ ] Eventos de parcelas PAYMENT gerados automaticamente
- [ ] Filtros por tipo e casamento disponíveis

### UC09: Alertas
- [ ] Notificação in-app aparece imediatamente
- [ ] Email enviado com resumo diário
- [ ] OVERDUE marcado automaticamente
- [ ] Documento com vencimento alertado com disclaimer

---

## Relacionamentos com Outros Módulos

| Relação | Módulo |
|---------|--------|
| Eventos PAYMENT gerados por parcelas | `03-financeiro.md` - UC04 |
| Alertas de documentos | `04-logistica.md` - UC07 |
| Dashboard global mostra próximos eventos | `01-dashboard-global.md` - UC10 |

---

**Última atualização:** 2 de maio de 2026
**Versão:** 1.0
**Módulo:** Cronograma
**Voltar:** [index.md](./index.md)

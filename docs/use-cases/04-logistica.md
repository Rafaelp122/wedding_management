# 📦 Módulo de Logística

## Estrutura de Navegação

```
Sidebar → 🤝 Fornecedores → Listagem GLOBAL de todos os fornecedores da empresa
                               ├── Novo Fornecedor
                               └── [Clica no fornecedor] → Casamentos vinculados

💒 Casamento → Aba 📦 Logística
                ├── Fornecedores vinculados
                ├── Itens / Serviços
                └── Documentos de referência
```

---

## UC05: Gerenciar Fornecedores

| Campo | Descrição |
|-------|-----------|
| **ID** | UC05 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista contrata um fornecedor |
| **Prioridade** | ⭐⭐⭐⭐☆ Importante |
| **Complexidade** | ⭐⭐☆☆☆☆ |

### Fluxo Principal: Cadastrar Fornecedor

1. Cerimonialista acessa "Fornecedores" na sidebar
2. Clica em "Novo Fornecedor"
3. Sistema exibe formulário:
   - Nome
   - Categoria de serviço (buffet, decoração, fotografia...)
   - Contato (telefone, email)
   - Observações (campo livre)
4. Cerimonialista preenche e confirma
5. Sistema salva fornecedor vinculado à **empresa** do cerimonialista
6. Fornecedor fica disponível globalmente para todos os casamentos

### Fluxo Alternativo: Reutilizar Fornecedor em um Casamento

1. Cerimonialista está dentro de um casamento (aba Logística)
2. Cria uma despesa e seleciona "Fornecedor"
3. Sistema exibe lista de fornecedores cadastrados na empresa
4. Cerimonialista seleciona existente ou cria novo
5. Sistema vincula fornecedor à despesa do casamento

### Fluxo Alternativo: Ver Fornecedores de um Casamento

1. Cerimonialista acessa aba Logística de um casamento
2. Sistema exibe lista de fornecedores vinculados a este casamento
3. Exibe também em quantas despesas ele foi usado neste casamento

### Regras de Negócio

- `BR-SEC01`: Fornecedor pertence à **empresa**, não ao casamento
- Pode ser reaproveitado entre casamentos da mesma empresa
- Campo `notes` para informações internas (ex: "Só atende SP capital")

---

## UC06: Gerenciar Itens / Serviços

| Campo | Descrição |
|-------|-----------|
| **ID** | UC06 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista precisa listar o que foi contratado |
| **Prioridade** | ⭐⭐⭐☆☆ Médio |
| **Complexidade** | ⭐⭐☆☆☆☆ |

### Fluxo Principal: Criar Item

1. Cerimonialista acessa "Itens" dentro da aba Logística de um casamento
2. Clica em "Novo Item"
3. Sistema exibe formulário:
   - Descrição (ex: "Buquê de rosas vermelhas")
   - Quantidade
   - Fornecedor
   - Categoria de orçamento
   - Status: `PENDING` → `IN_PROGRESS` → `DONE`
4. Cerimonialista preenche e confirma
5. Sistema salva item vinculado ao casamento e categoria

### Fluxo Alternativo: Atualizar Status

1. Cerimonialista marca item como `IN_PROGRESS`
2. Sistema permite anexar observação
3. Cerimonialista marca como `DONE` quando entregue

### Regras de Negócio

- `BR-L05`: Status do item é **independente** do status financeiro
- Item vinculado a BudgetCategory para rastreabilidade
- Quantidade e status permitem controle de entregas parciais

---

## UC07: Gerenciar Documentos de Referência

| Campo | Descrição |
|-------|-----------|
| **ID** | UC07 |
| **Ator** | Cerimonialista |
| **Gatilho** | Cerimonialista recebe PDF de orçamento/contrato do fornecedor |
| **Prioridade** | ⭐⭐⭐☆☆ Médio |
| **Complexidade** | ⭐⭐⭐☆☆☆ |

### Fluxo Principal: Upload de Documento

1. Cerimonialista acessa "Documentos" dentro da aba Logística de um casamento
2. Clica em "Upload"
3. Sistema solicita arquivo PDF
4. Cerimonialista seleciona PDF
5. Sistema faz upload direto para R2 via presigned URL
6. Sistema exibe preview do documento
7. Cerimonialista preenche metadados opcionais:
   - Valor de referência
   - Data de vencimento
8. Sistema salva documento vinculado à despesa

### Fluxo Alternativo: Documento sem Despesa

1. Cerimonialista faz upload de documento geral do casamento
2. Sistema permite vincular ao casamento (não a despesa específica)
3. Útil para: contrato geral, plantas do local, referências diversas

### Fluxo Alternativo: Gerar Despesa a partir do Documento

**Automação Logística → Financeiro**

1. Cerimonialista visualiza um documento na aba Logística
2. Clica em "Gerar Despesa"
3. Sistema pré-preenche formulário da despesa:
   - **Valor:** preenchido com `reference_amount` do documento
   - **Fornecedor:** vinculado ao documento (se houver)
   - **Descrição:** sugestão baseada no nome do documento
   - **Categoria:** cerimonialista seleciona
   - **Parcelas:** cerimonialista define quantidade
4. Cerimonialista ajusta e confirma
5. Sistema cria a Expense e vincula ao Documento de origem
6. Sistema auto-gera as parcelas
7. **Resultado:** Cerimonialista não cadastra a mesma informação duas vezes

### ⚠️ Disclaimer Exibido

```
"Este sistema não substitui consultoria jurídica.
Documentos são armazenados apenas para referência."
```

### Regras de Negócio

- Upload via presigned URL (não passa pelo backend)
- PDF até 50MB
- Documento é apenas referência, sem validade jurídica
- Alerta de vencimento enviado se expiration_date preenchida

---

## Critérios de Aceitação

### UC05: Fornecedores
- [ ] Fornecedor cadastrado fica disponível para todos os casamentos
- [ ] Mesmo fornecedor pode ser usado em múltiplos casamentos
- [ ] Logística do casamento mostra apenas fornecedores vinculados

### UC06: Itens
- [ ] Status do item independente do financeiro
- [ ] Quantidade permite controle de entregas parciais
- [ ] Item vinculado a categoria de orçamento

### UC07: Documentos
- [ ] Upload via presigned URL (sem travar o backend)
- [ ] Disclaimer visível antes do upload
- [ ] Documento vinculado a despesa ou casamento
- [ ] Botão "Gerar Despesa" disponível na visualização do documento
- [ ] Despesa gerada pré-preenchida com dados do documento
- [ ] Alerta enviado se data de vencimento preenchida

---

## Relacionamentos com Outros Módulos

| Relação | Módulo |
|---------|--------|
| Documento → Despesa (opcional) | `03-financeiro.md` - UC03 |
| Item → Categoria de Orçamento | `03-financeiro.md` - UC02 |
| Fornecedor → Despesas | `03-financeiro.md` - UC03 |
| Fornecedores (sidebar global) | `index.md` - Navegação |

---

**Última atualização:** 2 de maio de 2026
**Versão:** 1.1 - Automação Documento→Despesa adicionada
**Módulo:** Logística
**Voltar:** [index.md](./index.md)

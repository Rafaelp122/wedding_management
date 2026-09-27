# Especificação de Requisitos de Software (SRS) — Wedding Management System (Release 1.0 - MVP Web)

> **Documento de Origem & Negócio:** [Documento de Modelagem de Negócio e Visão do Produto](business-vision.md)
> **Catálogo Canônico de Regras:** [Catálogo de Regras de Negócio e Invariantes de Domínio](business-rules/index.md)
> **Topologia Arquitetural:** [Topologia Geral de Domínios e Bounded Contexts](domains/index.md)

---

## 1. Glossário do Domínio (Linguagem Ubíqua)

- **Assessoria Cerimonial (Tenant / `Company`):** Empresa cliente do SaaS B2B que planeja, orquestra e executa múltiplos casamentos. Representa o limite lógico de isolamento de dados no sistema.
- **Cliente (`Client`):** Entidade cadastral centralizada (`apps.clients`) que atua como Única Fonte da Verdade (SSOT) para dados de identificação e contato de pessoas físicas (nome, CPF, e-mail, telefone), reutilizável entre casamentos e isolada por tenant (`Company`).
- **Participante do Casamento (`WeddingClient`):** Entidade associativa (`apps.weddings`) que conecta um `Client` a um `Wedding`, especificando seu papel (`RoleChoices`: Noiva, Noivo, Pagador Financeiro, etc.) e sinalizando o signatário principal (`is_primary_signatory`).
- **Casamento (`Wedding`):** Entidade raiz de negócio que encapsula um evento matrimonial específico, com dados do contratante principal, noivos, data planejada da celebração, contagem de convidados e orçamento vinculado. Ciclo de vida: `PROPOSTA` $\to$ `PLANEJAMENTO` $\to$ `EM_ANDAMENTO` $\to$ `CONCLUIDO` (ou `CANCELADO`).
- **Contrato de Assessoria (`PlannerContract` / `Contract`):** Acordo formal de prestação de serviços e honorários firmado entre a assessoria e os contratantes do casamento. No modelo unificado, é representado pela entidade `Contract` com `contract_type="PLANNER"` (`apps.contracts`), acessado via fachada pública desacoplada (`apps.contracts.interfaces`) e exposto em schemas de API dedicados (`PlannerContractIn`/`PlannerContractOut`).
- **Teto Orçamentário (`Budget`):** Limite financeiro estimado total definido pela assessoria e pelo casal para a realização integral do casamento (relação 1:1 com o Casamento). Atua como simulação dinâmica em `PROPOSTA` e como Linha de Base (*baseline*) congelada a partir de `PLANEJAMENTO`.
- **Categoria Orçamentária (`BudgetCategory`):** Centro de custo temático (ex.: Buffet, Decoração, Fotografia, Espaço) que recebe uma fração alocada do orçamento global, com suporte a percentuais recomendados e criação de categorias customizadas.
- **Despesa (`Expense`):** Registro formal de um compromisso de gasto financeiro com fornecedor ou item, classificado em uma categoria orçamentária e com valor real acordado.
- **Tolerância Zero Centesimal:** Princípio contábil invariante que proíbe qualquer divergência de centavos entre o valor total de uma despesa e a soma das suas parcelas (\(\sum P_i \equiv V_{\text{total}}\)).
- **Parcela (`Installment`):** Desdobramento temporal de pagamento de uma despesa, caracterizado por valor centesimal, data de vencimento e status (`PENDING`, `PAID`, `OVERDUE`).
- **Fornecedor (`Supplier`):** Parceiro comercial (`apps.suppliers`) cadastrado no catálogo corporativo do tenant, com identificação fiscal auditada (CNPJ via Módulo 11) e reutilizável entre casamentos.
- **Contrato Legal com Terceiros (`Contract`):** Instrumento jurídico formal firmado com fornecedores prestadores de serviço (`apps.contracts`), possuindo valor base de face, minuta em PDF e ciclo de vida (`DRAFT` $\to$ `PENDING` $\to$ `SIGNED` $\to$ `CANCELED`).
- **Termo Aditivo Contratual (`ContractAddendum`):** Entidade filha dedicada vinculada (1:N) a um contrato principal para representar formalmente acréscimos financeiros, alterações de escopo ou prorrogações, agregando valor ao contrato (\(V_{\text{efetivo}} = V_{\text{base}} + \sum V_{\text{aditivos}}\)) sem auto-relacionamento circular.
- **Item de Suprimento Logístico (`SupplyItem`):** Bem material, suprimento físico ou insumo a ser mobilizado para o casamento (`apps.logistics`), gerenciado em 3 dimensões: escopo (`DESIRED`, `INCLUDED`, `DISCARDED` com justificativa obrigatória), cotação/compra e conferência física de entrega (`delivery_status`).
- **Item de Checklist Operacional (`ChecklistItem`):** Pendência operacional com prazo limite (`due_date`), prioridade e marcação booleana (`is_completed`), desacoplada da agenda e com nomenclatura distinta das tarefas assíncronas do sistema (`django.tasks`).
- **Evento de Agenda (`Event`):** Compromisso com data/hora de início e término (`start_time`, `end_time`) na agenda da assessoria (`apps.scheduler`), com detecção inteligente de conflitos suaves (*soft overlap*).
- **Template de Cronograma (`ScheduleTemplate`):** Conjunto padronizado de marcos e compromissos pré-calculados em dias relativos ($D - X$) à data da celebração, com presets de fábrica e personalização pela assessoria.
- **DTO Analítico (Data Transfer Object):** Objeto imutável projetado em consultas otimizadas no banco de dados para alimentar dashboards e relatórios executivos sem sobrecarga de rede.

---

## 2. Requisitos Funcionais (RF) — Nível de Objetivo do Usuário

### Módulo 1: Identidade, Acesso e Multitenancy (Tenants & Users)

#### RF-01 — Isolamento Lógico Multitenant de Dados (RBAC & Tenancy)
- **Descrição:** O sistema deve garantir que usuários autenticados acessem exclusivamente casamentos, orçamentos, contratos e registros pertencentes à sua empresa (`Company`), bloqueando compulsoriamente tentativas de leitura ou escrita cross-tenant.
- **Regras de Negócio Vinculadas:** [BR-T01 (Isolamento Lógico Row-Level)](domains/tenants-domain.md) e [BR-T04 (Propagação Obrigatória de Tenant)](domains/tenants-domain.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Isolamento de Listagem):* Dado que o usuário $A$ pertence à empresa $X$ e o usuário $B$ pertence à empresa $Y$, quando o usuário $A$ listar casamentos, o sistema retorna apenas os registros vinculados à empresa $X$.
  - *Cenário 2 (Bloqueio de Acesso Indevido):* Quando o usuário $A$ tentar acessar via UUID direto um contrato pertencente à empresa $Y$, o sistema responde com erro `HTTP 404 Not Found` (ocultando a existência do recurso por segurança).

#### RF-02 — Onboarding de Empresa e Usuário Proprietário
- **Descrição:** O sistema deve permitir que uma nova assessoria cerimonial realize seu cadastro autônomo, criando em uma transação atômica a entidade corporativa (`Company`) com slug único e a conta do usuário administrador proprietário (`Owner`).
- **Regras de Negócio Vinculadas:** [BR-U03 (Onboarding Atômico de Owner + Empresa)](domains/users-domain.md) e [BR-T02 (Geração de Slug Anti-Colisão)](domains/tenants-domain.md).
- **Critérios de Aceitação:**
  - *Cenário:* Ao submeter o formulário de registro com nome da assessoria, e-mail e senha, o sistema persiste a empresa, vincula o usuário como `Owner` com `on_delete=PROTECT` e despacha e-mail de confirmação de conta.

#### RF-03 — Autenticação Segura JWT e Login Social Google OAuth2
- **Descrição:** O sistema deve prover autenticação baseada em tokens JWT (`access` e `refresh`), recuperação de senha via token temporário e login com um clique via Google OAuth2, protegendo todas as rotas públicas com limitadores de requisição (Rate Limiting).
- **Regras de Negócio Vinculadas:** [BR-U01 (Normalização de E-mail)](domains/users-domain.md), [BR-U04 (Verificação Preventiva)](domains/users-domain.md) e [BR-U05 (Login Google com Auto-Provisionamento)](domains/users-domain.md).
- **Critérios de Aceitação:**
  - *Cenário 1:* Submissão de credenciais válidas retorna par de tokens JWT com expiração configurada e perfil de usuário.
  - *Cenário 2:* Requisições anônimas consecutivas que excedam o limite da rota são bloqueadas com `HTTP 429 Too Many Requests`.

#### RF-03B — Gestão Centralizada de Clientes e Participantes do Casamento (Client & WeddingClient)
- **Descrição:** O sistema deve gerenciar um cadastro centralizado de clientes (`apps.clients`) como Única Fonte da Verdade (SSOT) no nível da assessoria (`Company`), validando formato e unicidade do CPF, e associando clientes a casamentos através da entidade `WeddingClient` com papéis semânticos (`RoleChoices`: Noiva, Noivo, Pagador Financeiro, Representante Legal, Outro) e designação do signatário principal (`is_primary_signatory`).
- **Regras de Negócio Vinculadas:** [BR-CLI-01 a BR-CLI-03 (Regras de Clientes)](domains/clients-domain.md) e [RFC-001 (SSOT de Clientes)](rfc/001-macro-architecture-and-domain-redesign.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Reutilização e Unicidade):* Ao cadastrar um cliente com CPF já existente na mesma empresa, o sistema reutiliza o registro existente em vez de duplicar.
  - *Cenário 2 (Proposta com Criação Automática):* Na criação de uma proposta de casamento via `/api/v1/weddings/proposals/`, os dados do contratante principal são processados via interface `get_or_create_client_for_proposal()`, criando compulsoriamente a associação `WeddingClient` com `is_primary_signatory=True` e `role=FINANCIAL_PAYER`.
  - *Cenário 3 (Múltiplos Participantes):* Um casamento permite associar múltiplos clientes com papéis distintos (ex.: Noiva e Noivo), garantindo que apenas um signatário principal seja eleito como responsável contratual.

---

### Módulo 2: Gestão de Casamentos (Weddings)

#### RF-04 — Gestão do Ciclo de Vida do Casamento e Contrato de Assessoria
- **Descrição:** O sistema deve permitir o cadastro do casamento desde a fase preliminar de captação (`PROPOSTA`), onde a assessoria realiza simulação orçamentária e proposta de honorários profissionais. A gestão dos honorários utiliza o modelo unificado de contratos (`Contract` com `contract_type="PLANNER"` em `apps.contracts`), acessado via fachada pública desacoplada (`apps.contracts.interfaces`). A conversão para `PLANEJAMENTO` (`/convert-to-planning/`) congela a linha de base do orçamento mestre (`Budget.baseline_amount`), agenda o template de cronograma e gera o lançamento financeiro da assessoria, prosseguindo pelas etapas `EM_ANDAMENTO` $\to$ `CONCLUIDO` (ou `CANCELADO`).
- **Regras de Negócio Vinculadas:** [BR-W02 (Data Inicial no Futuro)](business-rules/weddings/wedding-status-lifecycle.md), [BR-W04 (Ordenação Cronológica)](business-rules/weddings/wedding-status-lifecycle.md), [BR-W05 (Transição Legal de Status)](business-rules/weddings/wedding-status-lifecycle.md), [BR-F04 (Baseline Congelada)](business-rules/finances/budget-category-distribution.md) e [RFC-001 (Ciclo de Vida E2E)](rfc/001-macro-architecture-and-domain-redesign.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Simulação em PROPOSTA):* Um casamento criado em `PROPOSTA` permite simular valores e categorias sem travar a linha de base contábil nem exigir data definitiva imutável.
  - *Cenário 2 (Ativação para PLANEJAMENTO):* Ao acionar `/convert-to-planning/` com o contrato da assessoria formalizado (`is_planner_contract_signed`), o sistema congela a baseline do orçamento via `freeze_budget_baseline_for_wedding()`, gera a despesa de honorários em finanças e enfileira a aplicação do template de cronograma.
  - *Cenário 3 (Data Passada Rejeitada):* A tentativa de criar ou ativar um casamento com data de celebração anterior à data atual do sistema deve ser rejeitada com `HTTP 400 Bad Request`.
  - *Cenário 4 (Transição Inválida):* A tentativa de transitar um casamento de `PLANEJAMENTO` diretamente para `CONCLUIDO` sem passar por `EM_ANDAMENTO` deve disparar erro de violação de máquina de estados.

#### RF-05 — Aplicação de Templates Canônicos de Cronograma
- **Descrição:** Ao criar ou configurar um casamento, o assessor deve poder selecionar um template predefinido de cronograma ("Clássico", "Minimalista", "Destination Wedding"), gerando automaticamente marcos e compromissos calculados em dias relativos à data do casamento.
- **Regras de Negócio Vinculadas:** [BR-W07 (Templates Canônicos de Cronograma)](business-rules/weddings/wedding-schedule-templates.md).
- **Critérios de Aceitação:**
  - *Cenário:* Ao escolher o template "Clássico" para um casamento agendado para daqui a 180 dias, o sistema cria automaticamente os eventos-chave com datas ajustadas retroativamente (ex.: Reunião de Buffet em $D-90$, Prova de Vestido em $D-60$).

#### RF-06 — Blindagem de Conclusão Prematura e Reabertura de Casamento
- **Descrição:** O sistema deve impedir que um casamento seja finalizado antes da data oficial da cerimônia e permitir que casamentos cancelados sejam reabertos, restaurando seu status para `EM_ANDAMENTO`.
- **Regras de Negócio Vinculadas:** [BR-W01 (Conclusão Prematura Bloqueada)](business-rules/weddings/wedding-status-lifecycle.md) e [BR-W06 (Reabertura de Casamento Cancelado)](business-rules/weddings/wedding-status-lifecycle.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Bloqueio de Conclusão):* Se a data da cerimônia for 15/12 e a data atual for 10/12, a ação de concluir o casamento deve ser bloqueada com mensagem explícita de violação.
  - *Cenário 2 (Reabertura):* Um casamento com status `CANCELADO` aciona o endpoint `/reopen/` e transita com sucesso para `EM_ANDAMENTO`.

---

### Módulo 3: Gestão Orçamentária e Financeira (Finances)

#### RF-07 — Definição de Teto e Distribuição Orçamentária por Categoria
- **Descrição:** O sistema deve permitir estabelecer um teto orçamentário global por casamento (`Budget`) e fracioná-lo em centros de custo (`BudgetCategory`), validando que a soma das alocações não ultrapasse o teto previsto.
- **Regras de Negócio Vinculadas:** [BR-F04-A..D (Distribuição e Teto Orçamentário por Categoria)](business-rules/finances/budget-category-distribution.md) e [BR-F06 (Benchmark da Assessoria)](business-rules/finances/tenant-budget-benchmark.md).
- **Critérios de Aceitação:**
  - *Cenário:* Para um orçamento mestre de R$ 100.000,00, a tentativa de alocar R$ 60.000,00 em Buffet e R$ 50.000,00 em Decoração (totalizando R$ 110.000,00) deve ser bloqueada pelo Service Layer sob trava pessimista (*select_for_update*).

#### RF-08 — Gestão de Despesas e Ancoragem Contratual
- **Descrição:** O sistema deve permitir registrar despesas vinculadas a uma categoria orçamentária e, opcionalmente, ancoradas a um contrato formal de fornecedor, assegurando paridade entre o valor da despesa e o valor de face do documento legal.
- **Regras de Negócio Vinculadas:** [BR-F02 (Conformidade Financeira com Contrato)](business-rules/finances/financial-integrity-rules.md) e [BR-F03 (Fronteira Cross-Wedding Guard)](business-rules/finances/financial-integrity-rules.md).
- **Critérios de Aceitação:**
  - *Cenário 1:* Ao criar uma despesa associada a um contrato de R$ 15.000,00, o valor real (`actual_amount`) da despesa deve ser inicializado compulsoriamente como R$ 15.000,00.
  - *Cenário 2 (Sugestão Inteligente):* O endpoint `/from-document/{uuid}` retorna o payload pré-preenchido com descrição, valor e fornecedor do contrato para aprovação rápida do assessor.

#### RF-09 — Parcelamento Inteligente com Tolerância Zero Centesimal
- **Descrição:** O sistema deve calcular planos de parcelamento automático dividindo o valor da despesa em até 24 parcelas com datas de vencimento configuráveis, absorvendo qualquer sobra de centavos na última parcela.
- **Regras de Negócio Vinculadas:** [BR-F01 (Tolerância Zero Centesimal)](business-rules/finances/financial-integrity-rules.md) e [ADR-010 (Tolerância Zero)](adr/010-tolerance-zero.md).
- **Critérios de Aceitação:**
  - *Cenário:* Uma despesa de R$ 1.000,00 dividida em 3 parcelas gera: Parcela 1 = R$ 333,33; Parcela 2 = R$ 333,33; Parcela 3 = R$ 333,34. A soma \(\sum P_i\) totaliza exatamente R$ 1.000,00. Qualquer discrepância de R$ 0,01 é rejeitada com `HTTP 422 Unprocessable Entity`.

#### RF-10 — Flexibilidade Financeira: Ajuste e Renegociação de Parcelas
- **Descrição:** O sistema deve permitir ajustar datas e valores de parcelas futuras ainda não pagas, bem como renegociar globalmente o parcelamento de uma despesa, desde que nenhuma parcela já quitada seja corrompida.
- **Regras de Negócio Vinculadas:** [BR-F01 (Imutabilidade de Quitação)](business-rules/finances/financial-integrity-rules.md) e [BR-F05 (Máquina de Estados de Parcelas)](business-rules/finances/installment-overdue-logic.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Ajuste Individual):* O assessor altera o vencimento da Parcela 3 de uma despesa sem alterar seu valor nem violar a ordem cronológica em relação à Parcela 2.
  - *Cenário 2 (Bloqueio de Renegociação):* Se a Parcela 1 já estiver marcada como `PAID`, a tentativa de renegociar globalmente o número de parcelas da despesa é bloqueada.

#### RF-11 — Controle de Pagamentos, Reversão e Status Derivado
- **Descrição:** O sistema deve registrar a liquidação de parcelas (`mark-as-paid`) com data efetiva, permitir o estorno de pagamentos indevidos (`unmark-as-paid`) e derivar o status da despesa (`PENDING` $\to$ `PARTIALLY_PAID` $\to$ `SETTLED`).
- **Regras de Negócio Vinculadas:** [BR-F05 (Ciclo de Vida de Parcelas)](business-rules/finances/installment-overdue-logic.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Quitação Total):* Ao liquidar a última parcela pendente de uma despesa, o status derivado da despesa transita automaticamente para `SETTLED` (Liquidada).
  - *Cenário 2 (Reversão):* Ao acionar `/unmark-as-paid/` em uma parcela, seu status retorna para `PENDING` (ou `OVERDUE` se o prazo já expirou) e o saldo devedor da despesa é recalculado.

---

### Módulo 4: Gestão de Fornecedores, Contratos e Suprimentos (Suppliers, Contracts & Logistics)

#### RF-12 — Catálogo Corporativo de Fornecedores e Validação de CNPJ (Módulo 11)
- **Descrição:** O sistema deve gerenciar um catálogo de fornecedores (`apps.suppliers`) compartilhado entre os casamentos da assessoria (`Company`), validando obrigatoriamente a integridade do CNPJ via algoritmo Módulo 11 com rejeição de sequências homogêneas repetidas.
- **Regras de Negócio Vinculadas:** [BR-SUP-01 / BR-SUP-02 (Regras de Fornecedores)](domains/suppliers-domain.md) e [BR-L05 (Validação e Sanitização de CNPJ)](business-rules/logistics/cnpj-validation-rules.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (CNPJ Válido):* Cadastro aceito com cálculo correto dos dígitos verificadores (DV1 e DV2), armazenando 14 dígitos puros e exibindo máscara formatada.
  - *Cenário 2 (CNPJ Falso Rejeitado):* Entrada de `11.111.111/1111-11` ou com DV incorreto é rejeitada com erro de validação sintática (HTTP 422).

#### RF-13 — Máquina de Estados de Contratos e Entidade Dedicada de Aditivos (ContractAddendum)
- **Descrição:** O sistema deve gerenciar o ciclo de vida contratual (`apps.contracts`: `DRAFT` $\to$ `PENDING` $\to$ `SIGNED` $\to$ `CANCELED`) tanto para fornecedores terceiros quanto para o contrato de assessoria, permitindo vincular Termos Aditivos através de entidade filha própria (`ContractAddendum` em relação 1:N), agregando valor ao contrato principal (\(V_{\text{efetivo}} = V_{\text{base}} + \sum V_{\text{aditivos}}\)) sem auto-relacionamentos circulares.
- **Regras de Negócio Vinculadas:** [BR-CON-01 / BR-CON-02 (Regras de Contratos)](domains/contracts-domain.md), [BR-L01 (Máquina de Estados de Contratos)](business-rules/logistics/contract-state-machine.md), [BR-L02 (Hierarquia e Aditivos)](business-rules/logistics/contract-parent-child-hierarchy.md) e [RFC-001 (Separação de Aditivos)](rfc/001-macro-architecture-and-domain-redesign.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Exigência para Assinatura):* Um contrato só transita para `SIGNED` se possuir `total_amount > 0`, data de assinatura e chave do arquivo PDF anexado.
  - *Cenário 2 (Aditivo em Entidade Filha):* Um termo aditivo (`ContractAddendum`) é criado obrigatoriamente associado a um contrato existente, com justificativa formal, valor de ajuste e documento comprobatório, atualizando em cascata o valor efetivo do contrato.

#### RF-14 — Custódia Digital e Upload de Documentos no Cloudflare R2
- **Descrição:** O sistema deve permitir o upload direto de minutas e contratos assinados em PDF para o Cloudflare R2 via Presigned URLs, evitando tráfego de binários pesados pelo backend Django.
- **Regras de Negócio Vinculadas:** [BR-C04 (Limite Defensivo de Upload)](domains/core-domain.md), [BR-CON-03 (Armazenamento Seguro de Minutas)](domains/contracts-domain.md) e [ADR-004 (Presigned URLs)](adr/004-presigned-urls.md).
- **Critérios de Aceitação:**
  - *Cenário:* O frontend solicita URL pré-assinada via `/upload-url/`, recebe a URL segura temporária (15 min) com HMAC SHA-256 e envia o binário via `HTTP PUT` diretamente ao bucket, confirmando a chave no contrato.

#### RF-15 — Gestão Multidimensional de Itens de Suprimento (SupplyItem)
- **Descrição:** O sistema deve permitir mapear itens físicos e suprimentos para o evento (`apps.logistics`) em três dimensões independentes: escopo (`DESIRED`, `INCLUDED`, `DISCARDED`), cotação/contratação (com fornecedor e contrato opcional) e status de entrega física no local (`PENDING` $\to$ `DELIVERED` $\to$ `RETURNED`). Itens descartados devem exigir compulsoriamente justificativa para auditoria do casal.
- **Regras de Negócio Vinculadas:** [BR-LOG-01 / BR-LOG-02 (Regras de Suprimentos)](domains/logistics-domain.md), [BR-L04 (Desacoplamento de Itens e Pagamentos)](business-rules/logistics/contract-state-machine.md) e [RFC-001 (Domínio de Suprimentos)](rfc/001-macro-architecture-and-domain-redesign.md).
- **Critérios de Aceitação:**
  - *Cenário 1 (Descarte com Justificativa):* Ao marcar um item como `DISCARDED`, a requisição deve falhar com validação se o campo `rejection_reason` não for fornecido.
  - *Cenário 2 (Conferência de Entrega):* O item "Doces Finos (800x)" transita para `DELIVERED` na portaria do salão independentemente do status de quitação financeira das parcelas do contrato.

---

### Módulo 5: Agenda, Cronograma e Checklist (Scheduler)

#### RF-16 — Cronograma de Eventos e Detecção de Conflitos (Soft Overlap)
- **Descrição:** O sistema deve oferecer calendário de compromissos para a assessoria, permitindo agendar reuniões, provas e cerimônias, alertando sobre sobreposição de horários (*soft overlap*) sem travar o agendamento.
- **Regras de Negócio Vinculadas:** [BR-S02 (Motor de Recorrência)](business-rules/scheduler/recurrence-rules-engine.md) e [BR-S03 (Detecção de Conflito de Agenda)](business-rules/scheduler/schedule-conflict-validation.md).
- **Critérios de Aceitação:**
  - *Cenário:* Ao salvar um evento com início às 14h e término às 16h no mesmo dia em que já existe reunião agendada das 15h às 17h, o sistema salva o registro e emite sinalizador de conflito suave no payload de resposta.

#### RF-17 — Projeção Read-Only de Eventos de Pagamento na Agenda
- **Descrição:** O sistema deve projetar automaticamente cada parcela de despesa cadastrada como um evento financeiro na agenda da assessoria, blindado contra edições manuais (*read-only guard*).
- **Regras de Negócio Vinculadas:** [BR-S01 (Proteção Somente-Leitura de Pagamentos)](business-rules/scheduler/payment-event-readonly-guard.md).
- **Critérios de Aceitação:**
  - *Cenário:* A tentativa de alterar a data ou o título de um evento de pagamento diretamente pela API da agenda é bloqueada com erro `DomainIntegrityError` (a alteração deve ser feita na parcela de origem).

#### RF-18 — Gestão de Checklist Operacional (ChecklistItem)
- **Descrição:** O sistema deve disponibilizar um checklist de pendências operacionais (`ChecklistItem`) por casamento, permitindo atribuir datas limite (`due_date`), níveis de prioridade e alternar a marcação (`is_completed`), com sincronização de barras de progresso nos painéis e nomenclatura desambiguada em relação a tarefas assíncronas do backend.
- **Regras de Negócio Vinculadas:** [RFC-001 (Renomeação ChecklistItem)](rfc/001-macro-architecture-and-domain-redesign.md).
- **Critérios de Aceitação:**
  - *Cenário:* O assessor marca a pendência "Confirmar lista final de convidados com buffet" como concluída via `/complete/`. A interface do dashboard recalcula imediatamente a métrica de progresso operacional sem recarregar a tela.

---

### Módulo 6: Dashboard & Inteligência Analítica (Dashboard)

#### RF-19 — Painel Executivo Consolidado de KPIs
- **Descrição:** O sistema deve exibir painéis de controle em 4 eixos (Financeiro, Contratos, Checklist de Tarefas e Contagem Regressiva) em nível corporativo do tenant e detalhado por casamento, utilizando projeções otimizadas para eliminar waterfalls (*Anti-Data-Stitching*).
- **Regras de Negócio Vinculadas:** [BR-D01 a BR-D04 (Regras de Agregação de Dashboard)](domains/dashboard-domain.md).
- **Critérios de Aceitação:**
  - *Cenário:* O endpoint `/dashboard/summary/` retorna em uma única consulta SQL consolidada as parcelas a vencer nos próximos 7 dias, tarefas urgentes e parcelas em atraso com latência inferior a 500 ms.

#### RF-20 — Gráficos Temporais de Fluxo de Caixa e Tarefas
- **Descrição:** O sistema deve fornecer projeções gráficas analíticas do fluxo de caixa mensal (parcelas pagas vs. pendentes ao longo do ano) e da distribuição percentual de conclusão de tarefas por evento.
- **Regras de Negócio Vinculadas:** [BR-D04 (Séries Temporais Pré-Agregadas em SQL)](domains/dashboard-domain.md).
- **Critérios de Aceitação:**
  - *Cenário:* Consulta ao gráfico de fluxo de caixa para o ano vigente retorna array ordenado de 12 meses contendo valores monetários exatos consolidados em banco de dados.

---

### Módulo 7: Relatórios Executivos Oficiais (Reporting)

#### RF-21 — Exportação de Relatório Consolidado em PDF Diagramado
- **Descrição:** O sistema deve gerar e exportar sob demanda relatórios executivos em formato PDF diagramado profissionalmente em dois passos (ReportLab), contendo resumo orçamentário, lista de contratos, cronograma de parcelas e numeração dinâmica "Página X de Y".
- **Regras de Negócio Vinculadas:** [BR-R01 (Isolamento via DTO Imutável)](domains/reporting-domain.md) e [BR-R02 (Identidade Visual PDF em Dois Passos)](domains/reporting-domain.md).
- **Critérios de Aceitação:**
  - *Cenário:* Ao requisitar `GET /reports/weddings/{uuid}/?format=pdf`, o sistema retorna binário `application/pdf` formatado com cabeçalho corporativo, dados sem vazamento cross-tenant e totalização conferida.

#### RF-22 — Exportação de Relatório Financeiro e Operacional em Planilha Excel
- **Descrição:** O sistema deve exportar pastas de trabalho em Excel (.xlsx) contendo abas segregadas para Orçamento Geral, Fornecedores & Contratos e Cronograma de Desembolso, com formatação monetária nas células.
- **Regras de Negócio Vinculadas:** [BR-R03 (Planilha Multi-Aba com Formatação Monetária)](domains/reporting-domain.md).
- **Critérios de Aceitação:**
  - *Cenário:* O download de planilha Excel abre arquivo nativo com valores monetários formatados em moeda contábil (`R$ #,##0.00`), permitindo que a assessoria envie a prestação de contas aos noivos.

---

### Módulo 8: Notificações e Rotinas Automatizadas em Background

#### RF-23 — Central de Alertas e Notificações In-App
- **Descrição:** O sistema deve registrar e exibir notificações transacionais in-app para a equipe da assessoria, com contadores de não lidas (*badges*), despacho não-bloqueante via tarefas assíncronas e histórico persistido.
- **Regras de Negócio Vinculadas:** [BR-N01 a BR-N04 (Ciclo de Vida de Notificações In-App)](business-rules/notifications/in-app-notifications-rules.md).
- **Critérios de Aceitação:**
  - *Cenário:* Ao transitar um contrato para `SIGNED`, o sistema enfileira tarefa assíncrona pós-commit que cria a notificação para os membros do tenant sem travar o tempo de resposta HTTP do assessor.

#### RF-24 — Auditoria Diária Automatizada de Parcelas Atrasadas (Cron)
- **Descrição:** O sistema deve disponibilizar endpoint interno de cron protegido por token OIDC para varredura diária no banco de dados, transitando compulsoriamente parcelas não pagas com data expirada para `OVERDUE`.
- **Regras de Negócio Vinculadas:** [BR-F05 (Máquina de Estados de Parcelas)](business-rules/finances/installment-overdue-logic.md).
- **Critérios de Aceitação:**
  - *Cenário:* Às 03h00 da madrugada, o Cloud Scheduler aciona `/internal/cron/mark-overdue/`. Todas as parcelas com `status=PENDING` e `due_date < hoje` são atualizadas para `OVERDUE` e registradas em log de auditoria.

---

## 3. Requisitos Não-Funcionais (RNF) — Critérios de Qualidade e Restrições Técnicas

- **RNF-01 — Desempenho e Eficiência da API:**
  - Rotas transacionais de leitura e escrita da API REST (Django Ninja) devem apresentar tempo de resposta $P50 < 200\text{ ms}$ e $P95 < 400\text{ ms}$. Consultas analíticas e dashboards complexos devem responder em menos de $500\text{ ms}$ utilizando consultas otimizadas sem consultas $N+1$.
- **RNF-02 — Segurança, Multi-Tenancy e Privacidade PII (LGPD):**
  - O sistema deve garantir isolamento rígido de dados no nível de linha (Row-Level Tenancy) filtrado via `TenantQuerySet.for_tenant(company)`. As senhas devem utilizar hash PBKDF2 com SHA-256 e dados sensíveis de contato devem ser protegidos contra exposição pública.
- **RNF-03 — Integridade e Confiabilidade Contábil:**
  - Todas as operações com valores monetários devem operar obrigatoriamente com o tipo `Decimal(12, 2)` do Python e colunas equivalentes no banco de dados. Mutações multi-entidade devem ser executadas compulsoriamente sob blocos transacionais `@transaction.atomic`.
- **RNF-04 — Usabilidade, Responsividade e Padrão Frontend:**
  - A interface web deve ser desenvolvida em React 19 com Tailwind CSS 4 e primitivas shadcn/ui, operando perfeitamente em telas móveis e desktop, separando rigorosamente componentes orquestradores (*Smart*) de componentes visuais puros (*Dumb*).
- **RNF-05 — Restrição de Infraestrutura e Custos (OpEx Mínimo):**
  - O sistema deve operar com arquitetura serverless em nuvem elástica (Google Cloud Run + Neon PostgreSQL Serverless + Cloudflare R2), garantindo custo operacional praticamente nulo durante ociosidade e compatibilidade com limites do nível gratuito (*Free Tier*).

---

## 4. Requisitos de Transição (RT)

- **RT-01 — Carga Inicial de Templates de Cronograma e Categorias Orçamentárias:**
  - O sistema deve dispor de comandos automáticos de inicialização de dados (*seed*) para alimentar o banco de dados com as categorias clássicas de casamento (Buffet, Espaço, Decoração, Foto & Vídeo, Som, etc.) e os 3 templates padrão de cronograma da plataforma.
- **RT-02 — Auto-provisionamento de Workspace com Dados de Demonstração:**
  - Ao registrar uma nova empresa de assessoria, o sistema deve oferecer a opção de carregar um casamento de demonstração pré-preenchido para acelerar o treinamento e a percepção de valor pelo novo assessor.
- **RT-03 — Onboarding Guiado para Assessorias Piloto:**
  - Procedimento de validação e testes operacionais com ao menos 3 empresas de assessoria cerimonial parceiras antes do lançamento público da versão 1.0.

---

## 5. Matriz de Rastreabilidade Vertical (Negócio $\to$ Requisitos da Solução)

A tabela a seguir demonstra formalmente a fundamentação de cada requisito da solução em uma necessidade legítima do mercado e das assessorias de casamento, eliminando qualquer desperdício de escopo (*gold plating*):

| Meta / Dor de Negócio (Origem: [business-vision.md](business-vision.md)) | Requisito da Solução Associado | Regra Canônica SSOT ([business-rules/](business-rules/index.md)) | Justificativa de Engenharia & Bounded Context |
| :--- | :--- | :--- | :--- |
| **Dor:** Vulnerabilidade e perda de dados cadastrais de noivos/pagadores em mensagens instantâneas. | **RF-03B** (Gestão de Clientes & Participantes) | **BR-CLI-01 a BR-CLI-03** ([clients-domain.md](domains/clients-domain.md)), [RFC-001](rfc/001-macro-architecture-and-domain-redesign.md) | Cadastro centralizado de pessoas físicas (SSOT) com validação de CPF e papéis de evento via `WeddingClient`. Bounded Contexts: `clients` e `weddings`. |
| **Dor:** Falta de suporte a alinhamentos preliminares e simulação orçamentária pré-contratual. | **RF-04** (Ciclo de Vida & Contrato da Assessoria) | **BR-W02, BR-W05** ([wedding-status-lifecycle.md](business-rules/weddings/wedding-status-lifecycle.md)), [RFC-001](rfc/001-macro-architecture-and-domain-redesign.md) | Fase preliminar `PROPOSTA`, formalização com contrato de assessoria (`Contract` tipo `PLANNER`) e conversão para `PLANEJAMENTO` com baseline congelada. Bounded Context: `weddings`. |
| **Dor:** Furos de centavos em planilhas que geram desconfiança e prejuízo nos orçamentos. | **RF-09, RF-10** (Parcelamento & Tolerância Zero) | **BR-F01** ([financial-integrity-rules.md](business-rules/finances/financial-integrity-rules.md)) | Cálculo matemático determinístico que aloca dízimas na última cota via `Decimal(12,2)`. Bounded Context: `finances`. |
| **Dor:** Falha cadastral e homologação de prestadores sem idoneidade fiscal. | **RF-12** (Catálogo de Fornecedores & CNPJ Módulo 11) | **BR-SUP-01, BR-SUP-02** ([suppliers-domain.md](domains/suppliers-domain.md)), [BR-L05](business-rules/logistics/cnpj-validation-rules.md) | Catálogo compartilhado com cálculo algorítmico Módulo 11 dos dígitos verificadores. Bounded Context: `suppliers`. |
| **Dor:** Falta de formalização de aditivos gerando litígios e disputas financeiras no pós-evento. | **RF-13** (Contratos & Entidade Dedicada de Aditivos) | **BR-CON-01, BR-CON-02** ([contracts-domain.md](domains/contracts-domain.md)), [BR-L01, BR-L02](business-rules/logistics/contract-state-machine.md) | Máquina de estados finita e entidade filha `ContractAddendum` (1:N) com recálculo agregado. Bounded Context: `contracts`. |
| **Dor:** Esquecimento ou descontrole no escopo e entrega de materiais no dia da celebração. | **RF-15** (Suprimentos Multidimensionais SupplyItem) | **BR-LOG-01, BR-LOG-02** ([logistics-domain.md](domains/logistics-domain.md)), [BR-L04](business-rules/logistics/contract-state-machine.md) | Gestão em 3 dimensões (escopo com justificativa de descarte, cotação e conferência de entrega). Bounded Context: `logistics`. |
| **Dor:** Sobrecarga na preparação manual de dados para reuniões executivas com os noivos. | **RF-19, RF-21, RF-22** (Dashboards, PDF e Excel) | **BR-D01 a BR-D04, BR-R01 a BR-R04** ([dashboard-domain.md](domains/dashboard-domain.md), [reporting-domain.md](domains/reporting-domain.md)) | Geração em 1 clique de PDFs diagramados (ReportLab) e Excel multi-aba alimentados por DTOs imutáveis. Bounded Contexts: `dashboard` e `reporting`. |
| **Dor:** Perda de documentos físicos e minutas contratuais de dezenas de fornecedores. | **RF-14** (Upload R2 Presigned URLs) | **BR-C04** ([core-domain.md](domains/core-domain.md)), [BR-CON-03](domains/contracts-domain.md), [ADR-004](adr/004-presigned-urls.md) | Armazenamento de minutas no Cloudflare R2 com URLs pré-assinadas e zero custo de egresso. Bounded Context: `contracts`. |
| **Meta:** Prevenção de conflito de horários de compromissos no cronograma da assessoria. | **RF-16, RF-18** (Agenda, Soft Overlap & ChecklistItems) | **BR-S03** ([schedule-conflict-validation.md](business-rules/scheduler/schedule-conflict-validation.md)), [RFC-001](rfc/001-macro-architecture-and-domain-redesign.md) | Algoritmo de *Soft Overlap* e checklist desambiguado de tarefas assíncronas. Bounded Context: `scheduler`. |
| **Meta:** Garantia de segurança e sigilo comercial entre empresas concorrentes. | **RF-01, RF-02** (Isolamento Multi-Tenant) | **BR-T01, BR-T04** ([tenants-domain.md](domains/tenants-domain.md)) | Filtro obrigatório de tenant em nível de queryset (`for_tenant`), blindando dados por empresa. Bounded Context: `tenants`. |
| **Restrição OpEx:** Custo de infraestrutura mínimo compatível com modelo de baixo orçamento. | **RNF-05** (Infraestrutura Serverless) | [ADR-001](adr/001-why-cloud-run.md), [ADR-002](adr/002-why-neon.md), [ADR-003](adr/003-why-r2.md) | Arquitetura serverless com Google Cloud Run, Neon DB e Cloudflare R2 com escala a zero. |

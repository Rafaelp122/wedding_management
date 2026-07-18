# Relatório de Análise de Testabilidade do Frontend (Feature: Weddings)

Nesta análise, focamos nos componentes da funcionalidade de `weddings` que apresentam oportunidades de melhoria para facilitar a criação de testes (tanto unitários quanto de integração).

## Componentes Analisados

### 1. `WeddingsTable.tsx` (279 linhas)
**Problemas Identificados:**
- **Acoplamento com Estado Global e React Query:** O componente faz uso direto do `useQueryClient` do `@tanstack/react-query` para invalidar queries quando um casamento é excluído ou editado, dependendo fortemente do contexto da aplicação.
- **Lógica Mista:** O componente renderiza a UI da tabela de casamentos (Presentational) *e* gerencia o estado de modais (`editingWedding`, `deletingWedding`), além de aplicar a lógica de formatação complexa dentro do próprio JSX.
- **Desafio de Teste:** Testar a tabela exige *mockar* `react-router-dom` (navegação), `@tanstack/react-query` (queryClient), modais de edição e de exclusão, tudo ao mesmo tempo.

**Recomendações:**
- Separar o `WeddingsTable` num componente puramente de apresentação (Dumb Component), cujas responsabilidades seriam:
  - Receber `weddings`, `onEditClick(wedding)`, `onDeleteClick(wedding)` e `onViewDetails(wedding)` como props.
- O componente *Pai* (`WeddingsListPage`) gerenciará o estado dos modais e a invalidação do React Query após ações bem-sucedidas. Assim, testar a lógica de apresentação não exigirá *mocks* pesados de dependências de estado da API.

### 2. `WeddingDetailPage.tsx` (250 linhas)
**Problemas Identificados:**
- **Acoplamento de Requisições:** Realiza múltiplas chamadas (`useWeddingDetail`, `useWeddingsOverviewRead`) e o hook direto do Query Client no mesmo arquivo que renderiza a UI principal da página.
- **Cálculos de UI Embutidos:** O código usa `useMemo` para formatação de data e `checklistPercentage`, e possui uma função interna `formatBudget`.
- **Desafio de Teste:** O arquivo exige configuração de Mocks do TanStack Query para os *endpoints* da API. É difícil testar isoladamente as regras de cálculo sem renderizar a árvore toda, que é grande.

**Recomendações:**
- Extrair as lógicas de formatação (ex: `formatBudget`) para funções de utilidade pura em um arquivo `utils/formatters.ts` que pode ser facilmente testado unitariamente sem dependência de React.
- Mover a chamada de requisição de dados (`useWeddingDetail`, `useWeddingsOverviewRead`) para um hook customizado `useWeddingPageData(uuid)` e retornar os estados. Isso permite testar a lógica de estado/hook de forma independente da UI através do `renderHook`.
- Dividir a UI da "Card de Perfil Compacto" em um sub-componente isolado, facilitando os testes da exibição das métricas vitais.

### 3. `WeddingOverview.tsx` (248 linhas)
**Problemas Identificados:**
- **Condicionais e Listas Diretas:** Componente denso que recebe o objeto gigante e mapeia as seções (métricas em blocos e duas colunas de ações urgentes e vencimentos próximos) no mesmo escopo.
- **Cálculos diretos:** Cálculos de `contracts_signed / contracts_total` e acesso profundo a dados como `urgentTasks` são feitos junto com a renderização.
- **Desafio de Teste:** Um teste que queira apenas validar a lista de próximos vencimentos será obrigado a renderizar os cards de contagem regressiva e outras integrações.

**Recomendações:**
- Extrair sub-componentes independentes (ex: `WeddingCountdownCard`, `WeddingTasksCard`, `WeddingUpcomingInstallmentsCard`). Dessa maneira, você poderá escrever testes direcionados ("O componente `WeddingTasksCard` renderiza estado de fallback quando não há urgências") com mais clareza, diminuindo o *overhead* de Mock dos objetos complexos.

## Conclusão Geral para Facilitar os Testes
Para maximizar a facilidade de criação de testes nos componentes:
1. Adotar o padrão **Container/Presentational Component**.
2. **Extrair cálculos e formatação** para funções puras.
3. **Desacoplar requisições e ações complexas** do componente que pinta a tela passando por `props` simples.

## Feature: Scheduler (Agenda e Tarefas)

A funcionalidade de Scheduler lida intensamente com renderização de calendário, tabelas e modais de criação/edição. Os seguintes componentes apresentam alta complexidade e dificultam os testes:

### 1. `EditEventDialog.tsx` (369 linhas) e `CreateEventDialog.tsx` (333 linhas)
**Problemas Identificados:**
- **Acoplamento Extremo de Responsabilidades:** Ambos os componentes não são apenas "Diálogos", eles também instanciam os hooks de formulário do React Hook Form (`useForm` com `zodResolver`), configuram a query de submissão (mutations do `@tanstack/react-query`) e ainda renderizam toda a UI do formulário (com mais de uma dezena de tags `<FormField>`).
- **Lógica de Conversão no JSX:** Utiliza funções como `toDateTimeLocalValue` e parseamento do DOM (ex: `e.target.value === "" ? 60 : Number(...)`) espalhados pelo JSX.
- **Desafio de Teste:** Para testar que a validação de data final menor que inicial funciona (regra do Zod), hoje é preciso montar todo o diálogo, preencher os inputs via user-events, clicar em salvar e analisar se a mensagem de erro do DOM foi renderizada, o que é um teste lento (E2E na camada de unidade).

**Recomendações:**
- Separar o "Formulário" (regras de Zod, Hook Form) do "Modal" (o Dialog que apenas envolve o formulário).
- Transformar `CreateEventForm` e `EditEventForm` em componentes que recebam a função `onSubmit` via prop e não chamem mutações da API diretamente. Isso permite testes unitários diretos na função onSubmit com Mocks, sem precisar testar a mutação da API em conjunto com a UI.
- Extrair o esquema do Zod (`formSchema` com `.superRefine`) e os *resolvers* para um arquivo à parte `zod/events.schema.ts`, possibilitando que o modelo seja testado independentemente do componente React usando asserções Zod diretamente.

### 2. `SchedulerPage.tsx` (289 linhas)
**Problemas Identificados:**
- **Inchaço de Estado:** O componente gere o estado de abas (`viewMode`), estado de "abrir/fechar" os *vários* diálogos de criação e edição (`createDialogOpen`, `editDialogOpen`), além de controlar o estado local dos eventos selecionados (`selectedEvent`, `createDefaultStart`).
- **Fetchings Consolidados:** Carrega `useSchedulerEventsList` e `useWeddingsList` e processa ordenação (`sortedEvents`) e cruzamentos (`weddingsByUuid`) tudo no mesmo arquivo antes de repassar para os componentes filhos.
- **Desafio de Teste:** O arquivo exige que sejam feitos mocks de ambas as APIs, configurações de página e instâncias de Query Client, transformando um simples teste de mudança de Tab num teste de alta complexidade (Heavy Mount).

**Recomendações:**
- Extrair o "Gerenciamento de Modais" para um Hook Customizado genérico (ex: `useDialogState()`) ou aplicar a inversão de controle passando essa responsabilidade para os filhos (ex: a tabela dispara um evento que uma "store" ou "provider" reage, ao invés do próprio page gerenciar N modais invisíveis na raiz).
- Isolar a lógica complexa de derivação de estado (`useMemo` de `weddingsByUuid` e `sortedEvents`) para um Custom Hook chamado `useSchedulerPageData`, deixando o componente da página unicamente responsável pelo esqueleto do layout e exibição dos estados de Loading/Error/Success.

### Padrão Geral Recomendado (Aplicável a todo o projeto)
A raiz da complexidade de testes no frontend do WMS atualmente é a violação do Princípio da Responsabilidade Única nos componentes. A refatoração ideal deve focar em:
1. **Modelos Zod testados isoladamente** (remover `.superRefine` de dentro do arquivo `.tsx`).
2. **Presentational Forms** (`MeuForm.tsx` recebe `defaultValues` e a função `onSubmit` via Props, sem chamar Hook de Mutation do React Query).
3. **Containers de Formulário** (`MeuFormDialog.tsx` ou "Smart Components" que renderizam o `MeuForm` e chamam a Mutation). Isso facilita uma cobertura abrangente no formulário sem usar Mocks de rede/query.

## Feature: Logistics (Contratos, Fornecedores e Itens)

A feature de logística lida com entidades que possuem múltiplos relacionamentos (Um Contrato pertence a um Fornecedor, possui Itens e pode gerar Despesas). A UI reflete essa complexidade.

### 1. `ContractUploadDialog.tsx` (336 linhas)
**Problemas Identificados:**
- **Múltiplos Formulários em um só estado:** O componente lida com o formulário principal (Zod de `LogisticsContractsCreateBody`), estado de rascunhos de itens (`itemDrafts`), estado de formulário financeiro embutido (`expenseChecked`, `expenseCategory`, `expenseNumInstallments`) e com o `File` (upload de anexo).
- **Submissão "Fat":** A função `onSubmit` possui quase 50 linhas de código estruturado imperativamente: solicita URL de upload na API -> faz o fetch do S3 -> constrói o payload do contrato -> mapeia drafts de itens -> mapeia despesas -> dispara `createFull`.
- **Desafio de Teste:** É o caso mais extremo de dificuldade de teste no frontend. Para testar o "caminho feliz", o desenvolvedor precisa *mockar* a API de contratos, a API de S3 (upload do blob do arquivo) e *mockar* interações pesadas de usuário (incluindo checkbox dinâmico).

**Recomendações:**
- Extrair a lógica pesada do `onSubmit` para um **Custom Hook de Mutação de Negócio** (`useCreateContractWithUpload`). Isso permite testar a lógica do upload assíncrono encadeado com a criação usando apenas Node/Vitest, sem depender da árvore do DOM.
- Dividir a View do Dialog em passos (Wizard) ou extrair sub-formulários. Componentizar os blocos `ContractCreateExpenseFields` e `ContractItemDrafts` como subcomponentes que gerenciam seu próprio pedaço do formulário usando a função `useFormContext` (React Hook Form).

### 2. `ContractDetailDialog.tsx` (302 linhas)
**Problemas Identificados:**
- **Acúmulo de Endpoints:** O modal busca o contrato (`useLogisticsContractsRead`), os itens (`useLogisticsItemsList`) e os aditivos (`useLogisticsContractsList` passando `parent_id`).
- **Gerenciamento de Navegação Embutida:** Recebe *callbacks* profundos (`onExpenseClick`, `onSupplierClick`, `onCreateAddendum`) para delegar navegação.

**Recomendações:**
- Este componente é um bom candidato ao padrão *Container/Presentational*.
- `ContractDetailContainer`: Chama as Queries, trata os loadings e delega a injeção dos callbacks.
- `ContractDetailDialog`: O Dumb Component que recebe `contract`, `items`, `addendums` e renderiza a UI puramente com base nas *props*. Muito mais fácil de injetar os dados falsos e verificar se os `badges` e detalhes renderizam corretamente usando o React Testing Library.

### 3. `VendorsItemsView.tsx` (200 linhas)
**Problemas Identificados:**
- **Controlador de Modais:** A "View" gerencia a abertura, o fechamento e a injeção de estado de múltiplos diálogos distintos (`uploadOpen`, `detailContractUuid`, `createItemOpen`, `editItem`). Isso infla o componente que deveria ser apenas um Layout Agregador.

**Recomendações:**
- Adotar o padrão de "Slot Providers" ou roteamento por *Query Params*. Em vez do componente raiz guardar booleanos infinitos (`isEditModalOpen`), alterar a URL para `?action=edit-item&id=123`. Um componente superior "DialogRouter" intercepta e abre os modais correspondentes. Isso limpa a View e permite testar modais diretamente forçando o estado inicial via URL/MemRouter nos testes.

## Feature: Dashboard (Agregador Global)

A feature de Dashboard atua como o painel central, reunindo requisições de praticamente todos os domínios do sistema (Casamentos, Finanças, Logística e Tarefas).

### 1. `DashboardPage.tsx` (309 linhas)
**Problemas Identificados:**
- **Excesso de Fetchings e Dependências:** Num único arquivo o componente utiliza `useWeddingsList`, `useWeddingsLookup`, `useWeddingsRead`, `useDashboardSummary` e `useDashboardWedding`. Múltiplos desses *hooks* usam lógicas condicionais de `enabled` dependendo do estado global `selectedWeddingUuid`.
- **Desafio de Teste:** O arquivo exige *mocking* massivo para renderizar com sucesso. Para escrever um teste que garanta a renderização da mensagem de saudação correta, é preciso mockar 5 rotas de API, o Hook do Zustand (`useAuthStore`) e injeções de layout.

**Recomendações:**
- Delegar as chamadas de API aos próprios componentes filhos quando possível, em vez da raiz da página baixar tudo e fazer "Prop Drilling".
- Caso a otimização exija chamadas na raiz (para evitar *Waterfalls*), extrair as lógicas agregadoras para um custom hook `useDashboardData()` que retorna os estados unificados (`isLoading`, `error`, `dados_para_telas`), permitindo testar as lógicas condicionais de `enabled` usando o `renderHook`.

### 2. `WeddingMonthlyChart.tsx` (352 linhas) e `DashboardOperations.tsx` (357 linhas)
**Problemas Identificados:**
- **Quebra do padrão de Componente Burro (Dumb Component):** Estes componentes deveriam ser puramente visuais, recebendo listas de tarefas ou finanças para apenas desenhar os gráficos e abas. No entanto, eles instanciam seus próprios *Hooks* do *React Query* internamente (`useFinancesInstallmentsList` e `useSchedulerTasksList`), com buscas disparadas *lazy* via condição das *Tabs* ativas.
- Em `DashboardOperations.tsx`, não há apenas a visualização, mas a implementação de Mutations de atualização de tarefas e invalidação pesada de Queries globais.

**Recomendações:**
- Para `WeddingMonthlyChart.tsx`: Deve ser quebrado em *Wrapper/Container* e *View*. O arquivo do gráfico real (ex: `RechartsLineChart`) não pode conhecer a biblioteca TanStack Query. Isso facilita o teste de renderização do Gráfico.
- Para `DashboardOperations.tsx`: Extrair a `List` renderizada nas abas para subcomponentes que gerenciam a sua própria parte da query (`TasksListTab`, `ContractsListTab`), removendo a montanha de variáveis acumuladas no topo do arquivo.

## Feature: Finances (Despesas e Orçamento)



A funcionalidade de Finanças é o coração matemático do projeto. Como esperado, o acoplamento afeta muito a testabilidade de tabelas e fluxos de despesa.



### 1. `ExpenseDetailSheet.tsx` (220 linhas)

**Problemas Identificados:**

- **Lógica de Status Embutida:** Regras de negócio de "progresso de pagamento" (`progress = (totalPaid / actualAmount) * 100`) estão atreladas ao componente de visualização.

- **Mutations Mistas:** O `Sheet` chama mutations de "Marcar Parcela como Paga" e "Desmarcar" (`togglePayment`), invalidando as queries relacionadas e lidando com Loading individual de botões.



**Recomendações:**

- Extrair os cálculos de Progresso e Sumarização para um `utils/finances.ts` puro para que sejam 100% cobertos por Testes Unitários simples.

- Isolar a responsabilidade de "Pagar Parcela" da "Visualização de Detalhes da Despesa", talvez com a `ExpenseInstallmentRow` virando seu próprio Smart Component responsável pela Mutação.



### 2. `ExpensesTable.tsx` (211 linhas)

**Problemas Identificados:**

- **Root State Hogs:** Semelhante a `VendorsItemsView`, a tabela de despesas tenta ser o pai de todos os modais da funcionalidade (`editingExpense`, `deletingExpense`, `detailExpense`), tornando um simples teste de layout num monstro de renderização dependente do Suspense/Lazy.



**Recomendações:**

- Extrair ações para um menu que envia Eventos e um Componente "gestor de modais" acima dele, ou tratar as edições em uma aba lateral ligada a rotas.
## Conclusão Final do Padrão
Em todo o Frontend, os maiores arquivos enfrentam o mesmo desafio: **misturar lógica de UI densa com lógicas pesadas de Fetch/Mutations do TanStack Query**.

### Plano Diretor para Refatoração e Testes (Guia Rápido)
1. **Forms**: Isolar Schemas Zod em arquivos `.schema.ts` e tratar o Formulário como *Presentational* que apenas exibe inputs e invoca `onSubmit(data)`. O Hook que chama a API deve envolver este componente.
2. **Modais Complexos (Wizard/Multi-passo)**: Para fluxos como o *Upload de Contratos com Despesas*, isolar as dezenas de linhas imperativas assíncronas do Submit num *Custom Hook* de negócio.
3. **Páginas Agregadoras (Dashboards/Visões)**: Adotar um forte padrão *Container/Presentational Component*, onde os cálculos gigantes de `useMemo` viram Hooks locais, que preparam propriedades para serem entregues prontas para visualização, simplificando radicalmente os Mocks durante os testes unitários.

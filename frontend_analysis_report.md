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
- **Desafio de Teste:** Um teste que queira apenas validar a lista de parcelas não pagas será obrigado a renderizar os cards de contagem regressiva e outras integrações.

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
- **Acoplamento Extremo de Responsabilidades:** Ambos os componentes não são apenas "Diálogos", eles também estanciam os hooks de formulário do React Hook Form (`useForm` com `zodResolver`), configuram a query de submissão (mutations do `@tanstack/react-query`) e ainda renderizam toda a UI do formulário (com mais de uma dezena de tags `<FormField>`).
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
3. **Containers de Formulário** (`MeuFormDialog.tsx` ou "Smart Components" que renderizam o `MeuForm` e chamam a Mutation). Isso permite 100% de cobertura no formulário sem usar Mocks de rede/query.

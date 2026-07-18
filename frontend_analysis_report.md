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

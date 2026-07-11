# ADR-022: Uso de Rotas Estáticas para Páginas do Fluxo Principal (SPA)

## Status
Aprovado

## Contexto
Anteriormente, o projeto seguia a convenção de carregar todas as páginas e abas sob demanda utilizando `React.lazy()` e `Suspense` em todas as rotas do frontend. A intenção original era manter o tamanho do bundle principal pequeno para acelerar o primeiro carregamento da aplicação.

Contudo, testes em ambiente de produção (Vercel + Google Cloud Run + Neon DB) demonstraram um gargalo significativo:
1. **Latência de TTFB:** Cada navegação exigia o download de um novo chunk JavaScript do servidor. Em conexões normais ou redes móveis, o tempo de resposta do servidor estático da Vercel adicionava centenas de milissegundos.
2. **Spinner Bloqueante:** A tag `<Suspense>` desmontava imediatamente o layout da página anterior, gerando um "flash" de tela branca com um spinner centralizado. Isso quebrava a experiência fluida de um Single Page Application (SPA), assemelhando-se a um recarregamento completo clássico.
3. **Cascatas de Download:** Algumas páginas carregavam dinamicamente sub-chunks, atrasando ainda mais o primeiro carregamento da tela.

Dado que o bundle total da aplicação é pequeno (menos de 2MB não compactado), o custo de baixar um único arquivo JS principal no primeiro acesso é desprezível e amortizado pelo cache agressivo do navegador.

## Decisão
Decidimos alterar a convenção de roteamento do projeto:
1. **Imports Estáticos para Rotas e Abas Principais:** As páginas centrais da experiência do usuário (`DashboardPage`, `WeddingsListPage`, `WeddingDetailPage`, `SchedulerPage`, `SuppliersPage`, `LoginPage` e `RegisterPage`), bem como as abas de detalhes do casamento (`WeddingOverview`, `WeddingFinancesView`, `WeddingVendorsItemsTab`, `WeddingTimelineTab`, `WeddingChecklistTab`), passam a ser importadas de forma **estática** (síncrona).
2. **Lazy Loading Reservado para Páginas Secundárias:** O uso de `React.lazy` fica restrito a componentes pesados de terceiros (ex: geradores de PDF) ou rotas raramente acessadas (ex: `ComingSoonPage`, `NotFoundPage`, telas de configurações administrativas).
3. **Substituição de Loaders Globais por Skeletons Inline:** Em vez de bloquear toda a tela com spinners ou layouts skeleton de página inteira (`if (isLoading) return <FullPageSkeleton>`), as páginas devem renderizar seus layouts estáticos imediatamente, exibindo `<Skeleton>` apenas nas áreas de dados dinâmicos enquanto as queries do React Query carregam em segundo plano.

## Consequências
* **Positivas:**
  * Navegação entre páginas do fluxo de trabalho é instantânea (0ms de atraso de chunk).
  * O visual do SPA é fluido, pois o menu de navegação e o cabeçalho nunca somem ou piscam.
  * O F5 se beneficia do cache do navegador, carregando o bundle principal instantaneamente.
* **Negativas:**
  * O tamanho do bundle principal inicial aumenta ligeiramente (cerca de 50KB a 100KB gzipped), o que é irrelevante para a experiência geral do usuário em redes modernas.

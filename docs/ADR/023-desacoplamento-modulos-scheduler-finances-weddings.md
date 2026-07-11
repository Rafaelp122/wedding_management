# ADR-023: Desacoplamento dos Módulos Core (Weddings, Scheduler e Finances)

## Status
Proposto

## Contexto
Durante a refatoração do fluxo de detalhes de casamento, identificamos fortes acoplamentos bidirecionais (dependências circulares) no nível de serviços e modelos entre os principais aplicativos da nossa arquitetura backend: `weddings`, `scheduler` e `finances`.

Atualmente, as seguintes dependências circulares existem no sistema:
1. **`weddings` ↔ `scheduler`**: O `scheduler` depende de `weddings` por meio do modelo `Event` (que possui chave estrangeira para `Wedding`). Em contrapartida, o `WeddingService` importa diretamente o `EventService` para criar eventos do cronograma inicial com base no modelo de cronograma selecionado pelo usuário.
2. **`finances` ↔ `scheduler`**: O `scheduler` depende de `finances` através do vínculo de parcelas (`source_installment`). Contudo, o `InstallmentService` (dentro de `finances`) importa `EventService` diretamente para gerenciar a criação/exclusão síncrona de lembretes no calendário de pagamentos.
3. **`weddings` ↔ `finances`**: Modelos financeiros como `Budget` e `Installment` pertencem a um `Wedding`. Por outro lado, as estatísticas de orçamento exibidas pelo `DashboardService` do app `weddings` são calculadas realizando consultas diretas aos modelos de dados internos de `finances`.

Essas dependências bidirecionais forçam o uso de importações tardias (inline imports no Python) dentro de métodos para evitar erros de importação cíclica e vazamento de limites de domínio. Isso prejudica a manutenibilidade, isolamento de testes unitários e qualquer futura modularização do sistema.

## Proposta de Decisão
Propomos as seguintes abordagens para o desacoplamento de domínio a serem implementadas em uma sprint dedicada à refatoração de arquitetura:

1. **Uso de Eventos de Domínio (Django Signals):**
   * Em vez de o `WeddingService` ou o `InstallmentService` chamarem diretamente o `EventService` para criar eventos no calendário, esses serviços passarão a disparar eventos de domínio (ex: sinais `post_save` do Django ou um barramento simples de eventos internos).
   * O módulo `scheduler` registrará escutadores (listeners) para reagir a esses eventos e criar/excluir eventos de calendário de forma assíncrona ou independente. Isso inverte e limpa o fluxo de dependência.

2. **Criação de uma Camada de Casos de Uso (Application Services / Use Cases):**
   * Operações cross-domínio complexas (como criar um casamento e inicializar seu cronograma correspondente) deixarão de viver dentro das classes de serviço de domínio. Elas serão movidas para classes de caso de uso de alto nível.
   * Exemplo: Um `CreateWeddingUseCase` orquestrará a chamada síncrona de `WeddingService.create(...)` e, em seguida, a inicialização em `SchedulerService.apply_template(...)`, sem que um domínio dependa ou conheça as regras internas do outro.

3. **Abstração de Leituras de Relatório (Read Models / DTOs):**
   * O dashboard de casamentos deixará de consultar os modelos de dados internos de `finances` diretamente. Criaremos interfaces de leitura ou DTOs específicos para expor dados consolidados, isolando as tabelas e modelos relacionais internos de cada módulo.

## Consequências
* **Positivas:**
  * Remoção completa de dependências circulares e de imports em escopo local (`import ... inside function`).
  * Facilidade de escrever testes isolados (unitários) para cada domínio sem necessidade de mockar ou instanciar objetos de múltiplos bancos de dados.
  * O código do core (`weddings`) e do faturamento (`finances`) fica 100% independente do canal de notificação/calendário (`scheduler`).
* **Negativas:**
  * Pequeno aumento no nível de indireção do código devido à introdução de sinais/eventos ou classes de casos de uso.

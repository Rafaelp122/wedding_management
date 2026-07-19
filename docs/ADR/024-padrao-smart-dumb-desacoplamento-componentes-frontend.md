# ADR-024: Padrão Smart/Dumb para Desacoplamento de Componentes e Testabilidade no Frontend

**Status:** Proposto
**Data:** Julho 2026
**Decisor:** Time de Frontend

---

## Contexto e Problema

No desenvolvimento do frontend (React, TypeScript, Vite, TanStack Query), identificou-se que componentes de UI acumulavam múltiplas responsabilidades de forma acoplada:
1. Realização direta de queries e mutações de rede (via hooks Orval/TanStack Query).
2. Gerenciamento interno de estado de formulários e schemas de validação Zod (via react-hook-form).
3. Leitura e controle de navegação de rotas (via React Router).
4. Cálculos complexos de agregação matemática e manipulação de datas para gráficos e status visuais.

Esse alto nível de acoplamento impedia a criação de testes unitários rápidos e independentes. Para testar qualquer elemento de UI, era necessário simular múltiplos provedores de contexto (QueryClientProvider, FormProvider, BrowserRouter, etc.) e lidar com o assincronismo do carregamento de dados da API. Isso gerava testes frágeis, difíceis de satisfazer no TypeScript, e com alta redundância de mocks globais.

Sob o ambiente de testes concorrido e sem isolamento do Vitest (`isolate: false`), essa poluição de mocks individuais em arquivos de teste frequentemente causava colisões e inconsistências na execução concorrente.

---

## Decisão

Adotaremos formalmente o padrão **Smart/Dumb Components** (também conhecido como *Container/Presenter*) e o isolamento de lógica pura para todo o frontend do projeto.

### 1. Smart Components (Containers ou Orchestrators)
Componentes de nível de página ou wrappers que gerenciam a infraestrutura assíncrona e lógica de roteamento.
* **Responsabilidades**: Chamar hooks de API (mutações, queries), ler parâmetros de rota, inicializar formulários e schemas de validação.
* **Ação**: Devem envelopar os componentes visuais correspondentes e passar a eles apenas dados processados e callbacks simples via Props.

### 2. Dumb Components (Presenters ou Views)
Componentes puramente visuais e focados na renderização da interface.
* **Responsabilidades**: Exibir a UI com base em Props e disparar callbacks de evento passados pelo container (ex: `onSuccess`, `onEdit`, `onSubmit`).
* **Regra Estrita**: Não podem conter dependências diretas de chamadas de API, roteamento ou hooks globais de dados assíncronos. Eles são síncronos e puros. Como exceção permitida, podem importar tipos gerados da API (`import type { ... }`) para garantir a integridade da tipagem estrita no TypeScript.
* **Benefício**: São testados unitariamente de forma instantânea sem necessidade de wrappers complexos (como `QueryClientProvider` ou `BrowserRouter`).

### 3. Funções Utilitárias Puras (Helpers)
Cálculos e lógica de negócio de formatação de dados, gráficos e regras de status.
* **Regra Estrita**: Devem ser extraídos para arquivos utilitários independentes (`utils/` ou `helpers.ts`) e parametrizados de forma determinística (ex: aceitando datas de referência como argumento em vez de chamarem `new Date()` interno).
* **Benefício**: Cobertura de testes abrangente com testes de função puros e sem peso de renderização do DOM.

### 4. Resolução de Import e Mocking sob `isolate: false`
* Evita-se o uso de `vi.mock` local em arquivos de teste para hooks customizados.
* Para evitar colisão de instâncias no cache do bundler (Vite), os caminhos de importação nos testes de mock (`.test.tsx`) devem combinar exatamente com o estilo de importação do componente real (ex: relative imports `../hooks` vs absolute paths `@/`).

---

## Consequências

### Positivas
* **Alta Testabilidade**: Facilidade extrema de escrever testes unitários síncronos e independentes para a camada de apresentação.
* **Componentes Reutilizáveis**: Componentes Dumb tornam-se altamente portáveis e reutilizáveis em outras partes do sistema.
* **Desempenho nos Testes**: Execução extremamente rápida da suíte de testes concorrentes do Vitest, sem processos pesados de mock de rede individuais.
* **Clareza de Responsabilidades**: Separação clara entre a lógica de negócios/rede e a lógica visual de renderização.

### Negativas
* **Multiplicação de Arquivos**: O padrão exige a criação de mais arquivos por feature (ex: `MyPage.tsx`, `MyPageView.tsx`, `useMyPageForm.ts`), o que requer uma disciplina de nomenclatura constante.

# ADR-016: Arquitetura de Eventos Genéricos e Tenancy por Empresa (B2B)

**Status:** Proposto
**Data:** Abril 2026
**Decisor:** Rafael
**Contexto:** Evolução do sistema de um gerenciador de casamentos solo para uma plataforma SaaS de gestão de agências de eventos, visando escalabilidade e flexibilidade de domínio.

---

## Contexto e Problema

O sistema atual foi modelado com foco exclusivo em **Casamentos** (`Wedding`) e o isolamento de dados (multitenancy) é baseado no **Usuário/Planner** individual.

### Limitações Técnicas e de Negócio:
1.  **Rigidez de Domínio:** Cerimonialistas frequentemente gerenciam outros tipos de celebrações (15 anos, formaturas, corporativos). O modelo `Wedding` com campos fixos (`bride_name`, `groom_name`) impede o reaproveitamento da lógica financeira e logística para outros contextos.
2.  **Dificuldade de Colaboração:** O multitenancy por `User` cria um silo de dados. Em agências de eventos, múltiplos funcionários precisam colaborar nos mesmos projetos. Mudar essa estrutura com dados em produção é uma operação de alto risco e custo.
3.  **Conflito Semântico:** O modelo `scheduler.Event` (atualmente representando compromissos de calendário) conflita com o termo de domínio de alto nível que representa o projeto/contrato.

---

## Decisão

Reestruturar o núcleo do sistema para adotar uma hierarquia de Tenancy por Organização, uma modelagem de eventos polimórfica e uma camada de serviços especializada por tipo de evento.

### 1. Novo Modelo de Tenancy: `Company`
- Introdução da entidade `Company` como o Tenant Primário e isolador de dados.
- Usuários (`User`) serão vinculados a uma `Company`.
- Substituição do `PlannerOwnedMixin` pelo `CompanyOwnedMixin`.
- Dados globais da agência (como base de fornecedores) serão isolados por `Company`.

### 2. Generalização de Eventos: `Event` + `Details`
- A entidade central de negócio passará a ser o `Event`, contendo apenas dados comuns a qualquer celebração (Nome, Data, Local, Status, Tipo).
- Atributos específicos de nicho serão movidos para modelos de detalhamento (ex: `WeddingDetail`) vinculados via `OneToOneField` ao `Event`.
- O isolamento operacional (Financeiro, Logística) usará o `EventOwnedMixin`.

### 3. Orquestração via Strategy Pattern e Controllers Especializados
Adotaremos uma estrutura de serviços e controladores baseada em delegação para separar a lógica genérica da específica:
- **`EventService` (Orquestrador)**: Gerencia o ciclo de vida base e delega ações específicas para `Handlers` especializados (ex: `WeddingHandler`). Isso evita a fragilidade da herança de métodos estáticos.
- **Controllers por Especialidade**:
  - `EventController` (`/events/`): Retorna apenas a base genérica (`EventOut`) para dashboards e calendários.
  - `WeddingController` (`/events/weddings/`): Retorna o domínio completo (`WeddingOut`) para gestão rica.
- **Benefício**: APIs genéricas permanecem rápidas e fáceis de tipar no frontend, enquanto APIs específicas garantem a integridade dos detalhes de nicho.

### 4. Resolução de Conflitos no Scheduler
- O modelo `scheduler.Event` (compromissos de calendário/agenda) será renomeado para `scheduler.Appointment`.

### 5. Tenant Silencioso no MVP
- No registro do usuário, uma `Company` será criada automaticamente de forma transparente.
- O usuário não interage diretamente com a entidade `Company` no MVP.
- Esta abordagem permite a migração futura para múltiplos usuários por empresa (colaboração) sem a necessidade de alteração de schema ou migrações de dados complexas em produção.

---

## Justificativa

### Por que Company em vez de User?
O valor de negócio está na capacidade de expansão para agências. Mesmo que o MVP comece com usuários solo, o isolamento por empresa garante que o sistema suporte o crescimento orgânico do cliente (contratação de assistentes) sem quebras estruturais.

### Por que OneToOne para Detalhes e Serviços Especializados?
Esta abordagem evita os problemas de performance da Herança de Tabela Múltipla (MTI) do Django e organiza a lógica de negócio de forma que o sistema possa crescer para novos nichos (ex: aniversários) apenas adicionando um novo par `ModelDetail` + `Service`, sem tocar no código core de finanças ou logística.

### Por que simplificar o Client no MVP?
Manteremos os dados dos clientes dentro de `WeddingDetail` ou campos de texto no `Event` por enquanto para evitar a complexidade de múltiplos vínculos e regras financeiras de rateio (quem paga o quê), que não são essenciais para validar o fluxo principal no MVP.

---

## Consequências

### Positivas ✅
- **Extensibilidade:** O motor financeiro e logístico passa a suportar qualquer tipo de evento.
- **Limpeza de Código:** Elimina condicionais do tipo `if event_type == 'wedding'` espalhados pelo sistema.
- **Prontidão B2B:** Estrutura pronta para suportar agências com múltiplos usuários de forma nativa.

### Negativas ❌
- **Esforço de Refatoração:** Exige migração de ForeignKeys em todos os módulos existentes e renomeação de mixins e modelos no scheduler.
- **Complexidade de Camadas:** Introduz uma estrutura de arquivos de serviço mais granular que exige rigor na manutenção.

---

## Próximos Passos
1. Renomear `scheduler.Event` para `Appointment`.
2. Criar app `tenants` com o modelo `Company`.
3. Implementar `CompanyOwnedMixin` e `EventOwnedMixin`.
4. Refatorar app `weddings` para `events`, introduzindo `Event` e `WeddingDetail` e a nova estrutura de `services/`.
5. Atualizar as ForeignKeys dos módulos de Finanças e Logística para apontar para `Event`.

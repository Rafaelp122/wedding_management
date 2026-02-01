# Levantamento de Requisitos - Wedding Management System

## 1. Requisitos Funcionais (RF)

O que o sistema PRECISA entregar para ter valor comercial.

### Módulo de Casamentos e Planejamento

**RF01:** O sistema deve permitir o gerenciamento de múltiplos casamentos simultâneos, segregando os dados por evento.

**RF02:** O sistema deve centralizar o perfil dos noivos, data confirmada e local do evento.

### Módulo Financeiro (Orçamento e Parcelas)

**RF03:** O sistema deve permitir a criação de um orçamento mestre com categorias de gastos (Buffet, Decoração, etc.).

**RF04:** O sistema deve oferecer o controle de parcelamento de pagamentos, com status de "Pago", "Pendente" e "Atrasado".

**RF05:** O sistema deve calcular em tempo real a saúde financeira do evento (Gasto Real vs. Estimado).

### Módulo de Logística de Itens

**RF06:** O sistema deve gerenciar uma lista de insumos/serviços com controle de fornecedor vinculado e quantidade necessária.

**RF07:** O sistema deve permitir a atualização de status de aquisição de cada item de forma independente.

### Módulo Jurídico (Contratos)

**RF08:** O sistema deve permitir o upload e armazenamento de contratos em PDF.

**RF09:** O sistema deve implementar uma funcionalidade de assinatura digital para validar os termos entre as partes interessadas.

**RF10:** O sistema deve disparar alertas automáticos para contratos próximos ao vencimento.

### Módulo de Cronograma (Calendário)

**RF11:** O sistema deve fornecer uma agenda interativa para controle de reuniões e marcos (deadlines).

**RF12:** O sistema deve permitir o agendamento de lembretes automáticos via e-mail ou notificações no sistema.

## 2. Requisitos Não Funcionais (RNF)

As restrições técnicas da arquitetura Headless.

**RNF01 (Arquitetura):** O Backend deve ser estritamente uma API REST (Django REST Framework) e o Frontend uma Single Page Application (React). Zero acoplamento de templates.

**RNF02 (Segurança):** A autenticação deve ser Stateless (JWT). Nenhuma informação de sessão deve ser mantida no servidor.

**RNF03 (Interface):** A UI deve ser Mobile-First. Cerimonialistas trabalham na rua, não apenas sentados em um escritório.

**RNF04 (Integridade):** O banco de dados deve garantir a integridade referencial. Se um casamento for deletado, todos os itens e contratos órfãos devem ser tratados (Soft Delete ou Cascade).

**RNF05 (Performance):** O tempo de carregamento inicial da aplicação React não deve exceder 3 segundos sob conexões 4G.

**RNF06 (Padronização):** Toda a API deve ser documentada automaticamente (Swagger/OpenAPI) para permitir integrações futuras.

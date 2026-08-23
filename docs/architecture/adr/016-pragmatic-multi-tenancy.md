# ADR-016: Multi-tenancy Pragmático e Orientado a Organização

## Status
Aceito

## Contexto
Originalmente, o sistema utilizava um modelo de isolamento de dados baseado diretamente no usuário (`PlannerOwnedMixin`), onde cada recurso (casamento, fornecedor, etc.) pertencia a um `User` específico.

Embora funcional para um MVP de usuário único, essa abordagem apresentava limitações críticas:
1. **Escalabilidade de Time**: Impossibilidade de múltiplos usuários (ex: assessores da mesma agência) compartilharem o acesso aos mesmos dados.
2. **Modelo de Negócio SaaS**: Dificuldade em vincular assinaturas e limites de plano a uma entidade organizacional (Empresa) em vez de indivíduos.
3. **Complexidade de Código**: O uso de múltiplos Mixins nos modelos gerava "Mixin Soup" e dificultava a manutenção.

## Decisão
Implementamos uma arquitetura de Multi-tenancy robusta baseada em **Organizações (Companies)**, mantendo a simplicidade para o usuário final através de uma estratégia de **Tenant Pragmático**.

### Mudanças Técnicas:
1. **App `tenants`**: Criado um novo aplicativo para gerenciar o domínio de organizações.
2. **`TenantModel`**: Classe base abstrata que substitui o `PlannerOwnedMixin`. Todo modelo de domínio agora herda de `TenantModel`, garantindo uma chave estrangeira para `Company`.
3. **`TenantManager`**: Centraliza o isolamento de dados através do método `.for_tenant(company)`, reduzindo o risco de vazamento de informações.
4. **Provisionamento Automático**: Para manter o fluxo de "Single-Player" no MVP, utilizamos um **Django Signal** vinculado à criação do `User`. Este signal dispara o `TenantService`, que cria silenciosamente uma `Company` para o novo usuário.

### Estrutura de Posse:
- **Vertical (Empresa)**: `TenantModel` garante que o dado pertença à organização correta.
- **Horizontal (Casamento)**: `WeddingOwnedMixin` continua sendo usado para recursos vinculados a um evento específico dentro de uma empresa.

## Consequências
- **Positivas**:
    - Código mais limpo e declarativo nos modelos.
    - O sistema está pronto para colaboração em equipe (SaaS profissional).
    - Facilidade para implementar modelos de assinatura por empresa.
    - Melhor performance via índices compostos `(company, uuid)`.
- **Negativas**:
    - Pequeno aumento no número de tabelas e relacionamentos iniciais.
    - Necessidade de sempre passar o contexto da `company` para a Service Layer.

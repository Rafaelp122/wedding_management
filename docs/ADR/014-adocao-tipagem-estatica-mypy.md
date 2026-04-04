# ADR 014: Adoção de Tipagem Estática com mypy em Todo o Projeto

## Status
Aceito

## Data
Abril 2026

## Decisor
Rafael

## Contexto
O backend evoluiu com múltiplos domínios de negócio (users, weddings, finances, logistics, scheduler) e integração contratual contínua com frontend via OpenAPI + Orval.

Com o crescimento da base, surgiram riscos recorrentes:

1. Erros de tipo descobertos apenas em runtime.
2. Regressões silenciosas em refactors de Service Layer e APIs.
3. Divergência entre contexto autenticado dinâmico do Django e assinaturas das regras de negócio.
4. Dificuldade para tornar mudanças seguras em módulos críticos sem aumentar custo de revisão manual.

A validação por testes e linting já existia, mas faltava uma camada de verificação estática abrangente para contratos internos Python.

## Decisão
Adotar tipagem estática com mypy + django-stubs como padrão de qualidade obrigatório no backend, com rollout incremental até cobertura de módulos críticos.

### Pilares da decisão

1. Ferramenta oficial de tipagem: mypy.
2. Plugin Django: django-stubs (mypy_django_plugin.main).
3. Política de endurecimento incremental por módulos (overrides), evitando big-bang.
4. Meta de qualidade: mypy global verde e ruff verde em todas as etapas.
5. Inclusão do mypy no pipeline de CI/CD.

## Escopo Implementado

### Configuração e dependências

1. Inclusão de mypy e django-stubs no grupo de desenvolvimento.
2. Configuração central em pyproject:
   - plugin do django-stubs
   - versão de Python
   - regras globais de aviso
   - overrides por módulo com disallow_untyped_defs e check_untyped_defs

### Endurecimento por camadas

1. Service Layer:
   - weddings, scheduler, finances e logistics
   - assinaturas explícitas de entrada/saída
   - padronização de contexto de usuário autenticado
2. API Layer:
   - handlers tipados por domínio
   - dependências tipadas
3. Core:
   - exceptions, mixins, managers e BaseModel tipados
4. Models:
   - users, weddings, scheduler, finances e logistics
   - métodos de domínio tipados (clean, __str__, propriedades utilitárias)

### Pipeline

1. Adição de etapa de mypy no workflow de integridade.
2. Manutenção da validação de contrato OpenAPI + Orval no CI.

## Consequências

### Positivas

1. Redução de regressões por incompatibilidade de tipos em refactors.
2. Maior segurança para evolução de regras de negócio.
3. Feedback mais rápido no desenvolvimento local e no CI.
4. Melhor suporte de IDE (navegação, inferência e autocomplete confiáveis).
5. Integração mais previsível entre camadas (API -> Service -> Model).

### Negativas e trade-offs

1. Aumento inicial de esforço para tipar código legado.
2. Curva de aprendizado para padrões de tipagem com Django ORM.
3. Necessidade de manter overrides e disciplina de expansão gradual.

## Decisões Técnicas Relevantes

1. AuthContextUser consolidado para representar o contexto de autenticação no domínio.
2. Narrowing explícito em operações que exigem usuário autenticado (ex.: criação/edição com ownership).
3. Tipagem de QuerySet e Managers base para manter consistência em for_user.
4. Tipagem de retorno em handlers de API para evitar funções implícitas.
5. Ajustes em nomes/imports para evitar conflitos com campos de model em tempo de import do plugin.

## Resultado Esperado

1. Pipeline com gate estático efetivo para backend Python.
2. Menor incidência de bugs de contrato interno.
3. Base pronta para próximo endurecimento (ex.: testes tipados, módulos auxiliares e convenções avançadas de tipos).

## Critérios de Sucesso

1. mypy global passando sem erros.
2. ruff passando sem violações.
3. CI com etapa de mypy ativa e obrigatória.
4. Contrato OpenAPI/Orval validado sem drift.

## Referências

1. ADR 006 - Service Layer Pattern
2. ADR 009 - Multitenancy
3. ADR 011 - BaseModel com full_clean no save
4. ADR 012 - Contract-Driven Frontend com Orval
5. ADR 013 - Migração de DRF para Django Ninja

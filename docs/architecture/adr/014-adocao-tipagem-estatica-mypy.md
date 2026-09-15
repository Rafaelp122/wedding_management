# ADR-014: Adoção de Tipagem Estática com mypy em Todo o Projeto

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟢 Vigente
> **Data:** Abril 2026
> **Decisor:** Rafael
> **Relacionados:** [ADR-011: BaseModel com save() chamando full_clean()](011-basemodel-save-full-clean.md) · [ADR-012: Contract-Driven Frontend com Orval](012-orval-contract-driven-frontend.md) · [ADR-013: Migração de DRF para Django Ninja](013-migrate-drf-to-ninja.md) · [ADR-016: Pragmatic Multi-Tenancy](016-pragmatic-multi-tenancy.md) · [ADR-030: Rich Domain Model e Service Layer](030-rich-domain-model-service-layer.md)

---

## 1. Contexto e Problema

O backend evoluiu com múltiplos domínios de negócio (users, weddings, finances, logistics, scheduler) e integração contratual contínua com frontend via OpenAPI + Orval.

Com o crescimento da base, surgiram riscos recorrentes:

1. Erros de tipo descobertos apenas em runtime.
2. Regressões silenciosas em refactors de Service Layer e APIs.
3. Divergência entre contexto autenticado dinâmico do Django e assinaturas das regras de negócio.
4. Dificuldade para tornar mudanças seguras em módulos críticos sem aumentar custo de revisão manual.

A validação por testes e linting já existia, mas faltava uma camada de verificação estática abrangente para contratos internos Python.

---

## 2. Decisão

Adotar tipagem estática com mypy + django-stubs como padrão de qualidade obrigatório no backend, com rollout incremental até cobertura de módulos críticos.

### Pilares da decisão

1. **Ferramenta oficial de tipagem:** `mypy`.
2. **Plugin Django:** `django-stubs` (`mypy_django_plugin.main`).
3. **Política de endurecimento incremental por módulos:** Overrides granulares, evitando abordagem big-bang arriscada.
4. **Meta de qualidade:** mypy global verde e ruff verde em todas as etapas de CI.
5. **Inclusão obrigatória no pipeline de CI/CD.**

---

## 3. Escopo Implementado

### Configuração e dependências

1. Inclusão de `mypy` e `django-stubs` no grupo de desenvolvimento (`pyproject.toml`).
2. Configuração central em `pyproject.toml`:
   - plugin do `django-stubs`
   - versão de Python (3.12+)
   - regras globais de aviso
   - overrides por módulo com `disallow_untyped_defs` e `check_untyped_defs`

### Endurecimento por camadas

1. **Service Layer:**
   - `weddings`, `scheduler`, `finances` e `logistics`
   - assinaturas explícitas de entrada e saída
   - padronização de contexto de usuário autenticado
2. **API Layer:**
   - handlers tipados por domínio
   - dependências tipadas
3. **Core:**
   - exceptions, mixins, managers e `BaseModel` tipados
4. **Models:**
   - `users`, `weddings`, `scheduler`, `finances` e `logistics`
   - métodos de domínio tipados (`clean`, `__str__`, propriedades utilitárias)

### Pipeline

1. Adição de etapa de mypy no workflow de integridade do CI.
2. Manutenção da validação de contrato OpenAPI + Orval no CI.

---

## 4. Consequências

### Positivas

1. Redução drástica de regressões por incompatibilidade de tipos em refatores.
2. Maior segurança para evolução de regras de negócio complexas.
3. Feedback imediato no desenvolvimento local e no CI.
4. Suporte de IDE de alta fidelidade (navegação, inferência e autocomplete confiáveis).
5. Integração mais previsível entre camadas (`API -> Service -> Model`).

### Negativas e mitigações

1. **Aumento de esforço inicial:** Exigiu tipagem detalhada de models legados e stubs do Django ORM.
2. **Curva de aprendizado:** Superada pela documentação de padrões de tipagem com Django ORM e stubs.
3. **Manutenção de overrides:** Minimizada pela disciplina de expansão gradual até cobertura estrita total.

---

## 5. Decisões Técnicas Relevantes

1. `AuthContextUser` consolidado para representar o contexto de autenticação no domínio.
2. Narrowing explícito em operações que exigem usuário autenticado (ex.: criação/edição com ownership).
3. Tipagem de `QuerySet` e `Managers` base para manter consistência em `for_tenant`.
4. Tipagem de retorno em handlers de API para evitar funções implícitas.
5. Ajustes em nomes/imports para evitar conflitos com campos de model em tempo de import do plugin.

---

## 6. Resultado Esperado e Critérios de Sucesso

1. `mypy` global passando sem erros no repositório.
2. `ruff` passando sem violações.
3. CI com etapa de `mypy` ativa e obrigatória como quality gate.
4. Contrato OpenAPI/Orval validado sem drift.

---

## 7. Referências

1. [ADR-006: Service Layer Pattern](006-service-layer.md)
2. [ADR-011: BaseModel com save() chamando full_clean()](011-basemodel-save-full-clean.md)
3. [ADR-012: Geração Automática da Camada de API do Frontend via Orval](012-orval-contract-driven-frontend.md)
4. [ADR-013: Migração de DRF para Django Ninja](013-migrate-drf-to-ninja.md)
5. [ADR-016: Pragmatic Multi-Tenancy (Row-Level)](016-pragmatic-multi-tenancy.md)
6. [ADR-030: Rich Domain Model e Service Layer](030-rich-domain-model-service-layer.md)

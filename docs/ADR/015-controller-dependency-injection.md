# ADR 015: Controllers e funções auxiliares de autorização para recursos

## Status

Aceito

## Contexto

Anteriormente, o sistema utilizava instâncias de `ninja.Router()` e funções isoladas para definir endpoints. A responsabilidade de autorização (verificar se um usuário logado era dono de um recurso específico identificado por um UUID) recaía sobre a **Service Layer**.

Isso gerava dois problemas principais:

1. **Fat Services:** O Service Layer deixava de ser focado apenas em regras de negócio para lidar com infraestrutura (recuperação de recursos e erros 404).
2. **Dificuldade de Teste:** Testes de unidade do Service exigiam setups complexos de banco de dados e usuários para validar simples mudanças de estado.

## Decisão

Adotar o padrão de **Controllers** do `django-ninja-extra` em conjunto com **funções auxiliares de autorização** explícitas para resolução de recursos.

Principais mudanças:

- Substituição de `Router()` por classes decoradas com `@api_controller`.
- Criação de funções auxiliares de autorização nos arquivos `dependencies.py` locais de cada app (ex: `get_wedding(request, wedding_uuid)`).
- O Controller agora recupera a instância validada e a passa para o Service.
- O Service agora recebe instâncias prontas de Modelos (`instance: Wedding`) em vez de UUIDs.

## Alternativas Consideradas

**Permission classes do `django-ninja-extra`**
Descartado porque injeta o objeto via `request.wedding` — um efeito colateral implícito que não aparece na assinatura do método, dificultando a leitura do fluxo e a tipagem estática.

**`Depends()` do FastAPI/Ninja v1.10+**
Descartado porque, embora o conceito seja ideal, o recurso não estava disponível ou estável na versão utilizada pelo projeto, e o uso de funções explícitas provê o mesmo ganho de segurança com menor "mágica" de framework.

**Manter autorização no Service Layer**
Descartado porque viola a separação de responsabilidades (SRP) — o Service passa a conhecer o contexto de autenticação e permissões, o que dificulta o reuso da lógica em tarefas de segundo plano (Celery) ou comandos de gerenciamento.

## Consequências

- **Pureza do Domínio:** Os Services tornaram-se "puros", focados 100% em mutação de estado e regras de negócio.
- **Segurança Centralizada:** A lógica de "posse" de recursos está centralizada em funções de dependência no Core, facilitando auditorias.
- **Auditoria Automatizada:** Implementamos testes via AST (`apps/core/tests/test_security_audit.py`) que impedem a criação de endpoints vulneráveis.
- **Melhor Testabilidade:** Testar um Service agora é tão simples quanto instanciar um objeto em memória e passá-lo para a função.

---

## Atualização (27 de Abril 2026): Resolução Nativa via Manager (Estado da Arte)

Para otimizar a performance, a tipagem e a Experiência do Desenvolvedor (DX), evoluímos a resolução de recursos para o "DNA" dos modelos Django:

1. **Método `resolve()` no BaseManager:** Em vez de uma função global, introduzimos o método `Model.objects.resolve(user, uuid)`.
   - _Performance:_ Permite encadeamento, ex: `Budget.objects.select_related('wedding').resolve(user, uuid)`.
   - _Robustez:_ Captura erros de formato de UUID e retorna 404 (ObjectNotFoundError) em vez de 500.
   - _Idempotência:_ Aceita tanto um UUID quanto uma instância já pronta do modelo.

2. **Regra Híbrida de Uso:**
   - **Recurso Principal (ID na URL):** O Controller resolve usando o wrapper local em `dependencies.py` (ex: `get_budget`) e entrega a instância pronta ao Service.
   - **Recursos Relacionados (ID no JSON):** O Service resolve internamente usando `RelatedModel.objects.resolve(user, uuid)`.

3. **DX Superior:** As dependências locais nos apps agora são "Thin Wrappers" explícitos, garantindo docstrings e introspecção completa nos IDEs modernos.

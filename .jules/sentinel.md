## 2025-05-15 - Validação de Complexidade de Senha no Registro
**Vulnerability:** Usuários podiam registrar contas com senhas extremamente fracas (ex: "12345678", "password"), apesar de o Django possuir validadores configurados em `AUTH_PASSWORD_VALIDATORS`.
**Learning:** No Django Ninja (ou qualquer fluxo customizado), o método `create_user` ou `set_password` do `UserManager` padrão NÃO invoca automaticamente os validadores de complexidade do Django. A validação do Pydantic no Schema apenas checava o tamanho mínimo (`min_length=8`).
**Prevention:** Sempre chamar explicitamente `django.contrib.auth.password_validation.validate_password(password)` na Service Layer antes de criar o usuário.

## 2025-05-22 - Implementação de Rate Limiting (Throttling)
**Vulnerability:** Endpoints de autenticação (/auth/token/) e registro (/auth/register/) estavam expostos a ataques de força bruta e DoS por falta de limites de requisição.
**Learning:** O Django Ninja (via `django-ninja-extra`) requer que as instâncias de throttle sejam passadas no parâmetro `throttle` do decorator (ex: `throttle=[AuthAnonRateThrottle()]`) e que o `Router` utilizado seja o do `ninja_extra` para garantir o processamento correto dos metadados de throttling.
**Prevention:** Sempre aplicar throttling em endpoints sensíveis (auth, password reset, etc.) e validar com testes de integração que disparam HTTP 429 após o limite ser atingido.

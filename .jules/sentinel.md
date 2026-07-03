## 2025-05-15 - Validação de Complexidade de Senha no Registro
**Vulnerability:** Usuários podiam registrar contas com senhas extremamente fracas (ex: "12345678", "password"), apesar de o Django possuir validadores configurados em `AUTH_PASSWORD_VALIDATORS`.
**Learning:** No Django Ninja (ou qualquer fluxo customizado), o método `create_user` ou `set_password` do `UserManager` padrão NÃO invoca automaticamente os validadores de complexidade do Django. A validação do Pydantic no Schema apenas checava o tamanho mínimo (`min_length=8`).
**Prevention:** Sempre chamar explicitamente `django.contrib.auth.password_validation.validate_password(password)` na Service Layer antes de criar o usuário.

## 2025-05-22 - Throttling de API no Django Ninja Extra
**Vulnerability:** Endpoints sensíveis (registro e login) estavam expostos a ataques de força bruta e enumeração de contas por falta de limitação de taxa (rate limiting).
**Learning:** O `django-ninja` padrão não possui throttling embutido nos decorators. É necessário usar `ninja_extra.Router` e configurar `THROTTLE_RATES` no `settings.py`. Testes automatizados de endpoints com throttling falham se o cache não for limpo entre as execuções.
**Prevention:** Utilizar `ninja_extra.Router` e o parâmetro `throttle` nos decorators de endpoints críticos. Adicionar um fixture `autouse` no `conftest.py` para limpar o cache durante os testes.

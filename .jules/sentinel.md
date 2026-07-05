## 2025-05-15 - Validação de Complexidade de Senha no Registro
**Vulnerability:** Usuários podiam registrar contas com senhas extremamente fracas (ex: "12345678", "password"), apesar de o Django possuir validadores configurados em `AUTH_PASSWORD_VALIDATORS`.
**Learning:** No Django Ninja (ou qualquer fluxo customizado), o método `create_user` ou `set_password` do `UserManager` padrão NÃO invoca automaticamente os validadores de complexidade do Django. A validação do Pydantic no Schema apenas checava o tamanho mínimo (`min_length=8`).
**Prevention:** Sempre chamar explicitamente `django.contrib.auth.password_validation.validate_password(password)` na Service Layer antes de criar o usuário.

## 2025-05-16 - Isolamento de Testes com Throttling (Rate Limiting)
**Vulnerability:** A introdução de Throttling em endpoints de autenticação causou falhas em testes pré-existentes de API.
**Learning:** O `ninja-extra` armazena os contadores de requisição no Cache do Django. Em ambiente de teste usando `LocMemCache`, o estado do cache persiste entre os testes se não for limpo explicitamente, levando a erros HTTP 429 inesperados em suítes de testes grandes.
**Prevention:** Implementar um fixture global `autouse` no `conftest.py` que execute `django.core.cache.cache.clear()` antes de cada caso de teste para garantir isolamento total.

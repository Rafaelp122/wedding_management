## 2025-05-15 - Validação de Complexidade de Senha no Registro
**Vulnerability:** Usuários podiam registrar contas com senhas extremamente fracas (ex: "12345678", "password"), apesar de o Django possuir validadores configurados em `AUTH_PASSWORD_VALIDATORS`.
**Learning:** No Django Ninja (ou qualquer fluxo customizado), o método `create_user` ou `set_password` do `UserManager` padrão NÃO invoca automaticamente os validadores de complexidade do Django. A validação do Pydantic no Schema apenas checava o tamanho mínimo (`min_length=8`).
**Prevention:** Sempre chamar explicitamente `django.contrib.auth.password_validation.validate_password(password)` na Service Layer antes de criar o usuário.

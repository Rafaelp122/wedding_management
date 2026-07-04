## 2025-05-15 - Validação de Complexidade de Senha no Registro
**Vulnerability:** Usuários podiam registrar contas com senhas extremamente fracas (ex: "12345678", "password"), apesar de o Django possuir validadores configurados em `AUTH_PASSWORD_VALIDATORS`.
**Learning:** No Django Ninja (ou qualquer fluxo customizado), o método `create_user` ou `set_password` do `UserManager` padrão NÃO invoca automaticamente os validadores de complexidade do Django. A validação do Pydantic no Schema apenas checava o tamanho mínimo (`min_length=8`).
**Prevention:** Sempre chamar explicitamente `django.contrib.auth.password_validation.validate_password(password)` na Service Layer antes de criar o usuário.

## 2025-05-20 - Falta de Limitação de Taxa (Throttling) em Endpoints de Autenticação
**Vulnerability:** Endpoints sensíveis como `/register/` e `/token/` não possuíam limitação de taxa, permitindo ataques de força bruta e negação de serviço (DoS).
**Learning:** O `django-ninja` básico não inclui throttling por padrão. É necessário utilizar `django-ninja-extra` e configurar explicitamente os validadores de taxa (`throttle`) nos routers ou endpoints. Além disso, as taxas devem usar abreviações de uma letra (ex: '5/m') para evitar erros de parsing.
**Prevention:** Aplicar `AnonRateThrottle` em todos os endpoints de autenticação e registro. Utilizar uma fixture global para limpar o cache nos testes automatizados para evitar que o estado do throttle vaze entre casos de teste.

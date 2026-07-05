## 2025-05-15 - Validação de Complexidade de Senha no Registro
**Vulnerability:** Usuários podiam registrar contas com senhas extremamente fracas (ex: "12345678", "password"), apesar de o Django possuir validadores configurados em `AUTH_PASSWORD_VALIDATORS`.
**Learning:** No Django Ninja (ou qualquer fluxo customizado), o método `create_user` ou `set_password` do `UserManager` padrão NÃO invoca automaticamente os validadores de complexidade do Django. A validação do Pydantic no Schema apenas checava o tamanho mínimo (`min_length=8`).
**Prevention:** Sempre chamar explicitamente `django.contrib.auth.password_validation.validate_password(password)` na Service Layer antes de criar o usuário.

## 2026-07-05 - Implementação de Throttling no Django Ninja Extra
**Vulnerability:** Endpoints sensíveis de autenticação (registro, login) estavam expostos a ataques de força bruta e DoS por falta de limite de taxa (rate limiting).
**Learning:** Para implementar throttling no Django Ninja Extra, é obrigatório: 1) Usar `ninja_extra.Router` em vez de `ninja.Router`. 2) Configurar um backend de `CACHES` no Django. 3) Definir `THROTTLE_RATES` nas configurações de `NINJA_EXTRA`.
**Prevention:** Sempre aplicar `AnonRateThrottle` em endpoints públicos e críticos e garantir que o ambiente de teste limpe o cache entre execuções para evitar falsos negativos (429 inesperados).

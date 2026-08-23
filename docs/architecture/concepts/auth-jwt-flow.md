# Arquitetura: Fluxo de Autenticação JWT, Onboarding e OAuth2

> **Módulo:** [auth-jwt-flow](auth-jwt-flow.md) | [users-domain](../domains/users-domain.md) | [tenants-domain](../domains/tenants-domain.md)
> **Camada:** Backend (`RegistrationService`, `TokenService`, `GoogleAuthService`) e Frontend (`Axios Interceptors`, `useAuthStore`)

---

## 1. Ciclo de Vida dos Tokens JWT (`TokenService`)

1. **Login (`POST /api/v1/auth/login`):** Valida e-mail e senha via `authenticate()`, retornando um `access_token` (vida curta) e um `refresh_token` (vida longa).
2. **Requisições Autenticadas:** O frontend anexa o cabeçalho `Authorization: Bearer <access_token>` em todas as chamadas API.
3. **Renovação Transparente (`Refresh Token Flow`):**
   - Quando o `access_token` expira, a API responde `401 Unauthorized`.
   - O Axios Response Interceptor detecta o `401`, enfileira requisições pendentes e chama automaticamente `POST /api/v1/auth/refresh`.
   - Com o novo `access_token` recebido, o interceptor re-executa as requisições que haviam falhado de forma transparente para o usuário.
   - Se o `refresh_token` também estiver expirado, o estado de autenticação é limpo (`clearAuth()`) e o usuário é redirecionado para a tela de login.

---

## 2. Onboarding e Verificação de E-mail (`RegistrationService`)

No cadastro de um novo proprietário (`POST /api/v1/auth/register`):
- O backend executa o cadastro do usuário e a criação da empresa (`Company`) em uma **transação atômica** (`@transaction.atomic`).
- Valida a senha usando os validadores do Django (`validate_password`).
- Garante a unicidade do e-mail antes de criar a empresa (`email_already_exists`).
- O usuário é criado inativo (`is_active=False`, `is_email_verified=False`) e associado como responsável pela empresa.
- Após o commit da transação, `EmailVerificationService` envia um link com `uid` e token para `/verify-email`.

Na confirmação (`POST /api/v1/auth/verify-email/`):
1. O backend decodifica o `uid` e valida o token pelo `default_token_generator`.
2. Tokens inválidos ou expirados retornam `400` com `code="invalid_token"`.
3. Tokens válidos definem `is_email_verified=True`, registram `email_verified_at` e ativam a conta (`is_active=True`).

O reenvio (`POST /api/v1/auth/resend-verification/`) é público, limitado por throttle e não revela se o e-mail existe. O serviço só envia mensagem para contas ainda não verificadas.

## 3. Redefinição de Senha (`PasswordResetService`)

O fluxo usa o mesmo gerador de tokens do Django e não revela a existência da conta:

1. `POST /api/v1/auth/password-reset/request/` recebe o e-mail e envia o link apenas para usuários ativos.
2. O link contém `uid` e token e direciona para a tela de redefinição no frontend.
3. `POST /api/v1/auth/password-reset/confirm/` valida o token, valida a nova senha e salva a senha criptografada.
4. Token inválido ou expirado retorna `400` com `code="invalid_token"`; senha inválida retorna `400` com `code="invalid_password"`.

Os endpoints possuem throttles separados para solicitação e confirmação, reduzindo abuso do fluxo de envio e de validação de tokens.

---

## 4. Autenticação e Auto-Provisionamento via Google OAuth2 (`GoogleAuthService`)

No login ou cadastro via Google (`POST /api/v1/auth/google`):
1. O backend recebe o `id_token` do Google e valida sua assinatura e emissor via `GoogleOAuthProvider`.
2. Se o usuário já existe na plataforma, valida o status ativo (`is_active`) e emite o par de JWTs.
3. Se for um novo usuário, o serviço executa o auto-provisionamento atômico:
   - Gera uma senha aleatória segura via `User.objects.make_random_password()`.
   - Cria o workspace tenant via `TenantService.create_company()`.
   - Cria e ativa a conta de usuário (`is_active=True`, `is_email_verified=True`), pois o provedor já validou o e-mail.

---

## 5. Diretrizes de Proteção de PII e Auditoria de Logs

Para cumprir regulamentações de privacidade e evitar o vazamento de segredos nos logs do servidor:
- **Mascaramento de E-mail (`_mask_email`):** Todos os logs de auditoria mascaram o e-mail do usuário (ex: `r*****l@domain.com`).
- **Fingerprint de Tokens:** Os tokens JWT recebidos no `refresh` e `verify` são logados apenas pela sua *fingerprint* SHA-256 truncada (`hashlib.sha256(token).hexdigest()[:12]`), impedindo a exposição de tokens brutos nos arquivos de log.

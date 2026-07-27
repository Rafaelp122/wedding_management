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

## 2. Onboarding Atômico de Proprietários (`RegistrationService`)

No cadastro de um novo proprietário (`POST /api/v1/auth/register`):
- O backend executa o cadastro do usuário e a criação da empresa (`Company`) em uma **transação atômica** (`@transaction.atomic`).
- Valida a senha usando os validadores do Django (`validate_password`).
- Garante a unicidade do e-mail antes de criar a empresa (`email_already_exists`).
- O usuário é ativado (`is_active=True`) e associado como responsável pela empresa.

---

## 3. Autenticação e Auto-Provisionamento via Google OAuth2 (`GoogleAuthService`)

No login ou cadastro via Google (`POST /api/v1/auth/google`):
1. O backend recebe o `id_token` do Google e valida sua assinatura e emissor via `GoogleOAuthProvider`.
2. Se o usuário já existe na plataforma, valida o status ativo (`is_active`) e emite o par de JWTs.
3. Se for um novo usuário, o serviço executa o auto-provisionamento atômico:
   - Gera uma senha aleatória segura via `User.objects.make_random_password()`.
   - Cria o workspace tenant via `TenantService.create_company()`.
   - Cria e ativa a conta de usuário (`is_active=True`).

---

## 4. Diretrizes de Proteção de PII e Auditoria de Logs

Para cumprir regulamentações de privacidade e evitar o vazamento de segredos nos logs do servidor:
- **Mascaramento de E-mail (`_mask_email`):** Todos os logs de auditoria mascaram o e-mail do usuário (ex: `r*****l@domain.com`).
- **Fingerprint de Tokens:** Os tokens JWT recebidos no `refresh` e `verify` são logados apenas pela sua *fingerprint* SHA-256 truncada (`hashlib.sha256(token).hexdigest()[:12]`), impedindo a exposição de tokens brutos nos arquivos de log.

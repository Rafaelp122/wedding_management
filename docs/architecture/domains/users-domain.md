# MOC de Domínio: Users & Authentication

> **Hub de Domínio:** [users-domain](users-domain.md) | [system-overview](../concepts/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/users/` & `frontend/src/features/auth/`

---

## Visão Geral do Domínio

O domínio de **Users** gerencia os usuários da plataforma, credenciais, autenticação JWT, integração OAuth2 com Google, onboarding de empresas e associação ao Workspace/Company (Tenant).

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/users/`)
- **Modelo de Dados:** [user-model](../../reference/models/users/user-model.md) — Custom User Model com `email` como `USERNAME_FIELD` e `CustomUserManager`.
- **Service Layer:**
  - `registration_service.py`: Onboarding atômico de novo proprietário (`register_new_owner`) com criação simultânea de `User` + `Company`.
  - `token_service.py`: Emissão, renovação e validação de tokens JWT (`obtain`, `refresh`, `verify`) com fingerprint SHA-256 nos logs.
  - `email_verification_service.py`: Envio, validação e reenvio de links de verificação de e-mail; ativa contas após confirmação.
  - `password_reset_service.py`: Solicitação e confirmação de redefinição de senha com tokens temporários e respostas que evitam enumeração de usuários.
  - `google_auth_service.py`: Autenticação social com Google OAuth2 (`authenticate_with_google`), auto-provisionamento com senha aleatória e mascaramento PII (`_mask_email`).
- **Arquitetura de Autenticação:** [auth-jwt-flow](../concepts/auth-jwt-flow.md).

### 2. Camada de Frontend (`frontend/src/features/auth/`)
- **Páginas (Smart Containers):**
  - `LoginPage.tsx` — Autenticação e login de usuários.
  - `RegisterPage.tsx` — Cadastro e criação de novos workspaces.
  - `VerifyEmailPage.tsx` — Confirmação do link de verificação e ativação da conta.
  - `VerifyEmailPendingPage.tsx` — Orientação e reenvio do e-mail de ativação.
  - `ForgotPasswordPage.tsx` / `ResetPasswordPage.tsx` — Solicitação e confirmação de nova senha.
- **Componentes (Views/Forms):**
  - `AuthLayout.tsx` — Layout padrão das telas de autenticação com hero promocional.
  - `LoginForm.tsx` — Formulário de login controlado por `react-hook-form` + `zod`.
  - `RegisterForm.tsx` — Formulário de cadastro com validação de senha.
  - `PasswordInput.tsx` — Input customizado com alternador de visibilidade.
  - `SocialButtons.tsx` — Botões de login social.
- **Estado Global:** `useAuthStore` (`src/stores/authStore.ts`).

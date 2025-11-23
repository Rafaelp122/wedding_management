# App: Users

O app `users` gerencia **autenticação, autorização e perfis de usuários** do sistema. Integrado com **Django Allauth** para fornecer signup, login, logout, recuperação de senha e gestão de sessões. Suporta interfaces **Web** (templates) e **API REST** (DRF).

---

## Status Atual

**Versão:** 2.0 (Arquitetura Híbrida: Web + API)  
**Testes:** 36 passando  
**Cobertura:** models, forms, views, serializers, urls, integração  
**Interfaces:** Web (Django + Allauth) + API (Django REST Framework)

---

## Responsabilidades

-   **Autenticação:** Login, Logout, Signup, Password Reset (via Django Allauth)
-   **Autorização:** Permissões e grupos de usuários
-   **Custom User Model:** Email como identificador principal
-   **Perfil de Usuário:** Edição de nome, email, username
-   **Validações:** Email único, username único, senhas fortes
-   **API REST:** CRUD de usuários, change password, profile endpoint

---

## Arquitetura

### Padrões Aplicados
- **Custom User Model:** Herda de `AbstractUser` com email único
- **Manager Pattern:** `CustomUserManager` para create_user/create_superuser
- **Django Allauth Integration:** Views customizadas com contexto extra
- **Hybrid Architecture:** Web (allauth) + API (DRF) com autenticação compartilhada
- **Form Styling:** Mixins do core para consistência visual
- **Separation of Concerns:** web/ (templates) e api/ (REST) separados

---

## Estrutura de Arquivos

### Models (`models.py`)

-   **`CustomUserManager` (BaseUserManager):**
    - **`create_user(username, email, password, **extra_fields)`:**
        - Valida email e username obrigatórios
        - Normaliza email (domínio em lowercase)
        - Criptografa senha com `set_password()`
        - Retorna User instance
    - **`create_superuser(username, email, password, **extra_fields)`:**
        - Define `is_staff=True`, `is_superuser=True`, `is_active=True`
        - Valida que flags foram setadas corretamente
        - Chama `create_user()` internamente

-   **`User` (AbstractUser):**
    - **Campos:**
        - `email` (EmailField, unique=True) - Identificador principal
        - `username` (CharField, unique=True, max 255) - Username único
        - `first_name`, `last_name` (herdados de AbstractUser)
        - `is_staff`, `is_superuser`, `is_active` (herdados)
        - `date_joined`, `last_login` (herdados)
    - **Configuração:**
        - `REQUIRED_FIELDS = ["email"]` - Email obrigatório no createsuperuser
        - `objects = CustomUserManager()` - Manager customizado
    - **Métodos:**
        - `__str__()` - Retorna email

### Web Interface (`web/`)

#### Forms (`web/forms.py`)

-   **`CustomUserCreationForm` (FormStylingMixinLarge + SignupForm):**
    - Herda de `allauth.account.forms.SignupForm`
    - Campos extras: `first_name`, `last_name`
    - Placeholders e labels em português
    - Logging de falhas de registro
    - `save(request)` - Salva first_name e last_name

-   **`CustomLoginForm` (FormStylingMixinLarge + LoginForm):**
    - Herda de `allauth.account.forms.LoginForm`
    - Campo "Usuário ou E-mail"
    - Checkbox "Lembrar de mim"
    - Styling Bootstrap aplicado

-   **`CustomResetPasswordForm` (FormStylingMixinLarge + ResetPasswordForm):**
    - Herda de `allauth.account.forms.ResetPasswordForm`
    - Campo de email para recuperação
    - Styling Bootstrap aplicado

-   **`CustomUserChangeForm` (FormStylingMixin + UserChangeForm):**
    - Formulário de edição de perfil
    - Campos: username, first_name, last_name, email
    - **Sem campo de senha** (evita alteração acidental)
    - Placeholders e labels customizados

#### Views (`web/views.py`)

-   **`EditProfileView` (LoginRequiredMixin + UpdateView):**
    - Permite editar perfil do usuário logado
    - Form: `CustomUserChangeForm`
    - Template: `users/edit_profile.html`
    - Success: Redireciona para `weddings:my_weddings`
    - Contexto extra: layout, ícones, action, button_text

#### Allauth Views (`web/allauth_views.py`)

Views customizadas que sobrescrevem as padrão do Django Allauth:

-   **`CustomSignupView` (SignupView):**
    - Adiciona `form_layout_dict` (col-md-6 para campos)
    - Adiciona `form_icons` (FontAwesome icons)
    - Button text: "Cadastrar"

-   **`CustomLoginView` (LoginView):**
    - Layout: col-md-12 para campos
    - Ícones: user, lock
    - Button text: "Entrar"

-   **`CustomLogoutView` (LogoutView):**
    - View padrão (sem customizações)

-   **`CustomPasswordResetView` (PasswordResetView):**
    - Layout: col-md-12 para email
    - Button text: "Enviar Instruções"

#### Adapter (`web/adapters.py`)

-   **`CustomAccountAdapter` (DefaultAccountAdapter):**
    - Adapter do Allauth para customizações futuras
    - Placeholder para lógica customizada de signup/login

#### URLs (`web/urls.py`)

-   **Namespace:** `users`
-   **Rotas Web:**
    - `/edit-profile/` - EditProfileView (name: `edit_profile`)
    - Allauth URLs integradas via `include('allauth.urls')`

### API Interface (`api/`)

#### Serializers (`api/serializers.py`)

-   **`UserSerializer` (ModelSerializer):**
    - **Campos:** username, email, first_name, last_name, password, password_confirm
    - **Write-only:** password, password_confirm
    - **Validações:**
        - Senhas devem ser iguais
        - Password é hasheado no `create()` e `update()`
    - **Uso:** CRUD de usuários

-   **`UserListSerializer` (ModelSerializer):**
    - **Campos:** id, username, email, full_name
    - **SerializerMethodField:** `full_name` (first_name + last_name ou username)
    - **Uso:** Listagem otimizada de usuários

-   **`UserDetailSerializer` (ModelSerializer):**
    - **Campos:** id, username, email, first_name, last_name, date_joined, weddings_count, items_count
    - **SerializerMethodField:** `weddings_count`, `items_count`
    - **Uso:** Detalhes completos do usuário

-   **`ChangePasswordSerializer` (Serializer):**
    - **Campos:** old_password, new_password, confirm_password
    - **Validações:**
        - old_password deve estar correta
        - new_password == confirm_password
    - **Uso:** Endpoint de mudança de senha

#### Views (`api/views.py`)

-   **`UserViewSet` (ModelViewSet):**
    - **Endpoints:**
        - `GET /api/v1/users/` - Lista usuários
        - `POST /api/v1/users/` - Cria usuário
        - `GET /api/v1/users/{id}/` - Detalhes do usuário
        - `PUT /api/v1/users/{id}/` - Atualiza completo
        - `PATCH /api/v1/users/{id}/` - Atualiza parcial
        - `DELETE /api/v1/users/{id}/` - Deleta usuário
        - `POST /api/v1/users/{id}/change-password/` - Muda senha
    - **Serializers:** UserSerializer (list/create), UserDetailSerializer (retrieve)
    - **Permissions:** IsAuthenticated
    - **Custom Action:** `change_password` (POST only)

#### URLs (`api/urls.py`)

-   **Router:** DRF DefaultRouter
-   **Basename:** `user`
-   **Namespace:** `users_api`

### Admin (`admin.py`)

-   **`CustomUserAdmin` (UserAdmin):**
    - **List Display:** email, username, first_name, last_name, is_staff
    - **Search Fields:** email, username, first_name, last_name
    - **Ordering:** email
    - **Fieldsets:** Email/Password, Personal info, Permissions, Important dates
    - **Add Fieldsets:** username, email, password, password2

---

## Testes (`tests/`)

### `test_models.py` (13 testes)

#### UserModelTest (8 testes):
- ✅ **test_create_user_with_valid_data** - Criação básica de usuário
- ✅ **test_create_superuser_with_valid_data** - Superuser com flags corretas
- ✅ **test_create_user_raises_error_without_email** - ValueError se email vazio
- ✅ **test_create_user_raises_error_without_username** - ValueError se username vazio
- ✅ **test_create_superuser_validates_permissions** - Valida is_staff e is_superuser
- ✅ **test_email_normalization** - Domínio em lowercase
- ✅ **test_string_representation** - __str__ retorna email

#### UserModelIntegrationTest (5 testes):
- ✅ **test_email_must_be_unique** - IntegrityError em email duplicado
- ✅ **test_username_must_be_unique** - IntegrityError em username duplicado
- ✅ **test_username_max_length_validation** - Rejeita username > 255 chars
- ✅ **test_direct_instantiation_validation** - full_clean() valida campos obrigatórios

### `web/test_forms.py` (8 testes)

#### CustomUserCreationFormTest (6 testes):
- ✅ **test_form_valid_registration** - Registro com dados válidos
- ✅ **test_form_invalid_password_mismatch** - Rejeita senhas diferentes
- ✅ **test_form_invalid_duplicate_email** - Rejeita email duplicado
- ✅ **test_form_has_large_css_classes** - FormStylingMixinLarge aplicado
- ✅ **test_form_logs_warning_on_failure** - Logging de erros

#### CustomUserChangeFormTest (2 testes):
- ✅ **test_form_updates_fields** - Atualiza username, email, first_name, last_name
- ✅ **test_password_field_is_removed** - Sem campo de senha no form

### `web/test_views.py` (5 testes)

#### EditProfileViewTest (5 testes):
- ✅ **test_anonymous_redirected_to_login** - Anônimo → 302
- ✅ **test_get_renders_form_with_instance** - Renderiza form preenchido
- ✅ **test_post_updates_profile** - Atualiza perfil com sucesso
- ✅ **test_post_update_duplicate_email_fails** - Rejeita email já usado
- ✅ **test_post_update_invalid_data_shows_errors** - Mostra erros de validação

### `web/test_urls.py` (4 testes)
- ✅ **test_signup_url_resolves** - URL signup resolve
- ✅ **test_signin_url_resolves** - URL login resolve
- ✅ **test_logout_url_resolves** - URL logout resolve
- ✅ **test_edit_profile_url_resolves** - URL edit_profile resolve

### `api/test_serializers.py` (6 testes)

#### UserSerializerTest (3 testes):
- ✅ **test_serialization** - Serializa User corretamente
- ✅ **test_deserialization_valid** - Deserializa dados válidos
- ✅ **test_validation_password_mismatch** - Rejeita senhas diferentes
- ✅ **test_update_without_password** - Permite update sem alterar senha

#### UserListSerializerTest (2 testes):
- ✅ **test_serialization_with_full_name** - full_name com first + last
- ✅ **test_full_name_fallback_to_username** - full_name = username se nome vazio

#### UserDetailSerializerTest (1 teste):
- ✅ **test_serialization_with_counts** - Inclui weddings_count e items_count

#### ChangePasswordSerializerTest (2 testes):
- ✅ **test_valid_data** - Aceita dados válidos
- ✅ **test_validation_password_mismatch** - Rejeita senhas diferentes

**Total:** 36 testes passando ✅

---

## Fluxo de Autenticação

### 1. Signup (Web):
```
[Usuário] 
    → Acessa /accounts/signup/
    → Preenche CustomUserCreationForm
    → Allauth valida dados
    → CustomUserManager.create_user()
    → User salvo no banco
    → Login automático (opcional)
    → Redirect para my_weddings
```

### 2. Login (Web):
```
[Usuário]
    → Acessa /accounts/login/
    → Preenche CustomLoginForm (username ou email)
    → Allauth autentica
    → Session criada
    → Redirect para LOGIN_REDIRECT_URL
```

### 3. Password Reset (Web):
```
[Usuário]
    → Acessa /accounts/password/reset/
    → Preenche CustomResetPasswordForm (email)
    → Allauth envia email com token
    → Usuário clica no link
    → Define nova senha
    → Login manual
```

### 4. API Authentication:
```
[Cliente API]
    → POST /api/v1/users/login/ (com SessionAuthentication)
    → Recebe session cookie
    → Usa cookie em requisições subsequentes
    
    Ou:
    → Usa TokenAuthentication (se configurado)
```

---

## Segurança

### Model Level:
- ✅ Email único (unique constraint no banco)
- ✅ Username único (unique constraint no banco)
- ✅ Senha hasheada com PBKDF2 (Django default)
- ✅ Normalização de email (domínio lowercase)
- ✅ Validação de comprimento (username ≤ 255)

### View Level (Web):
- ✅ `LoginRequiredMixin` em EditProfileView
- ✅ CSRF protection em todos os forms
- ✅ Allauth valida tentativas de login (rate limiting configurável)

### API Level:
- ✅ `IsAuthenticated` permission em todos os endpoints
- ✅ Password não retornado em serializers (write_only=True)
- ✅ Old password validado em change_password
- ✅ Hashing automático de novas senhas

---

## Integração com Django Allauth

### Configuração (settings/base.py):
```python
INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ...
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_FORMS = {
    'signup': 'apps.users.web.forms.CustomUserCreationForm',
    'login': 'apps.users.web.forms.CustomLoginForm',
    'reset_password': 'apps.users.web.forms.CustomResetPasswordForm',
}
ACCOUNT_ADAPTER = 'apps.users.web.adapters.CustomAccountAdapter'
```

### Views Customizadas (urls.py):
```python
from apps.users.web.allauth_views import (
    CustomSignupView, CustomLoginView, 
    CustomLogoutView, CustomPasswordResetView
)

urlpatterns = [
    path('signup/', CustomSignupView.as_view(), name='account_signup'),
    path('login/', CustomLoginView.as_view(), name='account_login'),
    # ...
]
```

---

## Performance

- **Queries otimizadas:** `select_related`, `prefetch_related` quando necessário
- **Indexação:** Email e username têm índices únicos automáticos
- **API Pagination:** DRF pagina listas de usuários (PAGE_SIZE=10)
- **Session Cache:** Redis como backend de sessão (configurável)

---

## Melhorias Recentes (v2.0)

### Implementado:
1. ✅ Custom User Model com CustomUserManager
2. ✅ Integração completa com Django Allauth
3. ✅ Forms customizados com styling Bootstrap
4. ✅ Views customizadas (signup, login, reset, edit profile)
5. ✅ API REST completa (CRUD + change password)
6. ✅ Serializers com 3 níveis (List, Detail, Full)
7. ✅ 36 testes cobrindo models, forms, views, serializers

---

## Melhorias Futuras (v3.0 - Considerando)

### Autenticação Social:
1. **Google OAuth:** Login com Google (via allauth.socialaccount)
2. **GitHub OAuth:** Login com GitHub
3. **Facebook OAuth:** Login com Facebook

### Features Avançados:
1. **Two-Factor Authentication (2FA):**
   - TOTP com django-otp
   - SMS backup (Twilio)

2. **Token Authentication:**
   - JWT com djangorestframework-simplejwt
   - Refresh tokens

3. **Avatar de Usuário:**
   - Upload de foto de perfil
   - Crop automático

4. **Activity Log:**
   - Histórico de logins
   - Log de mudanças de perfil

5. **Email Verification:**
   - Ativar `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'`
   - Templates customizados de email

---

## Dependências

### Apps Django:
- `django.contrib.auth` - Base de autenticação
- `django.contrib.sessions` - Sessões de usuário
- `allauth.account` - Signup, login, reset
- `rest_framework` - API REST

### Apps do Projeto:
- `apps.core.mixins` - FormStylingMixin, FormStylingMixinLarge
- `apps.core.utils` - add_placeholder
- `apps.weddings` - Relacionamento (User.weddings)
- `apps.items` - Relacionamento indireto (User → Wedding → Items)

---

## Exemplos de Uso

### 1. Criar usuário via Manager:
```python
from apps.users.models import User

# Usuário comum
user = User.objects.create_user(
    username='johndoe',
    email='john@example.com',
    password='securepass123',
    first_name='John',
    last_name='Doe'
)

# Superusuário
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)
```

### 2. Autenticar via API (Python):
```python
import requests

# Login
session = requests.Session()
response = session.post('http://localhost:8000/api/v1/auth/login/', json={
    'username': 'johndoe',
    'password': 'securepass123'
})

# Usar session cookie em outras requisições
users = session.get('http://localhost:8000/api/v1/users/').json()
```

### 3. Mudar senha via API:
```python
response = session.post(
    'http://localhost:8000/api/v1/users/me/change-password/',
    json={
        'old_password': 'oldpass',
        'new_password': 'newpass123',
        'confirm_password': 'newpass123'
    }
)
```

### 4. Acessar weddings de um usuário:
```python
user = User.objects.get(username='johndoe')
weddings = user.weddings.all()  # via related_name='planner'

for wedding in weddings:
    print(f"{wedding.groom_name} & {wedding.bride_name}")
```

---

## Comandos Úteis

### Executar testes:
```bash
# Via pytest (recomendado)
pytest apps/users/tests/ -v

# Testes por categoria
pytest apps/users/tests/test_models.py -v
pytest apps/users/tests/web/ -v
pytest apps/users/tests/api/ -v

# Com coverage
pytest apps/users/tests/ --cov=apps.users --cov-report=html
```

### Criar usuários no shell:
```python
python manage.py shell

from apps.users.models import User

# Criar usuário
user = User.objects.create_user('testuser', 'test@example.com', 'pass123')

# Listar usuários
User.objects.all()

# Buscar por email
User.objects.get(email='test@example.com')
```

### Criar superusuário:
```bash
python manage.py createsuperuser
# Pede: username, email, password
```

---

## Endpoints API

| Método | URL | Descrição | Auth |
|--------|-----|-----------|------|
| GET | `/api/v1/users/` | Lista usuários | ✅ |
| POST | `/api/v1/users/` | Cria usuário | ✅ |
| GET | `/api/v1/users/{id}/` | Detalhes do usuário | ✅ |
| PUT | `/api/v1/users/{id}/` | Atualiza completo | ✅ |
| PATCH | `/api/v1/users/{id}/` | Atualiza parcial | ✅ |
| DELETE | `/api/v1/users/{id}/` | Deleta usuário | ✅ |
| POST | `/api/v1/users/{id}/change-password/` | Muda senha | ✅ |

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** 2.0 - Arquitetura Híbrida (Web + API) com Django Allauth

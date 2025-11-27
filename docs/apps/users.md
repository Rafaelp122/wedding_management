# Users - Documentação Técnica Completa

Sistema de autenticação e gestão de usuários com Django Allauth e API REST.

**Versão:** 2.0  
**Status:** ✅ 36 testes passando  
**Arquitetura:** Híbrida - Django Allauth (Web) + Django REST Framework (API)  

---

## Índice

- [Visão Geral](#visão-geral)
- [Custom User Model](#custom-user-model)
- [Interface Web (Allauth)](#interface-web-allauth)
- [Interface API (DRF)](#interface-api-drf)
- [Segurança](#segurança)
- [Testes](#testes)
- [Fluxos de Autenticação](#fluxos-de-autenticação)

---

## Visão Geral

O app `users` gerencia **autenticação, autorização e perfis de usuários** do sistema. Integra Django Allauth para fornecer signup, login, logout e recuperação de senha, além de uma API REST completa para integrações programáticas.

### Responsabilidades

-   **Autenticação:** Login, Logout, Signup, Password Reset
-   **Autorização:** Permissões e grupos de usuários
-   **Custom User Model:** Email como identificador principal
-   **Perfil de Usuário:** Edição de nome, email, username
-   **Validações:** Email único, username único, senhas fortes
-   **API REST:** CRUD de usuários, change password, profile endpoint

---

## Custom User Model

### CustomUserManager

**Manager customizado que substitui o padrão do Django:**

```python
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """Cria e retorna um User com username, email e senha"""
        if not email:
            raise ValueError("Email é obrigatório")
        if not username:
            raise ValueError("Username é obrigatório")
        
        email = self.normalize_email(email)  # Domínio em lowercase
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hash PBKDF2
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Cria e retorna um superusuário"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)
```

### User Model

**Modelo customizado que herda de AbstractUser:**

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    
    REQUIRED_FIELDS = ["email"]  # Além de username (padrão)
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
```

**Campos herdados de AbstractUser:**
- `first_name`, `last_name`
- `is_staff`, `is_superuser`, `is_active`
- `date_joined`, `last_login`

**Configuração em settings.py:**
```python
AUTH_USER_MODEL = "users.User"
```

---

## Interface Web (Allauth)

### Forms

**1. CustomUserCreationForm** - Signup com campos extras

```python
class CustomUserCreationForm(FormStylingMixinLarge, SignupForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    last_name = forms.CharField(max_length=150, required=True, label="Sobrenome")
    
    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        logger.info(f"Novo usuário registrado: {user.email}")
        return user
```

**2. CustomLoginForm** - Login com username ou email

```python
class CustomLoginForm(FormStylingMixinLarge, LoginForm):
    login = forms.CharField(
        label="Usuário ou E-mail",
        widget=forms.TextInput(attrs={'placeholder': 'Seu usuário ou e-mail'})
    )
    remember = forms.BooleanField(label="Lembrar de mim", required=False)
```

**3. CustomResetPasswordForm** - Recuperação de senha

**4. CustomUserChangeForm** - Edição de perfil (sem senha)

```python
class CustomUserChangeForm(FormStylingMixin, UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        # Sem campo de senha para evitar alteração acidental
```

### Views

**EditProfileView** - Edição de perfil do usuário logado

```python
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "users/edit_profile.html"
    success_url = reverse_lazy("weddings:my_weddings")
    
    def get_object(self, queryset=None):
        return self.request.user  # Sempre edita o próprio perfil
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "form_layout_dict": {"username": "col-md-6", "email": "col-md-6", ...},
            "form_icons": {"username": "fa-user", "email": "fa-envelope", ...},
            "action": self.request.path,
            "button_text": "Salvar Alterações"
        })
        return context
```

### Allauth Views Customizadas

**Sobrescrevem as views padrão para adicionar contexto:**

```python
class CustomSignupView(SignupView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout_dict"] = {"username": "col-md-6", "email": "col-md-6"}
        context["form_icons"] = {"username": "fa-user", "email": "fa-envelope"}
        context["button_text"] = "Cadastrar"
        return context
```

### Configuração Allauth (settings.py)

```python
INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',  # Para OAuth futuro
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Configurações Allauth
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Aceita ambos
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Sem verificação de email
ACCOUNT_LOGOUT_ON_GET = False  # Confirmação antes de logout

ACCOUNT_FORMS = {
    'signup': 'apps.users.web.forms.CustomUserCreationForm',
    'login': 'apps.users.web.forms.CustomLoginForm',
    'reset_password': 'apps.users.web.forms.CustomResetPasswordForm',
}

ACCOUNT_ADAPTER = 'apps.users.web.adapters.CustomAccountAdapter'
```

---

## Interface API (DRF)

### Serializers

**1. UserSerializer** - CRUD completo

```python
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'password', 'password_confirm']
        read_only_fields = ['id']
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise ValidationError("Senhas não coincidem")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
```

**2. UserListSerializer** - Listagem otimizada

```python
class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']
    
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username
```

**3. UserDetailSerializer** - Detalhes completos

```python
class UserDetailSerializer(serializers.ModelSerializer):
    weddings_count = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'date_joined', 'weddings_count', 'items_count']
    
    def get_weddings_count(self, obj):
        return obj.weddings.count()
    
    def get_items_count(self, obj):
        from apps.items.models import Item
        return Item.objects.filter(wedding__planner=obj).count()
```

**4. ChangePasswordSerializer** - Mudança de senha

```python
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Senha atual incorreta")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise ValidationError("Novas senhas não coincidem")
        return attrs
```

### ViewSet

**UserViewSet** - CRUD completo + custom action

```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        Endpoint: POST /api/v1/users/{id}/change-password/
        Body: {old_password, new_password, confirm_password}
        """
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            logger.info(f"Senha alterada para usuário: {user.email}")
            return Response({"status": "Senha alterada com sucesso"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Endpoints API

```
GET    /api/v1/users/              - Lista usuários
POST   /api/v1/users/              - Cria usuário
GET    /api/v1/users/{id}/         - Detalhes do usuário
PUT    /api/v1/users/{id}/         - Atualiza completo
PATCH  /api/v1/users/{id}/         - Atualiza parcial
DELETE /api/v1/users/{id}/         - Deleta usuário
POST   /api/v1/users/{id}/change-password/ - Muda senha
```

---

## Segurança

### Model Level

- ✅ **Email único:** Constraint no banco
- ✅ **Username único:** Constraint no banco
- ✅ **Senha hasheada:** PBKDF2 com salt (Django default)
- ✅ **Normalização:** Domínio do email em lowercase
- ✅ **Validação de comprimento:** username ≤ 255 caracteres

### View Level (Web)

- ✅ **LoginRequiredMixin:** EditProfileView protegida
- ✅ **CSRF Protection:** Todos os forms protegidos
- ✅ **Rate Limiting:** Allauth pode limitar tentativas de login
- ✅ **Session Security:** Session cookie HttpOnly e Secure

### API Level

- ✅ **IsAuthenticated:** Permission em todos os endpoints
- ✅ **Password write_only:** Não retornado em responses
- ✅ **Old password validation:** Obrigatório em change_password
- ✅ **Hashing automático:** set_password() sempre usado

---

## Testes

### Estrutura (36 testes)

**test_models.py (13 testes):**
- UserModelTest (8) - Criação, validações, normalização
- UserModelIntegrationTest (5) - Constraints únicos, max_length

**web/test_forms.py (8 testes):**
- CustomUserCreationFormTest (6) - Registro, validações
- CustomUserChangeFormTest (2) - Edição de perfil

**web/test_views.py (5 testes):**
- EditProfileViewTest (5) - Renderização, update, segurança

**web/test_urls.py (4 testes):**
- Resolução de URLs (signup, login, logout, edit_profile)

**api/test_serializers.py (6 testes):**
- UserSerializerTest (4) - Serialization, validation
- UserListSerializerTest (2) - full_name field
- UserDetailSerializerTest (1) - Counts fields
- ChangePasswordSerializerTest (2) - Validações

### Executar Testes

```bash
# Todos os testes
pytest apps/users -v

# Apenas web
pytest apps/users/tests/web -v

# Apenas API
pytest apps/users/tests/api -v

# Com cobertura
pytest apps/users --cov=apps.users --cov-report=html
```

**Status:** ✅ 36/36 passando

---

## Fluxos de Autenticação

### 1. Signup (Web)

```
[Visitante]
    → Acessa /accounts/signup/
    → Preenche CustomUserCreationForm
    ↓
[Allauth Valida]
    → Email único
    → Username único
    → Senhas coincidem
    ↓
[CustomUserManager.create_user()]
    → Normaliza email
    → Hash senha (PBKDF2)
    → Salva no banco
    ↓
[Login Automático] (opcional)
    → Session criada
    → Redirect para my_weddings
```

### 2. Login (Web)

```
[Usuário]
    → Acessa /accounts/login/
    → Username ou email + senha
    ↓
[Allauth Autentica]
    → Backend: ModelBackend + AuthenticationBackend
    → Valida credenciais
    ↓
[Session Criada]
    → Cookie sessionid
    → Redirect para LOGIN_REDIRECT_URL
```

### 3. API Authentication

```
[Cliente API]
    → POST /api/v1/users/ (criar conta)
    ↓
[UserSerializer.create()]
    → Valida dados
    → create_user() via manager
    ↓
[Login via SessionAuth]
    → POST /api/v1/auth/login/
    → Recebe session cookie
    ↓
[Requisições Subsequentes]
    → Inclui session cookie
    → IsAuthenticated valida
```

---

## Próximos Passos

### Sugerido:

1. **OAuth Social:** Google, GitHub, Facebook (via allauth.socialaccount)
2. **Two-Factor Authentication (2FA):** TOTP com django-otp
3. **Token Authentication:** JWT com djangorestframework-simplejwt
4. **Avatar de Usuário:** Upload de foto de perfil
5. **Email Verification:** Ativar ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** 2.0 - Arquitetura Híbrida (Web + API) com Django Allauth

# App: Pages

O app `pages` gerencia as páginas públicas do site, incluindo a Landing Page (home) e o formulário de contato. Fornece a interface inicial para visitantes não autenticados e captura mensagens de contato para processamento administrativo.

---

## Status Atual

**Versão:** 1.0  
**Testes:** 19 passando  
**Cobertura:** models, forms, views, urls, integração com email, validações  
**Interface:** Web (HTMX) + Email Notifications

---

## Responsabilidades

-   **Landing Page:** Página inicial pública com informações do serviço
-   **Formulário de Contato:** Captura mensagens de visitantes via HTMX
-   **Persistência:** Salva mensagens no banco (modelo `ContactInquiry`)
-   **Notificações:** Envia email para administrador quando houver nova mensagem
-   **Redirecionamento:** Usuários autenticados são redirecionados automaticamente

---

## Arquitetura

### Padrões Aplicados
- **HTMX First:** Formulário de contato via AJAX sem page reload
- **Graceful Degradation:** Erros de email não quebram experiência do usuário
- **Security:** Validação de dados + logging de tentativas suspeitas
- **User Experience:** HTTP 200 (sucesso) vs 400 (erro) para feedback HTMX
- **Admin Workflow:** Mensagens com flag `read` para controle no admin

---

## Estrutura de Arquivos

### Models (`models.py`)

-   **`ContactInquiry` (BaseModel):**
    - **Campos:**
        - `name` (CharField, max 100) - Nome do visitante
        - `email` (EmailField) - Email para contato
        - `message` (TextField) - Mensagem enviada
        - `read` (BooleanField, default False) - Status de leitura
        - `created_at`, `updated_at` (herdados de BaseModel)
    - **Meta:**
        - `ordering = ("-created_at")` - Mais recentes primeiro
        - `verbose_name_plural` - "Mensagens de Contato"
    - **Métodos:**
        - `__str__()` - "Mensagem de {name} ({email})"
        - `mark_as_read()` - Helper para marcar como lida

### Forms (`forms.py`)

-   **`ContactForm` (FormStylingMixin + ModelForm):**
    - **Campos:** name, email, message
    - **Validações:**
        - Campos obrigatórios (required=True)
        - Email válido (EmailField)
        - Logging automático de erros (via clean())
    - **UX:**
        - Placeholders dinâmicos (via `add_placeholder`)
        - Textarea com 5 rows para mensagem
        - Bootstrap styling (via FormStylingMixin)

### Views (`views.py`)

-   **`HomeView` (RedirectAuthenticatedUserMixin + TemplateView):**
    - **Template:** `pages/home.html`
    - **Comportamento:**
        - Usuário anônimo → Renderiza Landing Page
        - Usuário autenticado → Redireciona para `weddings:my_weddings`
    - **Contexto:**
        - `contact_form` - Instância do ContactForm
        - `form_icons` - Dicionário de ícones FontAwesome por campo

-   **`ContactFormSubmitView` (View):**
    - **Método:** POST apenas (GET retorna 405)
    - **Fluxo de Sucesso (HTTP 200):**
        1. Valida formulário
        2. Salva no banco (`ContactInquiry`)
        3. Envia email para admin
        4. Retorna `_contact_success.html` (template HTMX)
    - **Fluxo de Erro (HTTP 400):**
        1. Retorna `_contact_form_partial.html` com erros
        2. Reinjeta `form_icons` no contexto
        3. Status 400 para sinalizar erro ao HTMX
    - **Tratamento de Erro de Email:**
        - Falha no envio de email NÃO quebra o fluxo
        - Erro é logado (via logger.error)
        - Usuário recebe sucesso normalmente
        - Admin investiga via logs

### URLs (`urls.py`)

-   **Namespace:** `pages`
-   **Rotas:**
    - `/` - HomeView (name: `home`)
    - `/contact-submit/` - ContactFormSubmitView (name: `contact_submit`)

### Admin (`admin.py`)

-   **Status:** Vazio (não implementado)
-   **Sugestão Futura:** Implementar admin para gerenciar mensagens
    - List display: name, email, created_at, read
    - List filter: read, created_at
    - Actions: mark_as_read, mark_as_unread
    - Search: name, email, message

---

## Testes (`tests/`)

### `test_models.py` (5 testes)
- ✅ **test_create_valid_inquiry** - Criação básica e __str__
- ✅ **test_ordering_latest_first** - Ordenação por created_at DESC
- ✅ **test_name_max_length_validation** - Rejeita nome > 100 chars
- ✅ **test_mark_as_read_method** - Helper marca como lida
- ✅ **test_invalid_email_format** - Validação de email inválido

### `test_forms.py` (6 testes)
- ✅ **test_form_valid_data** - Dados válidos passam
- ✅ **test_form_invalid_missing_required_fields** - Todos campos obrigatórios
- ✅ **test_form_invalid_email_format** - Email inválido falha
- ✅ **test_widgets_and_placeholders** - Placeholders e textarea rows=5
- ✅ **test_logging_on_error** - Logger é chamado em erro
- ✅ **test_form_save_creates_model_instance** - Integração: save() cria no banco

### `test_views.py` (6 testes)
- ✅ **HomeView:**
    - test_get_renders_home_template - Anônimo vê landing page
    - test_authenticated_user_redirects_to_dashboard - Logado é redirecionado
- ✅ **ContactFormSubmitView:**
    - test_post_valid_saves_db_and_sends_email - Sucesso completo (DB + email)
    - test_post_invalid_returns_400_and_form_errors - Erro retorna form com erros
    - test_email_failure_is_handled_gracefully - Falha de email não quebra
    - test_get_request_returns_405 - GET não permitido

### `test_urls.py` (2 testes)
- ✅ **test_home_url_resolves** - URL "/" resolve para HomeView
- ✅ **test_contact_submit_url_resolves** - URL "/contact-submit/" resolve

**Total:** 19 testes passando ✅

---

## Templates (`templates/pages/`)

### Estrutura:
```
pages/
├── home.html                           # Landing Page principal
├── emails/
│   └── contact_notification.txt       # Template de email (plaintext)
└── partials/
    └── home/
        ├── _contact_form_partial.html  # Formulário HTMX
        └── _contact_success.html       # Mensagem de sucesso HTMX
```

### Integração HTMX:
```html
<!-- Em home.html -->
<form hx-post="{% url 'pages:contact_submit' %}"
      hx-target="#contact-container"
      hx-swap="innerHTML">
  <!-- Campos do formulário -->
</form>
```

**Comportamento:**
- Sucesso (200) → Swap para `_contact_success.html`
- Erro (400) → Swap para `_contact_form_partial.html` com erros

---

## Fluxo de Dados: Formulário de Contato

```
[Visitante] 
    → Preenche formulário na Landing Page
    → Clica em "Enviar" (HTMX POST)
         ↓
[ContactFormSubmitView]
    → Valida dados
    → Cria ContactInquiry no banco
    → Envia email para admin
         ↓
[Sucesso]
    → HTTP 200
    → Retorna _contact_success.html
    → HTMX atualiza container (sem page reload)
         ↓
[Admin]
    → Recebe email no inbox
    → (Futuro) Acessa Django Admin para ler/gerenciar mensagens
```

---

## Segurança

- **CSRF Protection:** Formulário Django protegido automaticamente
- **Email Validation:** Django EmailField valida formato
- **Max Length:** Nome limitado a 100 caracteres
- **Logging:** Erros de validação são logados para monitoramento
- **Graceful Failure:** Falha de email não expõe erro ao usuário
- **XSS Protection:** Django auto-escaping nos templates

---

## Email Configuration

### Settings Required:
```python
# settings/base.py ou local.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-app'
DEFAULT_FROM_EMAIL = 'noreply@seusite.com'
ADMIN_EMAIL = 'admin@seusite.com'
```

### Template de Email:
```
Nova Mensagem de Contato

Nome: {{ name }}
Email: {{ email }}
Data: {{ created_at }}

Mensagem:
{{ message }}
```

---

## Performance

- **Queries otimizadas:** Apenas 1 INSERT por mensagem
- **Email assíncrono (futuro):** Considerar Celery para envio em background
- **Sem N+1:** View não faz queries adicionais
- **HTMX:** Reduz carga de página (apenas swap de container)

---

## Melhorias Recentes (v1.0)

### Implementado:
1. ✅ Modelo `ContactInquiry` com campo `read`
2. ✅ Formulário com placeholders e styling Bootstrap
3. ✅ View HTMX com HTTP 200/400 para feedback
4. ✅ Envio de email com tratamento gracioso de erro
5. ✅ Logging completo de validações e erros
6. ✅ Redirecionamento automático de usuários autenticados
7. ✅ 19 testes cobrindo models, forms, views, integração

---

## Melhorias Futuras (Considerando)

### Curto Prazo:
1. **Django Admin para ContactInquiry:**
   - List display com filtros
   - Actions para marcar como lido/não lido
   - Busca por nome/email
   - Date hierarchy por created_at

2. **Envio de email assíncrono:**
   - Integrar com Celery
   - Evitar delay no response para o usuário

3. **Email HTML:**
   - Template HTML + plaintext fallback
   - Melhor formatação visual

### Longo Prazo:
1. **Analytics:** Tracking de conversões do formulário
2. **Captcha:** Proteção contra spam (Google reCAPTCHA)
3. **Auto-reply:** Email de confirmação para o visitante
4. **Webhooks:** Notificar Slack/Discord quando houver nova mensagem

---

## Dependências

### Apps Relacionados:
- **`apps.core.mixins.auth`:** `RedirectAuthenticatedUserMixin`
- **`apps.core.mixins.forms`:** `FormStylingMixin`
- **`apps.core.utils.forms_utils`:** `add_placeholder`
- **`apps.users`:** User model (para redirecionamento)

### Bibliotecas Externas:
- Django Core Mail (email)
- Django Forms (validação)
- HTMX (frontend - via CDN)

---

## Exemplos de Uso

### 1. Acessar Landing Page:
```bash
# URL: http://localhost:8000/
# Resultado: Renderiza home.html com formulário de contato
```

### 2. Enviar mensagem via HTMX:
```javascript
// Frontend (HTMX automático)
// POST /contact-submit/
// Data: {name: "João", email: "joao@test.com", message: "Olá"}
// Response: HTML fragment (_contact_success.html ou _contact_form_partial.html)
```

### 3. Marcar mensagem como lida (Python shell):
```python
from apps.pages.models import ContactInquiry

inquiry = ContactInquiry.objects.first()
inquiry.mark_as_read()  # Atualiza read=True e salva
```

---

## Comandos Úteis

### Executar testes:
```bash
# Via pytest (recomendado)
pytest apps/pages/tests/ -v

# Teste específico
pytest apps/pages/tests/test_views.py::ContactFormSubmitViewTest -v

# Via Django
python manage.py test apps.pages
```

### Verificar mensagens no shell:
```python
python manage.py shell

from apps.pages.models import ContactInquiry

# Listar todas
ContactInquiry.objects.all()

# Não lidas
ContactInquiry.objects.filter(read=False)

# Marcar como lida
msg = ContactInquiry.objects.first()
msg.mark_as_read()
```

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** 1.0 - Landing Page + Contact Form

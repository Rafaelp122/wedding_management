# Pages - Documentação Técnica Completa

Landing page e formulário de contato com HTMX e notificações por email.

**Versão:** 1.0  
**Status:** ✅ 19 testes passando  
**Interface:** Web (HTMX) + Email Notifications  

---

## Índice

- [Visão Geral](#visão-geral)
- [Models](#models)
- [Forms](#forms)
- [Views](#views)
- [Templates & HTMX](#templates--htmx)
- [Email Notifications](#email-notifications)
- [Segurança](#segurança)
- [Testes](#testes)

---

## Visão Geral

O app `pages` gerencia as **páginas públicas do site**, incluindo a Landing Page (home) e o formulário de contato. Fornece a interface inicial para visitantes não autenticados e captura mensagens de contato.

### Responsabilidades

-   **Landing Page:** Página inicial pública com informações do serviço
-   **Formulário de Contato:** Captura mensagens de visitantes via HTMX
-   **Persistência:** Salva mensagens no banco (modelo `ContactInquiry`)
-   **Notificações:** Envia email para administrador quando houver nova mensagem
-   **Redirecionamento:** Usuários autenticados são redirecionados automaticamente

---

## Models

### ContactInquiry

**Modelo para armazenar mensagens de contato:**

```python
class ContactInquiry(BaseModel):
    """Mensagem de contato enviada pela Landing Page"""
    
    name = models.CharField(max_length=100, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    message = models.TextField(verbose_name="Mensagem")
    read = models.BooleanField(default=False, verbose_name="Lida")
    
    class Meta:
        ordering = ["-created_at"]  # Mais recentes primeiro
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
    
    def __str__(self):
        return f"Mensagem de {self.name} ({self.email})"
    
    def mark_as_read(self):
        """Helper para marcar mensagem como lida"""
        self.read = True
        self.save(update_fields=['read', 'updated_at'])
```

**Campos herdados de BaseModel:**
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

---

## Forms

### ContactForm

**Formulário de contato com validações:**

```python
class ContactForm(FormStylingMixin, forms.ModelForm):
    """Formulário HTMX para captura de mensagens"""
    
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona placeholders
        add_placeholder(self.fields['name'], 'Seu nome completo')
        add_placeholder(self.fields['email'], 'seu@email.com')
        add_placeholder(self.fields['message'], 'Sua mensagem...')
    
    def clean(self):
        """Logging de erros de validação"""
        cleaned_data = super().clean()
        if self.errors:
            logger.warning(f"Erro no formulário de contato: {self.errors}")
        return cleaned_data
```

**Validações:**
- Nome: obrigatório, máximo 100 caracteres
- Email: obrigatório, formato válido
- Mensagem: obrigatório, sem limite de caracteres

---

## Views

### HomeView

**Landing page com redirecionamento condicional:**

```python
class HomeView(RedirectAuthenticatedUserMixin, TemplateView):
    """
    Landing Page pública.
    Usuários autenticados são redirecionados para dashboard.
    """
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_form'] = ContactForm()
        context['form_icons'] = {
            'name': 'fas fa-user',
            'email': 'fas fa-envelope',
            'message': 'fas fa-comment-dots',
        }
        return context
```

**Comportamento:**
- **Usuário anônimo:** Renderiza landing page com formulário
- **Usuário autenticado:** Redireciona para `weddings:my_weddings`

### ContactFormSubmitView

**Endpoint HTMX para processar formulário:**

```python
class ContactFormSubmitView(View):
    """
    Processa formulário de contato via HTMX POST.
    GET não é permitido (retorna 405).
    """
    
    def get(self, request):
        return HttpResponse("Method not allowed", status=405)
    
    def post(self, request):
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # 1. Salva no banco
            inquiry = form.save()
            logger.info(f"Nova mensagem de contato: {inquiry}")
            
            # 2. Envia email para admin
            try:
                self._send_notification_email(inquiry)
            except Exception as e:
                # Erro de email NÃO quebra o fluxo
                logger.error(f"Falha ao enviar email: {e}")
            
            # 3. Retorna sucesso (HTTP 200)
            return render(
                request,
                'pages/partials/home/_contact_success.html',
                status=200
            )
        
        # 4. Retorna erros (HTTP 400)
        return render(
            request,
            'pages/partials/home/_contact_form_partial.html',
            {
                'contact_form': form,
                'form_icons': {
                    'name': 'fas fa-user',
                    'email': 'fas fa-envelope',
                    'message': 'fas fa-comment-dots',
                }
            },
            status=400
        )
    
    def _send_notification_email(self, inquiry):
        """Envia email para admin com detalhes da mensagem"""
        subject = f"Nova mensagem de contato: {inquiry.name}"
        message = render_to_string('pages/emails/contact_notification.txt', {
            'name': inquiry.name,
            'email': inquiry.email,
            'message': inquiry.message,
            'created_at': inquiry.created_at,
        })
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False  # Lança exceção se falhar
        )
        
        logger.info(f"Email enviado para {settings.ADMIN_EMAIL}")
```

---

## Templates & HTMX

### Estrutura de Templates

```
pages/
├── home.html                           # Landing Page principal
├── emails/
│   └── contact_notification.txt       # Template de email
└── partials/
    └── home/
        ├── _contact_form_partial.html  # Formulário HTMX
        └── _contact_success.html       # Mensagem de sucesso
```

### Integração HTMX

**home.html:**
```html
<div id="contact-container">
  <form hx-post="{% url 'pages:contact_submit' %}"
        hx-target="#contact-container"
        hx-swap="innerHTML"
        class="contact-form">
    {% csrf_token %}
    
    <!-- Campos do formulário -->
    {% for field in contact_form %}
      <div class="form-group">
        <i class="{{ form_icons|get_icon_class:field.name }}"></i>
        {{ field }}
        {% if field.errors %}
          <div class="invalid-feedback">{{ field.errors.0 }}</div>
        {% endif %}
      </div>
    {% endfor %}
    
    <button type="submit" class="btn btn-primary">
      Enviar Mensagem
    </button>
  </form>
</div>
```

**Comportamento HTMX:**
1. **Usuário preenche e envia**
2. **HTMX faz POST** para `/contact-submit/`
3. **Sucesso (200):** Swap container com `_contact_success.html`
4. **Erro (400):** Swap container com `_contact_form_partial.html` (mostra erros)

---

## Email Notifications

### Template de Email

**emails/contact_notification.txt:**
```
Nova Mensagem de Contato

Nome: {{ name }}
Email: {{ email }}
Data: {{ created_at|date:"d/m/Y H:i" }}

Mensagem:
{{ message }}

---
Esta mensagem foi enviada através do formulário de contato do Wedding Management System.
```

### Configuração de Email (settings.py)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-app'
DEFAULT_FROM_EMAIL = 'noreply@weddingmanagement.com'
ADMIN_EMAIL = 'admin@weddingmanagement.com'
```

**Tratamento de Erro:**
- Falha no envio de email **NÃO quebra** a experiência do usuário
- Erro é logado via `logger.error()`
- Usuário ainda recebe mensagem de sucesso
- Admin investiga via logs

---

## Segurança

### Validações

- ✅ **CSRF Protection:** Formulário Django protegido automaticamente
- ✅ **Email Validation:** Django EmailField valida formato
- ✅ **Max Length:** Nome limitado a 100 caracteres
- ✅ **Required Fields:** Todos os campos obrigatórios
- ✅ **XSS Protection:** Django auto-escaping em templates

### Logging

```python
# Logging de erros de validação
logger.warning(f"Erro no formulário de contato: {form.errors}")

# Logging de mensagens criadas
logger.info(f"Nova mensagem de contato: {inquiry}")

# Logging de emails enviados
logger.info(f"Email enviado para {settings.ADMIN_EMAIL}")

# Logging de erros de email
logger.error(f"Falha ao enviar email: {e}")
```

---

## Testes

### Estrutura (19 testes)

**test_models.py (5 testes):**
- Criação e __str__
- Ordenação (mais recentes primeiro)
- Validação de max_length
- Helper mark_as_read()
- Validação de email inválido

**test_forms.py (6 testes):**
- Dados válidos
- Campos obrigatórios
- Email inválido
- Widgets e placeholders
- Logging de erros
- Integração: save() cria no banco

**test_views.py (6 testes):**
- **HomeView (2):**
  - Anônimo vê landing page
  - Autenticado é redirecionado
- **ContactFormSubmitView (4):**
  - POST válido salva DB + envia email (200)
  - POST inválido retorna form com erros (400)
  - Falha de email não quebra fluxo
  - GET retorna 405

**test_urls.py (2 testes):**
- Resolução de URLs (home, contact_submit)

### Executar Testes

```bash
# Todos os testes
pytest apps/pages -v

# Teste específico
pytest apps/pages/tests/test_views.py::ContactFormSubmitViewTest -v

# Com coverage
pytest apps/pages --cov=apps.pages --cov-report=html
```

**Status:** ✅ 19/19 passando

---

## Fluxo Completo

```
[Visitante]
    → Acessa http://localhost:8000/ (HomeView)
    → Vê landing page com formulário
    ↓
[Preenche Formulário]
    → Nome: João Silva
    → Email: joao@test.com
    → Mensagem: Gostaria de mais informações
    ↓
[Clica em "Enviar" - HTMX POST]
    → POST /contact-submit/
    ↓
[ContactFormSubmitView]
    → Valida dados
    → Cria ContactInquiry no banco
    → Envia email para admin@weddingmanagement.com
    ↓
[HTTP 200 - Sucesso]
    → HTMX swap container
    → Mostra mensagem: "Obrigado! Em breve entraremos em contato."
    ↓
[Admin]
    → Recebe email no inbox
    → (Futuro) Acessa Django Admin para ler/gerenciar
```

---

## Melhorias Futuras

### Curto Prazo:

1. **Django Admin para ContactInquiry:**
   - List display: name, email, created_at, read
   - List filter: read, created_at
   - Actions: mark_as_read, mark_as_unread
   - Search: name, email, message

2. **Email Assíncrono:**
   - Integrar com Celery
   - Evitar delay no response

3. **Email HTML:**
   - Template HTML + plaintext fallback
   - Melhor formatação visual

### Longo Prazo:

1. **Google reCAPTCHA:** Proteção contra spam
2. **Auto-reply:** Email de confirmação para visitante
3. **Webhooks:** Notificar Slack/Discord
4. **Analytics:** Tracking de conversões

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** 1.0 - Landing Page + Contact Form

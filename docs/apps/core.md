# Core - Documentação Técnica Completa

Biblioteca interna de componentes compartilhados e reutilizáveis.

**Versão:** Atual (Contínuo)  
**Status:** ✅ 34 testes passando  
**Tipo:** Shared Components / Biblioteca Interna  

---

## Índice

- [Visão Geral](#visão-geral)
- [Mixins](#mixins)
- [Models](#models)
- [Utilitários](#utilitários)
- [Template Tags](#template-tags)
- [Tasks Celery](#tasks-celery)
- [Constantes](#constantes)
- [Testes](#testes)

---

## Visão Geral

O app `core` é o **alicerce compartilhado** do projeto, fornecendo funcionalidades reutilizáveis que eliminam duplicação de código seguindo o princípio DRY (Don't Repeat Yourself).

### Filosofia

> **"Escreva uma vez, use em qualquer lugar"**

O Core encapsula padrões comuns em componentes testados e documentados, reduzindo bugs e facilitando manutenção.

### Responsabilidades

-   **Mixins Reutilizáveis:** Auth, Forms, Views
-   **Models Base:** Timestamps automáticos
-   **Utilitários:** Helpers para forms e HTML
-   **Template Tags:** Lógica de apresentação encapsulada
-   **Tasks Celery:** Processamento assíncrono
-   **Constantes:** Configurações globais

---

## Mixins

### Auth Mixins (`mixins/auth.py`)

**1. OwnerRequiredMixin**

**Garante que usuários só acessem seus próprios recursos:**

```python
class OwnerRequiredMixin(LoginRequiredMixin):
    """
    Filtra queryset por ownership.
    
    Attributes:
        owner_field_name (str): Nome do campo que identifica o dono (ex: 'planner', 'user')
    
    Raises:
        ImproperlyConfigured: Se owner_field_name não for definido
    
    Example:
        class MyUpdateView(OwnerRequiredMixin, UpdateView):
            model = Wedding
            owner_field_name = 'planner'  # Filtra por wedding.planner == request.user
    """
    owner_field_name: Optional[str] = None
    
    def get_queryset(self):
        if self.owner_field_name is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requer 'owner_field_name'"
            )
        
        queryset = super().get_queryset()
        filter_kwargs = {self.owner_field_name: self.request.user}
        return queryset.filter(**filter_kwargs)
```

**Uso:**
```python
# Em apps.weddings.views
class WeddingUpdateView(OwnerRequiredMixin, UpdateView):
    model = Wedding
    owner_field_name = 'planner'
    # Automaticamente filtra: Wedding.objects.filter(planner=request.user)
```

**2. RedirectAuthenticatedUserMixin**

**Redireciona usuários já autenticados de páginas públicas:**

```python
class RedirectAuthenticatedUserMixin:
    """
    Redireciona usuários autenticados para dashboard.
    
    Useful para páginas de login/signup onde usuários já logados
    não precisam estar.
    
    Attributes:
        redirect_url (str): URL de destino (default: 'weddings:my_weddings')
        redirect_message (str): Mensagem de boas-vindas (default: auto-gerada)
    
    Example:
        class HomeView(RedirectAuthenticatedUserMixin, TemplateView):
            redirect_url = 'dashboard'
    """
    redirect_url: str = "weddings:my_weddings"
    redirect_message: Optional[str] = None
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if self.redirect_message is None:
                name = request.user.first_name or request.user.username
                self.redirect_message = f"Bem-vindo de volta, {name}!"
            
            messages.info(request, self.redirect_message)
            return redirect(self.redirect_url)
        
        return super().dispatch(request, *args, **kwargs)
```

**Uso:**
```python
# Em apps.pages.views
class HomeView(RedirectAuthenticatedUserMixin, TemplateView):
    template_name = 'pages/home.html'
    # Usuário logado → redirect para my_weddings
    # Usuário anônimo → renderiza landing page
```

### Form Mixins (`mixins/forms.py`)

**1. BaseFormStylingMixin**

**Classe base parametrizável (não usar diretamente):**

```python
class BaseFormStylingMixin:
    """
    Base para mixins de estilização de formulários.
    Não usar diretamente, usar subclasses.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            current_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{current_classes} {self.get_base_classes()}".strip()
    
    def get_base_classes(self) -> str:
        """Subclasses devem sobrescrever"""
        raise NotImplementedError
    
    def _add_error_class(self, field):
        """Adiciona 'is-invalid' se campo tem erro"""
        if field in self.errors:
            current = self.fields[field].widget.attrs.get("class", "")
            self.fields[field].widget.attrs["class"] = f"{current} is-invalid".strip()
```

**2. FormStylingMixin**

**Estilização Bootstrap padrão:**

```python
class FormStylingMixin(BaseFormStylingMixin):
    """
    Aplica classes Bootstrap padrão (form-control).
    
    Classes aplicadas:
        - form-control
        - is-invalid (se houver erro após validação)
    
    Example:
        class ContactForm(FormStylingMixin, forms.ModelForm):
            class Meta:
                model = ContactInquiry
                fields = ['name', 'email', 'message']
    """
    def get_base_classes(self) -> str:
        return "form-control"
```

**3. FormStylingMixinLarge**

**Estilização Bootstrap large (para destaque):**

```python
class FormStylingMixinLarge(BaseFormStylingMixin):
    """
    Aplica classes Bootstrap large (form-control-lg).
    
    Classes aplicadas:
        - form-control
        - form-control-lg
        - is-invalid (se houver erro após validação)
    
    Ideal para: formulários de login/signup, campos destacados.
    
    Example:
        class LoginForm(FormStylingMixinLarge, forms.Form):
            username = forms.CharField()
            password = forms.CharField(widget=forms.PasswordInput())
    """
    def get_base_classes(self) -> str:
        return "form-control form-control-lg"
```

### View Mixins (`mixins/views.py`)

**1. HtmxUrlParamsMixin**

**Extrai parâmetros da query string do header HTMX:**

```python
class HtmxUrlParamsMixin:
    """
    Extrai parâmetros do header HX-Current-Url.
    
    Útil para preservar estado de filtros/paginação em requests HTMX.
    
    Methods:
        _get_params_from_htmx_url() -> Dict[str, str]
    
    Example:
        class MyListView(HtmxUrlParamsMixin, ListView):
            def get_queryset(self):
                params = self._get_params_from_htmx_url()
                search = params.get('q', '')
                return MyModel.objects.filter(name__icontains=search)
    """
    def _get_params_from_htmx_url(self) -> Dict[str, str]:
        """
        Extrai query params do header HX-Current-Url.
        
        Returns:
            Dict com parâmetros (ex: {'q': 'busca', 'page': '2'})
            Dict vazio se header não existir
        """
        hx_current_url = self.request.headers.get("HX-Current-Url", "")
        
        if not hx_current_url:
            return {}
        
        try:
            parsed = urlparse(hx_current_url)
            params = parse_qs(parsed.query)
            # parse_qs retorna listas, pegar primeiro valor
            return {k: v[0] for k, v in params.items()}
        except Exception as e:
            logger.warning(f"Erro ao parsear HX-Current-Url: {e}")
            return {}
```

**2. BaseHtmxResponseMixin**

**Facilita renderização de respostas HTMX:**

```python
class BaseHtmxResponseMixin:
    """
    Base para views que retornam respostas HTMX.
    
    Attributes:
        htmx_template_name (str): Template parcial HTMX
        htmx_retarget_id (str): ID do elemento alvo (ex: '#content')
        htmx_swap_method (str): Método de swap (default: 'innerHTML')
    
    Methods:
        render_htmx_response(trigger=None, **kwargs) -> HttpResponse
    
    Example:
        class MyPartialView(BaseHtmxResponseMixin, TemplateView):
            htmx_template_name = 'partials/_list.html'
            htmx_retarget_id = '#content'
            
            def get(self, request):
                context = {'items': Item.objects.all()}
                return self.render_htmx_response(**context)
    """
    htmx_template_name: Optional[str] = None
    htmx_retarget_id: Optional[str] = None
    htmx_swap_method: str = "innerHTML"
    
    def render_htmx_response(
        self, 
        trigger: Optional[str] = None, 
        **kwargs
    ) -> HttpResponse:
        """
        Renderiza resposta HTMX com headers corretos.
        
        Args:
            trigger: Evento HTMX para disparar (ex: 'itemAdded')
            **kwargs: Contexto adicional para o template
        
        Returns:
            HttpResponse com headers HTMX configurados
        
        Raises:
            ImproperlyConfigured: Se atributos obrigatórios faltarem
        """
        if not self.htmx_template_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requer 'htmx_template_name'"
            )
        if not self.htmx_retarget_id:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requer 'htmx_retarget_id'"
            )
        
        context = {'request': self.request}
        context.update(kwargs)
        
        response = render(self.request, self.htmx_template_name, context)
        response['HX-Retarget'] = self.htmx_retarget_id
        response['HX-Reswap'] = self.htmx_swap_method
        
        if trigger:
            response['HX-Trigger-After-Swap'] = trigger
        
        return response
```

---

## Models

### BaseModel

**Model abstrato com timestamps automáticos:**

```python
class BaseModel(models.Model):
    """
    Model abstrato para herança.
    
    Adiciona automaticamente:
        - created_at: Data/hora de criação
        - updated_at: Data/hora da última atualização
    
    Example:
        class MyModel(BaseModel):
            name = models.CharField(max_length=100)
            # Automaticamente tem created_at e updated_at
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        abstract = True  # Não cria tabela no banco
```

**Uso:**
```python
from apps.core.models import BaseModel

class Wedding(BaseModel):
    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    # created_at e updated_at são herdados
```

---

## Utilitários

### Forms Utils (`utils/forms_utils.py`)

**1. add_attr()**

```python
def add_attr(field, attr_name: str, attr_new_val: str):
    """
    Adiciona ou atualiza atributo HTML em campo de formulário.
    
    Args:
        field: Campo do formulário
        attr_name: Nome do atributo (ex: 'class', 'placeholder')
        attr_new_val: Novo valor a adicionar
    
    Example:
        add_attr(form.fields['email'], 'class', 'my-custom-class')
        # Resultado: class="form-control my-custom-class"
    """
    current = field.widget.attrs.get(attr_name, "")
    updated = f"{current} {attr_new_val}".strip()
    field.widget.attrs[attr_name] = updated
```

**2. add_placeholder()**

```python
def add_placeholder(field, placeholder_val: str):
    """
    Adiciona placeholder a campo de formulário.
    
    Args:
        field: Campo do formulário
        placeholder_val: Texto do placeholder
    
    Example:
        add_placeholder(form.fields['email'], 'seu@email.com')
    """
    add_attr(field, 'placeholder', placeholder_val)
```

---

## Template Tags

### Form Helpers (`templatetags/form_helpers.py`)

**1. get_field_class**

```django
{% load form_helpers %}

{% get_field_class field layout_dict %}
```

**Retorna classe CSS de coluna para campo:**

```python
@register.simple_tag
def get_field_class(field, layout_dict):
    """
    Retorna classe de coluna Bootstrap para campo.
    
    Args:
        field: Campo do formulário
        layout_dict: Dict com mapeamento campo → classe
    
    Returns:
        Classe CSS (ex: 'col-6', 'col-md-6')
        'col-12' se não encontrado (fallback)
    
    Example:
        layout_dict = {'name': 'col-6', 'email': 'col-6'}
        {% get_field_class field layout_dict %}
        # Retorna: 'col-6' se field.name == 'name'
    """
    if isinstance(layout_dict, dict):
        return layout_dict.get(field.name, 'col-12')
    return 'col-12'
```

**2. get_icon_class**

```django
{{ field|get_icon_class:icon_dict }}
```

**Retorna classe de ícone FontAwesome:**

```python
@register.filter
def get_icon_class(field, icon_dict):
    """
    Retorna classe de ícone para campo.
    
    Args:
        field: Campo do formulário
        icon_dict: Dict com mapeamento campo → ícone
    
    Returns:
        Classe FontAwesome (ex: 'fas fa-user')
        '' se não encontrado
    
    Example:
        icon_dict = {'name': 'fa-user', 'email': 'fa-envelope'}
        {{ field|get_icon_class:icon_dict }}
        # Retorna: 'fa-user' se field.name == 'name'
    """
    if isinstance(icon_dict, dict):
        return icon_dict.get(field.name, '')
    return ''
```

**3. is_textarea**

```django
{% if field|is_textarea %}...{% endif %}
```

**Verifica se campo é Textarea:**

```python
@register.filter
def is_textarea(field):
    """
    Verifica se campo é Textarea.
    
    Args:
        field: Campo do formulário
    
    Returns:
        True se widget for Textarea, False caso contrário
    
    Example:
        {% if field|is_textarea %}
          <small>Máximo 500 caracteres</small>
        {% endif %}
    """
    return isinstance(field.field.widget, forms.Textarea)
```

---

## Tasks Celery

### Tarefas Assíncronas (`tasks.py`)

**1. send_welcome_email**

```python
@shared_task
def send_welcome_email(user_email: str):
    """
    Envia email de boas-vindas para novo usuário.
    
    Args:
        user_email: Email do destinatário
    
    Usage:
        send_welcome_email.delay('user@example.com')
    """
    send_mail(
        subject='Bem-vindo ao Wedding Management!',
        message='Obrigado por se cadastrar...',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )
```

**2. send_reminder_emails**

```python
@shared_task
def send_reminder_emails():
    """
    Envia lembretes de eventos nas próximas 24h.
    
    Agendável via Celery Beat (diariamente às 9h).
    
    Usage (celerybeat_schedule):
        'send-reminders': {
            'task': 'apps.core.tasks.send_reminder_emails',
            'schedule': crontab(hour=9, minute=0),
        }
    """
    from apps.scheduler.models import Event
    from django.utils import timezone
    
    tomorrow = timezone.now() + timedelta(days=1)
    events = Event.objects.filter(
        start_time__date=tomorrow.date(),
        status='CONFIRMED'
    )
    
    for event in events:
        send_mail(...)
```

**3. cleanup_old_sessions**

```python
@shared_task
def cleanup_old_sessions():
    """
    Limpa sessões expiradas do banco.
    
    Agendável via Celery Beat (semanalmente).
    """
    from django.core.management import call_command
    call_command('clearsessions')
```

**4. generate_wedding_report**

```python
@shared_task
def generate_wedding_report(wedding_id: int):
    """
    Gera relatório completo de um casamento.
    
    Args:
        wedding_id: ID do casamento
    
    Returns:
        Caminho do arquivo PDF gerado
    
    Usage:
        result = generate_wedding_report.delay(123)
        pdf_path = result.get()  # Bloqueia até completar
    """
    wedding = Wedding.objects.get(pk=wedding_id)
    # Gera relatório em PDF...
    return pdf_path
```

**5. process_contract_document**

```python
@shared_task(bind=True, max_retries=3)
def process_contract_document(self, contract_id: int):
    """
    Processa documentos de contrato (PDF, assinatura).
    
    Args:
        self: Task instance (bind=True)
        contract_id: ID do contrato
    
    Retry: Máximo 3 tentativas com countdown exponencial
    
    Usage:
        process_contract_document.delay(456)
    """
    try:
        contract = Contract.objects.get(pk=contract_id)
        # Processa documento...
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---

## Constantes

### GRADIENTS (`constants.py`)

**Lista de gradientes CSS para visualizações:**

```python
GRADIENTS = [
    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",  # Roxo
    "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",  # Rosa
    "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",  # Azul
    "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",  # Verde
    "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",  # Coral
    "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",  # Teal
    "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",  # Suave
    "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",  # Laranja
]
```

**Uso:**
```python
from apps.core.constants import GRADIENTS

# Em budget.views
for i, category in enumerate(categories):
    gradient = GRADIENTS[i % len(GRADIENTS)]  # Rotaciona
```

---

## Testes

### Estrutura (34 testes)

**mixins/test_auth_mixins.py (10):**
- OwnerRequiredMixin (6) - Filtragem, segurança, configuração
- RedirectAuthenticatedUserMixin (4) - Redirect, mensagens

**mixins/test_form_mixins.py (4):**
- FormStylingMixin (2) - Classes Bootstrap, is-invalid
- FormStylingMixinLarge (2) - Classes large, is-invalid

**mixins/test_view_mixins.py (16):**
- HtmxUrlParamsMixin (8) - Extração de params, edge cases
- BaseHtmxResponseMixin (8) - Renderização, headers, configuração

**utils/test_forms_utils.py (4):**
- add_attr (3) - Criar, append, whitespace
- add_placeholder (1) - Funcionalidade

### Executar Testes

```bash
# Todos os testes
pytest apps/core -v

# Apenas mixins
pytest apps/core/tests/mixins -v

# Apenas utils
pytest apps/core/tests/utils -v

# Com cobertura
pytest apps/core --cov=apps.core --cov-report=html
```

**Status:** ✅ 34/34 passando

---

## Próximos Passos

### Sugerido:

1. **Mais Mixins:**
   - `PaginationMixin` genérico
   - `SearchMixin` genérico
   - `ExportMixin` (CSV, Excel, PDF)

2. **Mais Tasks:**
   - `send_notification` (genérico)
   - `backup_database`
   - `generate_analytics_report`

3. **Mais Utils:**
   - `date_utils.py` - Helpers de data/hora
   - `string_utils.py` - Slugify, truncate

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** Atual (Contínuo) - Base compartilhada do projeto

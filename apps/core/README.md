# App: Core

O app `core` é o **alicerce compartilhado** do projeto, fornecendo funcionalidades reutilizáveis que são utilizadas por todos os outros apps. Contém mixins, utilitários, models base, tasks do Celery, template tags e constantes globais.

---

## Status Atual

**Versão:** Atual (Contínuo)  
**Testes:** 34 passando  
**Cobertura:** mixins (auth, forms, views), utils, template tags  
**Tipo:** Biblioteca Interna / Shared Components

---

## Responsabilidades

-   **Mixins Reutilizáveis:** Componentes DRY para autenticação, formulários e views
-   **Models Base:** Modelo abstrato `BaseModel` com timestamps automáticos
-   **Utilitários:** Helpers para manipulação de formulários e atributos HTML
-   **Template Tags:** Tags customizadas para templates Django
-   **Tasks Celery:** Tarefas assíncronas e agendadas (email, relatórios, limpeza)
-   **Constantes:** Configurações globais (GRADIENTS para UI)

---

## Arquitetura

### Filosofia: DRY (Don't Repeat Yourself)
O app `core` elimina duplicação de código seguindo o princípio:
> **"Escreva uma vez, use em qualquer lugar"**

### Padrões Aplicados
- **Abstract Base Models:** Herança de timestamps sem criar tabelas
- **Mixin Pattern:** Composição de funcionalidades em views e forms
- **Utility Functions:** Funções puras e reutilizáveis
- **Template Tags:** Encapsulamento de lógica de apresentação
- **Async Tasks:** Processamento em background com Celery

---

## Estrutura de Arquivos

### 📂 Mixins (`mixins/`)

Componentes reutilizáveis para views e forms. **[Documentação detalhada](mixins/README.md)**

#### Auth Mixins (`mixins/auth.py`)
- **`OwnerRequiredMixin`:**
  - Garante que usuários só acessem seus próprios recursos
  - Filtra queryset por `owner_field_name` (ex: `planner`)
  - Herda de `LoginRequiredMixin`
  - Uso: `class MyView(OwnerRequiredMixin, UpdateView)`

- **`RedirectAuthenticatedUserMixin`:**
  - Redireciona usuários já autenticados de páginas públicas
  - Útil em login/signup para evitar re-login
  - Mensagem de boas-vindas personalizada
  - Uso: `class HomeView(RedirectAuthenticatedUserMixin, TemplateView)`

#### Form Mixins (`mixins/forms.py`)
- **`BaseFormStylingMixin`:**
  - Classe base parametrizável para estilização Bootstrap
  - Não usar diretamente, use as subclasses

- **`FormStylingMixin`:**
  - Aplica classes Bootstrap padrão (`form-control`)
  - Adiciona `is-invalid` em campos com erro
  - Uso: `class MyForm(FormStylingMixin, forms.Form)`

- **`FormStylingMixinLarge`:**
  - Versão large para formulários destacados
  - Classes: `form-control-lg` + custom font size
  - Ideal para páginas de login/registro

#### View Mixins (`mixins/views.py`)
- **`HtmxUrlParamsMixin`:**
  - Extrai parâmetros da query string do header `HX-Current-Url`
  - Útil para preservar estado de paginação/filtros em HTMX
  - Método: `_get_params_from_htmx_url() -> Dict[str, str]`

- **`BaseHtmxResponseMixin`:**
  - Facilita renderização de respostas HTMX
  - Configura headers automaticamente (HX-Retarget, HX-Reswap)
  - Método: `render_htmx_response(trigger=None, **kwargs)`
  - Requer: `htmx_template_name`, `htmx_retarget_id`

### 📦 Models (`models.py`)

-   **`BaseModel` (Abstract Model):**
    - **Campos:**
        - `created_at` (DateTimeField, auto_now_add=True)
        - `updated_at` (DateTimeField, auto_now=True)
    - **Meta:** `abstract = True` (não cria tabela)
    - **Uso:** Herdar em outros models para ter timestamps automáticos
    - **Exemplo:**
      ```python
      from apps.core.models import BaseModel
      
      class MyModel(BaseModel):
          name = models.CharField(max_length=100)
          # Automaticamente tem created_at e updated_at
      ```

### 🛠 Utilitários (`utils/`)

#### Forms Utils (`utils/forms_utils.py`)
-   **`add_attr(field, attr_name, attr_new_val)`:**
    - Adiciona ou atualiza atributo HTML em campo de formulário
    - Exemplo: `add_attr(field, 'class', 'my-class')`

-   **`add_placeholder(field, placeholder_val)`:**
    - Adiciona placeholder a campo de formulário
    - Wrapper de `add_attr` para facilitar uso
    - Exemplo: `add_placeholder(form.fields['email'], 'seu@email.com')`

### 🏷️ Template Tags (`templatetags/`)

#### Form Helpers (`templatetags/form_helpers.py`)
-   **`{% get_field_class field layout_dict %}`:**
    - Retorna classe CSS de coluna para campo (ex: `col-6`)
    - Fallback: `col-12` se não encontrado no layout_dict

-   **`{{ field|get_icon_class:icon_dict }}`:**
    - Retorna classe de ícone FontAwesome para campo
    - Exemplo: `fas fa-user` para campo `name`

-   **`{{ field|is_textarea }}`:**
    - Verifica se campo é Textarea (para estilização condicional)
    - Uso: `{% if field|is_textarea %}...{% endif %}`

### ⚙️ Tasks Celery (`tasks.py`)

Tarefas assíncronas para processamento em background:

-   **`send_welcome_email(user_email)`:**
    - Envia email de boas-vindas para novos usuários
    - Shared task (pode ser chamado de qualquer app)

-   **`send_reminder_emails()`:**
    - Envia lembretes de eventos futuros (próximas 24h)
    - Agendável via Celery Beat (diariamente às 9h)

-   **`cleanup_old_sessions()`:**
    - Limpa sessões expiradas do banco
    - Agendável via Celery Beat (semanalmente)

-   **`generate_wedding_report(wedding_id)`:**
    - Gera relatório completo de um casamento
    - Útil para exportação/auditoria

-   **`process_contract_document(contract_id)`:**
    - Processa documentos de contrato (PDF, assinatura)
    - Com retry automático (max 3 tentativas)

**Configuração Celery Beat:**
```python
# Em settings/base.py ou celery.py
CELERY_BEAT_SCHEDULE = {
    'send-reminder-emails-every-day': {
        'task': 'apps.core.tasks.send_reminder_emails',
        'schedule': crontab(hour=9, minute=0),  # 9h diariamente
    },
    'cleanup-sessions-weekly': {
        'task': 'apps.core.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),  # Domingos
    },
}
```

### 🎨 Constantes (`constants.py`)

-   **`GRADIENTS`:**
    - Lista de 8 gradientes CSS para visualizações coloridas
    - Usado em budget (categorias), dashboard, etc.
    - Cores: Roxo, Índigo, Rosa, Azul, Coral, Teal, Laranja
    - Rotaciona automaticamente se houver mais de 8 categorias

---

## Testes (`tests/`)

### Mixins (`tests/mixins/`)

#### `test_auth_mixins.py` (10 testes)
- ✅ **OwnerRequiredMixin (6 testes):**
  - Filtra queryset por owner
  - Herança de LoginRequiredMixin
  - ImproperlyConfigured se faltarem atributos
  - Integração: isolamento de dados por usuário
  - Usuário anônimo → 302 redirect
  - Lista vazia se usuário não tem recursos

- ✅ **RedirectAuthenticatedUserMixin (4 testes):**
  - Usuário anônimo acessa normalmente
  - Usuário autenticado → redirect
  - Mensagem usa first_name se disponível
  - Fallback para username se first_name vazio

#### `test_form_mixins.py` (4 testes)
- ✅ **FormStylingMixin (2 testes):**
  - Aplica classes Bootstrap padrão
  - Adiciona `is-invalid` após validação com erro

- ✅ **FormStylingMixinLarge (2 testes):**
  - Aplica classes Bootstrap large
  - Adiciona `is-invalid` após validação com erro

#### `test_view_mixins.py` (16 testes)
- ✅ **HtmxUrlParamsMixin (8 testes):**
  - Extrai parâmetros do header HX-Current-Url
  - Retorna dict vazio se header ausente
  - Lida com valores vazios e caracteres encoded
  - Log de warning em caso de exceção
  - Suporta chaves duplicadas (pega primeiro valor)

- ✅ **BaseHtmxResponseMixin (8 testes):**
  - Injeta request no contexto automaticamente
  - Passa kwargs customizados para template
  - Renderiza com headers HTMX corretos
  - Suporta swap method customizado (innerHTML, outerHTML)
  - Suporta trigger customizado (HX-Trigger-After-Swap)
  - ImproperlyConfigured se faltarem atributos

### Utils (`tests/utils/`)

#### `test_forms_utils.py` (4 testes)
- ✅ **add_attr:**
  - Cria novo atributo se não existir
  - Appenda a atributo existente (preservando anterior)
  - Remove whitespace extra

- ✅ **add_placeholder:**
  - Adiciona placeholder corretamente

**Total:** 34 testes passando ✅

---

## Dependências

### Apps que Usam Core:
- ✅ **weddings** - Usa OwnerRequiredMixin, BaseModel, GRADIENTS
- ✅ **items** - Usa BaseModel, mixins de view e form
- ✅ **scheduler** - Usa BaseModel, mixins de view, tasks de reminder
- ✅ **budget** - Usa GRADIENTS para visualização
- ✅ **pages** - Usa RedirectAuthenticatedUserMixin, FormStylingMixin
- ✅ **contracts** - Usa BaseModel, tasks de processamento
- ✅ **users** - Usa tasks de welcome email

### Bibliotecas Externas:
- Django 5.2
- Celery 5.4
- Redis 7 (broker do Celery)

---

## Exemplos de Uso

### 1. Usar BaseModel em novo modelo:
```python
from apps.core.models import BaseModel

class MyModel(BaseModel):
    name = models.CharField(max_length=100)
    # created_at e updated_at são herdados automaticamente
```

### 2. Aplicar mixins em view:
```python
from apps.core.mixins import OwnerRequiredMixin, BaseHtmxResponseMixin
from django.views.generic import UpdateView

class MyUpdateView(OwnerRequiredMixin, BaseHtmxResponseMixin, UpdateView):
    model = MyModel
    owner_field_name = 'user'
    htmx_template_name = 'partials/my_form.html'
    htmx_retarget_id = '#content'
    fields = ['name']
```

### 3. Usar utilitários em formulário:
```python
from apps.core.utils.forms_utils import add_placeholder
from apps.core.mixins import FormStylingMixin

class MyForm(FormStylingMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_placeholder(self.fields['email'], 'seu@email.com')
```

### 4. Chamar task Celery:
```python
from apps.core.tasks import send_welcome_email

# Síncrono (bloqueia)
send_welcome_email('user@example.com')

# Assíncrono (background)
send_welcome_email.delay('user@example.com')
```

### 5. Usar template tag:
```django
{% load form_helpers %}

{% for field in form %}
  <div class="{{ field|get_field_class:layout_dict }}">
    <i class="{{ field|get_icon_class:icon_dict }}"></i>
    {{ field }}
    {% if field|is_textarea %}
      <small>Máximo 500 caracteres</small>
    {% endif %}
  </div>
{% endfor %}
```

---

## Performance

- **Mixins:** Zero overhead, apenas composição de classes
- **BaseModel:** Timestamps automáticos no banco (não em Python)
- **Template Tags:** Cached compilation, execução rápida
- **Celery Tasks:** Processamento assíncrono não bloqueia requests
- **Utils:** Funções puras, sem side effects

---

## Melhorias Recentes

### v2.0 (21/11/2025) - Refatoração de Mixins
- ✨ Eliminada duplicação em form mixins (BaseFormStylingMixin)
- ✨ Type hints completos em todos os mixins
- ✨ Documentação expandida com exemplos de uso
- ✨ Bug fix: espaço na mensagem de boas-vindas

### v1.5 - Template Tags
- ✨ Validação de tipo (dict vs string) em get_field_class
- ✨ Template tag is_textarea para detecção de widget
- ✨ Segurança contra valores inválidos

---

## Melhorias Futuras (Considerando)

### Curto Prazo:
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
   - `string_utils.py` - Slugify, truncate, etc.

### Longo Prazo:
1. **Cache Manager:** Wrapper para Redis com helpers
2. **Audit Trail:** Middleware para log de mudanças
3. **Permission System:** Sistema de permissões granulares


---

## Comandos Úteis

### Executar testes:
```bash
# Via pytest (recomendado)
pytest apps/core/tests/ -v

# Testes específicos
pytest apps/core/tests/mixins/ -v
pytest apps/core/tests/utils/ -v

# Com coverage
pytest apps/core/tests/ --cov=apps.core --cov-report=html
```

### Testar tasks Celery:
```bash
# Python shell
python manage.py shell

from apps.core.tasks import send_welcome_email
send_welcome_email.delay('test@example.com')
```

### Verificar Celery Beat:
```bash
# Ver tasks agendadas
celery -A wedding_management beat --loglevel=info

# Ver workers ativos
celery -A wedding_management worker --loglevel=info
```

---

## Documentação Relacionada

- **[Mixins README](mixins/README.md)** - Documentação detalhada de cada mixin
- **[Templates README](../../templates/README.md)** - Uso de template tags

---

**Última Atualização:** 22 de novembro de 2025  
**Versão:** Atual (Contínuo) - Base compartilhada do projeto

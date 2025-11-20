# Core Mixins - Documentação

Este módulo contém mixins reutilizáveis que fornecem funcionalidades comuns para views e formulários em toda a aplicação.

## 📋 Índice

- [Auth Mixins](#auth-mixins)
- [Form Mixins](#form-mixins)
- [View Mixins](#view-mixins)
- [Uso e Exemplos](#uso-e-exemplos)

---

## 🔐 Auth Mixins

### `OwnerRequiredMixin`

**Propósito:** Garante que usuários autenticados só possam acessar seus próprios recursos.

**Herda de:** `LoginRequiredMixin`

**Atributos Necessários:**
- `model`: O modelo Django a ser filtrado
- `owner_field_name`: Nome do campo que referencia o proprietário (ex: `'user'`, `'planner'`, `'owner'`)

**Exemplo:**
```python
from django.views.generic import UpdateView
from apps.core.mixins import OwnerRequiredMixin
from .models import Wedding

class WeddingUpdateView(OwnerRequiredMixin, UpdateView):
    model = Wedding
    owner_field_name = 'planner'
    fields = ['date', 'location', 'budget']
```

**O que faz:**
- ✅ Verifica se o usuário está autenticado
- ✅ Filtra o queryset para mostrar apenas objetos do usuário
- ✅ Previne acesso não autorizado a recursos de outros usuários

---

### `RedirectAuthenticatedUserMixin`

**Propósito:** Redireciona usuários já autenticados de páginas públicas (login, signup).

**Atributos Configuráveis:**
- `redirect_url_authenticated`: URL de destino (padrão: `'weddings:my_weddings'`)
- `redirect_message`: Mensagem de boas-vindas (padrão: `'Bem vindo de volta'`)

**Exemplo:**
```python
from django.views.generic import TemplateView
from apps.core.mixins import RedirectAuthenticatedUserMixin

class HomeView(RedirectAuthenticatedUserMixin, TemplateView):
    template_name = 'home.html'
    redirect_message = 'Olá novamente'
```

**O que faz:**
- ✅ Intercepta usuários já logados
- ✅ Exibe mensagem personalizada de boas-vindas
- ✅ Redireciona para área autenticada
- ✅ Usa `first_name` do usuário, ou `username` como fallback

---

## 📝 Form Mixins

### `BaseFormStylingMixin`

**Propósito:** Classe base para aplicar estilos CSS Bootstrap aos formulários.

**Atributos Configuráveis:**
- `form_control_classes`: Classes CSS para campos normais
- `checkbox_classes`: Classes CSS para checkboxes

**Não use diretamente.** Use as subclasses específicas abaixo.

---

### `FormStylingMixin`

**Propósito:** Aplica estilos Bootstrap padrão aos campos do formulário.

**Exemplo:**
```python
from django import forms
from apps.core.mixins import FormStylingMixin

class ContactForm(FormStylingMixin, forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    active = forms.BooleanField(required=False)
```

**O que faz:**
- ✅ Adiciona `form-control ps-5` aos campos normais
- ✅ Adiciona `form-check-input` aos checkboxes
- ✅ Marca campos inválidos com `is-invalid` após validação

---

### `FormStylingMixinLarge`

**Propósito:** Aplica estilos Bootstrap em tamanho grande (para formulários destacados).

**Uso:** Ideal para páginas de login, registro ou formulários principais.

**Exemplo:**
```python
from django import forms
from apps.core.mixins import FormStylingMixinLarge

class SignupForm(FormStylingMixinLarge, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
```

**O que faz:**
- ✅ Adiciona `form-control form-control-lg ps-5 custom-font-size`
- ✅ Mesmas funcionalidades do `FormStylingMixin`, mas com campos maiores

---

## 🌐 View Mixins

### `HtmxUrlParamsMixin`

**Propósito:** Extrai parâmetros da query string do header `HX-Current-Url`.

**Método Principal:**
```python
_get_params_from_htmx_url() -> Dict[str, str]
```

**Exemplo:**
```python
from django.views import View
from apps.core.mixins import HtmxUrlParamsMixin

class MyHtmxView(HtmxUrlParamsMixin, View):
    def get(self, request):
        params = self._get_params_from_htmx_url()
        page = params.get('page', '1')
        search = params.get('q', '')
        # ... processar com os parâmetros preservados
```

**O que faz:**
- ✅ Lê o header `HX-Current-Url` enviado pelo HTMX
- ✅ Extrai todos os query parameters
- ✅ Retorna dict vazio em caso de erro (não quebra a requisição)
- ✅ Útil para manter estado de paginação/filtros em requisições AJAX

---

### `BaseHtmxResponseMixin`

**Propósito:** Facilita a renderização de respostas HTMX com headers apropriados.

**Atributos Necessários:**
- `htmx_template_name`: Nome do template a renderizar
- `htmx_retarget_id`: Seletor CSS do elemento alvo (ex: `'#results'`)

**Atributos Opcionais:**
- `htmx_reswap_method`: Método de swap (padrão: `'innerHTML'`)

**Métodos:**
- `get_htmx_context_data(**kwargs)`: Prepara o contexto do template
- `render_htmx_response(trigger=None, **kwargs)`: Renderiza a resposta

**Exemplo:**
```python
from django.views import View
from apps.core.mixins import BaseHtmxResponseMixin

class ItemListView(BaseHtmxResponseMixin, View):
    htmx_template_name = 'partials/items_list.html'
    htmx_retarget_id = '#items-container'
    htmx_reswap_method = 'innerHTML'
    
    def get(self, request):
        items = Item.objects.all()
        return self.render_htmx_response(
            trigger='itemsUpdated',
            items=items,
            total=items.count()
        )
```

**O que faz:**
- ✅ Renderiza o template especificado
- ✅ Configura headers HTMX automaticamente:
  - `HX-Retarget`: Onde inserir o conteúdo
  - `HX-Reswap`: Como inserir (innerHTML, outerHTML, etc)
  - `HX-Trigger-After-Swap`: Evento customizado (opcional)
- ✅ Injeta automaticamente o `request` no contexto

---

## 🎯 Uso e Exemplos

### Combinando Múltiplos Mixins

```python
from django.views.generic import UpdateView
from apps.core.mixins import (
    OwnerRequiredMixin,
    BaseHtmxResponseMixin,
    HtmxUrlParamsMixin
)

class WeddingUpdateView(
    OwnerRequiredMixin,
    BaseHtmxResponseMixin,
    HtmxUrlParamsMixin,
    UpdateView
):
    model = Wedding
    owner_field_name = 'planner'
    htmx_template_name = 'partials/wedding_form.html'
    htmx_retarget_id = '#wedding-detail'
    fields = ['date', 'location', 'budget']
    
    def form_valid(self, form):
        self.object = form.save()
        return self.render_htmx_response(
            trigger='weddingUpdated',
            wedding=self.object
        )
```

### Importação Simplificada

```python
# Ao invés de:
from apps.core.mixins.auth import OwnerRequiredMixin
from apps.core.mixins.forms import FormStylingMixin
from apps.core.mixins.views import BaseHtmxResponseMixin

# Use:
from apps.core.mixins import (
    OwnerRequiredMixin,
    FormStylingMixin,
    BaseHtmxResponseMixin
)
```

---

## 🔄 Melhorias Implementadas (Changelog)

### Versão Atual

**Auth Mixins:**
- ✨ **Bug Fix:** Corrigido espaço na mensagem de boas-vindas (agora: "Bem vindo de volta, Nome!")
- ✨ Adicionados type hints completos
- ✨ Documentação expandida com exemplos de uso
- ✨ Melhorada estrutura de docstrings

**Form Mixins:**
- ✨ Refatorado para eliminar duplicação de código
- ✨ Criada classe base `BaseFormStylingMixin` parametrizável
- ✨ `FormStylingMixin` e `FormStylingMixinLarge` agora herdam da base
- ✨ Adicionados type hints
- ✨ Documentação melhorada

**View Mixins:**
- ✨ Melhoradas docstrings com exemplos práticos
- ✨ Adicionados type hints completos
- ✨ Documentação de parâmetros e retornos
- ✨ Exemplos de uso expandidos

**Geral:**
- ✨ Criado `__init__.py` com exports organizados
- ✨ Todos os testes passando (30/30)
- ✨ Zero erros de lint nos arquivos de mixins

---

## 🧪 Testes

Todos os mixins possuem cobertura de testes completa:

```bash
# Rodar testes dos mixins
pytest apps/core/tests/mixins/ -v

# Cobertura específica
pytest apps/core/tests/mixins/test_auth_mixins.py
pytest apps/core/tests/mixins/test_form_mixins.py
pytest apps/core/tests/mixins/test_view_mixins.py
```

**Status Atual:** ✅ 30/30 testes passando

---

## 📚 Recursos Adicionais

- [Documentação Django CBVs](https://docs.djangoproject.com/en/stable/topics/class-based-views/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Bootstrap Forms](https://getbootstrap.com/docs/5.0/forms/overview/)

---

**Última Atualização:** 20 de novembro de 2025

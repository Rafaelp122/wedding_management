# Scheduler - Documentação Técnica Completa

Sistema de calendário de eventos com FullCalendar.js e API REST.

**Versão:** 2.0  
**Status:** ✅ 61 testes passando  
**Cobertura:** models, forms, views, mixins, querysets, API  

---

## Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Models & QuerySets](#models--querysets)
- [Forms](#forms)
- [Mixins](#mixins)
- [Views](#views)
- [API REST](#api-rest)
- [FullCalendar Integration](#fullcalendar-integration)
- [Segurança](#segurança)
- [Testes](#testes)

---

## Visão Geral

O app `scheduler` gerencia o **calendário de eventos** relacionados aos casamentos. Permite criar, visualizar, editar e deletar compromissos como reuniões, pagamentos, provas e outras tarefas importantes do planejamento.

### Responsabilidades

-   **Gerenciamento de Eventos:** CRUD completo de eventos de calendário
-   **Visualização Temporal:** Exibição em formato de calendário (FullCalendar.js)
-   **Filtros e Busca:** Filtrar por tipo, status e busca textual
-   **API REST:** Endpoint JSON para integração com frontend
-   **Validação de Horários:** Garante que horário de fim seja após início

---

## Arquitetura

### Padrões Aplicados

- **Single Responsibility Principle (SRP):** Cada mixin tem uma responsabilidade
- **Separation of Concerns:** Lógica separada em mixins granulares
- **DRY:** Reutilização de mixins do core (`ModalContextMixin`)
- **Lean Testing:** Testes focados em comportamento crítico (v2.0 - 68% redução)

### Estrutura de Arquivos

```
apps/scheduler/
├── models.py          # Model Event
├── querysets.py       # EventQuerySet customizado
├── forms.py           # EventForm com validações
├── mixins.py          # 8 mixins granulares
├── views.py           # Class-Based Views (CBV)
├── api_views.py       # API REST para FullCalendar
├── urls.py            # Rotas web + API
├── admin.py           # Admin Django
└── tests/
    ├── test_models.py      # 10 testes
    ├── test_querysets.py   # 6 testes
    ├── test_forms.py       # 11 testes
    ├── test_mixins.py      # 8 testes (refatorado)
    ├── test_views.py       # 14 testes
    ├── test_api_views.py   # 2 testes
    └── test_urls.py        # 10 testes
```

---

## Models & QuerySets

### Event Model

**Campos principais:**

```python
class Event(BaseModel):
    # Relações
    wedding = ForeignKey(Wedding, on_delete=CASCADE, related_name="events")
    
    # Dados do evento
    title = CharField(max_length=200)
    description = TextField(blank=True)
    
    # Datas
    start_time = DateTimeField()
    end_time = DateTimeField()
    
    # Categorização
    event_type = CharField(max_length=50, choices=TYPE_CHOICES)
    status = CharField(max_length=50, choices=STATUS_CHOICES, default="PENDING")
```

**Tipos de Evento:**
- `MEETING` - Reunião
- `PAYMENT` - Pagamento
- `FITTING` - Prova (vestido, terno, etc)
- `TASK` - Tarefa
- `OTHER` - Outro

**Status disponíveis:**
- `PENDING` - Pendente
- `CONFIRMED` - Confirmado
- `CANCELLED` - Cancelado
- `COMPLETED` - Concluído

**Validações:**

```python
def save(self, *args, **kwargs):
    if self.end_time and self.start_time and self.end_time <= self.start_time:
        raise ValidationError("Horário de fim deve ser após o início")
    super().save(*args, **kwargs)
```

### EventQuerySet

**Métodos disponíveis:**

```python
Event.objects
    .by_wedding(wedding)            # Filtra por casamento
    .by_date_range(start, end)      # Filtra por período
    .upcoming()                     # Eventos futuros ordenados
    .apply_search(q)                # Busca por título/descrição
    .apply_sort(option)             # Ordenação customizada
```

**Implementação:**

```python
def by_date_range(self, start_date, end_date):
    """Filtra eventos em um período"""
    return self.filter(
        start_time__gte=start_date,
        end_time__lte=end_date
    )

def upcoming(self):
    """Eventos futuros ordenados por data"""
    from django.utils import timezone
    return self.filter(start_time__gte=timezone.now()).order_by("start_time")

def apply_search(self, query):
    """Busca por título ou descrição"""
    return self.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )
```

---

## Forms

### EventForm

**Validações de negócio:**

```python
class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "event_type", "start_time", "end_time", "status"]
        widgets = {
            "start_time": DateTimeInput(format="%d/%m/%Y %H:%M", attrs={"type": "datetime-local"}),
            "end_time": DateTimeInput(format="%d/%m/%Y %H:%M", attrs={"type": "datetime-local"}),
            "description": Textarea(attrs={"rows": 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        
        if start_time and end_time:
            if end_time <= start_time:
                logger.warning(f"Tentativa de horário inválido: {start_time} → {end_time}")
                raise ValidationError("Horário de fim deve ser após o início")
            
            # Validação: não pode ser no passado
            from django.utils import timezone
            if start_time < timezone.now():
                logger.warning(f"Tentativa de data passada: {start_time}")
                raise ValidationError("Não pode agendar eventos no passado")
        
        return cleaned_data
```

**UX:**
- Widget datetime-local para melhor seleção de data/hora
- Placeholders e ícones FontAwesome
- Logging de validações falhadas

---

## Mixins

### Arquitetura Granular (8 Mixins → v2.0)

**1. EventOwnershipMixin** - Garante isolamento por usuário

```python
class EventOwnershipMixin:
    def get_queryset(self):
        return Event.objects.filter(wedding__planner=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        if "wedding_id" in kwargs:
            self.wedding = get_object_or_404(
                Wedding,
                id=kwargs["wedding_id"],
                planner=request.user
            )
        return super().dispatch(request, *args, **kwargs)
```

**2. EventFormLayoutMixin** - Define layout do formulário

**3. EventModalContextMixin** - Contexto de modais (DEPRECIADO em v2.0)

**4. EventQuerysetMixin** - Lógica de filtros e busca

```python
class EventQuerysetMixin:
    def build_queryset(self, search=None, event_type=None, status=None, sort=None):
        qs = Event.objects.filter(wedding=self.wedding)
        if search:
            qs = qs.apply_search(search)
        if event_type:
            qs = qs.filter(event_type=event_type)
        if status:
            qs = qs.filter(status=status)
        if sort:
            qs = qs.apply_sort(sort)
        return qs
```

**5. EventPaginationContextMixin** - Paginação de eventos

**6. EventHtmxResponseMixin** - Respostas HTMX customizadas

**7. EventFormMixin** - Lógica de form_valid/invalid

**8. EventListActionsMixin** - Facade (agrupa funcionalidades)

---

## Views

### EventCalendarView - Calendário principal

```python
class EventCalendarView(
    LoginRequiredMixin,
    EventOwnershipMixin,
    TemplateView
):
    template_name = "scheduler/calendar.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.wedding
        return context
```

### EventCreateView - Criação com modal (v2.0 - usa ModalContextMixin)

```python
class EventCreateView(
    LoginRequiredMixin,
    EventOwnershipMixin,
    ModalContextMixin,  # Do core
    CreateView
):
    form_class = EventForm
    template_name = "scheduler/partials/_event_form.html"
    
    def form_valid(self, form):
        form.instance.wedding = self.wedding
        self.object = form.save()
        logger.info(f"Evento criado: {self.object}")
        return HttpResponse(status=200, headers={"HX-Trigger": "eventCreated"})
```

### EventUpdateView - Edição com modal (v2.0 - usa ModalContextMixin)

```python
class EventUpdateView(
    LoginRequiredMixin,
    EventOwnershipMixin,
    ModalContextMixin,  # Do core
    UpdateView
):
    form_class = EventForm
    template_name = "scheduler/partials/_event_form.html"
    
    def form_valid(self, form):
        self.object = form.save()
        logger.info(f"Evento atualizado: {self.object}")
        return HttpResponse(status=200, headers={"HX-Trigger": "eventUpdated"})
```

### EventDeleteView - Exclusão com confirmação

### EventDetailView - Detalhes do evento

---

## API REST

### EventListAPIView - Endpoint JSON para FullCalendar

```python
class EventListAPIView(LoginRequiredMixin, View):
    """
    API REST para FullCalendar.js
    Retorna eventos em formato JSON compatível com FullCalendar
    """
    def get(self, request):
        wedding_id = request.GET.get("wedding_id")
        
        # Validar ownership
        wedding = get_object_or_404(
            Wedding,
            id=wedding_id,
            planner=request.user
        )
        
        # Buscar eventos
        events = Event.objects.filter(wedding=wedding)
        
        # Serializar para FullCalendar
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "title": event.title,
                "start": event.start_time.isoformat(),
                "end": event.end_time.isoformat(),
                "description": event.description,
                "eventType": event.event_type,
                "status": event.status,
                "backgroundColor": self._get_color_by_type(event.event_type),
            })
        
        return JsonResponse(events_data, safe=False)
    
    def _get_color_by_type(self, event_type):
        """Cores por tipo de evento"""
        colors = {
            "MEETING": "#3788d8",
            "PAYMENT": "#f39c12",
            "FITTING": "#e74c3c",
            "TASK": "#2ecc71",
            "OTHER": "#95a5a6",
        }
        return colors.get(event_type, "#95a5a6")
```

**Endpoint:**
```
GET /scheduler/api/events/?wedding_id=123
```

**Resposta:**
```json
[
  {
    "id": 1,
    "title": "Reunião com Buffet",
    "start": "2025-12-01T14:00:00",
    "end": "2025-12-01T15:00:00",
    "description": "Definir menu",
    "eventType": "MEETING",
    "status": "CONFIRMED",
    "backgroundColor": "#3788d8"
  }
]
```

---

## FullCalendar Integration

### JavaScript (calendar.js)

```javascript
document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  var weddingId = calendarEl.dataset.weddingId;
  
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'pt-br',
    
    // Carregar eventos via API
    events: `/scheduler/api/events/?wedding_id=${weddingId}`,
    
    // Clique em evento: abrir modal de detalhes
    eventClick: function(info) {
      openEventDetailModal(info.event.id);
    },
    
    // Clique em data: abrir modal de criação
    dateClick: function(info) {
      openEventCreateModal(info.dateStr);
    },
    
    // Personalização
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
  });
  
  calendar.render();
});
```

### Templates

**calendar.html:**
```html
<div id="calendar" data-wedding-id="{{ wedding.id }}"></div>

<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js"></script>
<script src="{% static 'scheduler/js/calendar.js' %}"></script>
```

---

## Segurança

### Multicamadas de Proteção

1. **LoginRequiredMixin** - Autenticação obrigatória
2. **EventOwnershipMixin** - Validação de ownership
3. **API Validation** - Filtra eventos por planner
4. **Logging** - Auditoria de tentativas não autorizadas

**Testes de Segurança:**

```python
def test_other_user_cannot_access_events(self):
    """Outro usuário não pode ver eventos de outro wedding"""
    hacker = User.objects.create_user(username="hacker", password="123")
    self.client.force_login(hacker)
    
    response = self.client.get(self.url)
    assert response.status_code == 404  # Wedding não encontrado
```

---

## Performance

### Otimizações

- **Queries otimizadas:** `select_related('wedding__planner')`
- **API eficiente:** Serialização direta para JSON
- **Filtros no banco:** Queries com annotate/aggregate
- **Índices futuros:** Considerar adicionar em `(wedding, start_time)`

---

## Testes

### Estrutura (61 testes)

- **`test_models.py` (10):** Validações de horário, choices, cascade
- **`test_querysets.py` (6):** Filtros, busca, ordenação
- **`test_forms.py` (11):** Validações, widgets, logging
- **`test_mixins.py` (8):** Segurança, HTMX, form (v2.0 refatorado)
- **`test_views.py` (14):** CRUD completo, segurança
- **`test_api_views.py` (2):** API REST, filtros
- **`test_urls.py` (10):** Resolução de rotas

### Refatoração v2.0 (Lean Testing)

**Antes:** 25 testes em mixins  
**Depois:** 8 testes em mixins  
**Redução:** 68%

**Removidos:**
- Testes de configuração (triviais)
- Testes de UI/templates (não são responsabilidade de mixins)
- Testes de implementação (testam "como", não "o quê")

**Mantidos:**
- Testes de segurança (isolamento de dados)
- Testes de comportamento crítico
- Testes de integrações complexas

---

## Rotas

### urls.py

```python
from django.urls import path
from apps.scheduler import views, api_views

app_name = "scheduler"

urlpatterns = [
    # Views web
    path("<int:wedding_id>/calendar/", views.EventCalendarView.as_view(), name="calendar"),
    path("<int:wedding_id>/events/create/", views.EventCreateView.as_view(), name="create_event"),
    path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="edit_event"),
    path("events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="delete_event"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    
    # API REST
    path("api/events/", api_views.EventListAPIView.as_view(), name="api_events"),
]
```

---

## Próximos Passos

### Sugerido:

1. **Índices compostos:** `(wedding, start_time)` para performance
2. **Admin melhorado:** `date_hierarchy`, mais campos
3. **Recurring events:** Eventos recorrentes (semanais, mensais)
4. **Notificações de lembrete:** E-mail X dias antes do evento
5. **iCal export:** Exportar para Google Calendar/Outlook

---

**Última Atualização:** 21 de novembro de 2025  
**Versão:** 2.0 - Lean Testing + ModalContextMixin do core

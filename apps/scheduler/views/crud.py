from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from ..models import Event
from ..forms import EventCrudForm
from .mixins import EventPlannerOwnerMixin


class EventListView(LoginRequiredMixin, ListView):
    """Lista todos os eventos do planner logado."""
    model = Event
    template_name = "scheduler/schedule_list.html"
    context_object_name = "events"

    def get_queryset(self):
        # Filtra eventos apenas do planner autenticado
        print(f"DEBUG EventListView: Buscando eventos para planner ID: {self.request.user.id}")
        qs = Event.objects.filter(planner=self.request.user).order_by("start_time")
        print(f"DEBUG EventListView: Encontrados {qs.count()} eventos.")
        return qs


class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Cria um novo evento."""
    model = Event
    form_class = EventCrudForm
    template_name = "scheduler/schedule_form.html"
    success_url = reverse_lazy("scheduler:list")
    success_message = "Evento '%(title)s' criado com sucesso!"

    def get_context_data(self, **kwargs):
        # Configurações visuais e ícones do formulário
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Criar Novo Evento"

        context["form_layout_dict"] = {
            "title": "col-md-12",
            "wedding": "col-md-6",
            "event_type": "col-md-6",
            "start_time": "col-md-6",
            "end_time": "col-md-6",
            "location": "col-md-12",
            "description": "col-md-12",
        }

        context["form_icons"] = {
            "title": "fas fa-heading",
            "wedding": "fas fa-ring",
            "event_type": "fas fa-calendar-check",
            "start_time": "fas fa-clock",
            "end_time": "fas fa-clock",
            "location": "fas fa-map-marker-alt",
        }

        context["form_action"] = "."
        return context

    def get_form_kwargs(self):
        # Passa o usuário logado para o formulário
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        print("DEBUG EventCreateView: Enviando user para form kwargs.")
        return kwargs

    def form_valid(self, form):
        # Define o planner logado como responsável pelo evento
        form.instance.planner = self.request.user
        print(f"DEBUG EventCreateView: Definindo planner {self.request.user.id} para novo evento.")
        return super().form_valid(form)


class EventUpdateView(EventPlannerOwnerMixin, SuccessMessageMixin, UpdateView):
    """Edita um evento existente."""
    form_class = EventCrudForm
    template_name = "scheduler/schedule_form.html"
    success_url = reverse_lazy("scheduler:list")
    success_message = "Evento '%(title)s' atualizado com sucesso!"
    pk_url_kwarg = "event_id"

    def get_context_data(self, **kwargs):
        # Define título e layout do formulário de edição
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar Evento"

        context["form_layout_dict"] = {
            "title": "col-md-12",
            "event_type": "col-md-6",
            "start_time": "col-md-6",
            "end_time": "col-md-6",
            "location": "col-md-12",
            "description": "col-md-12",
        }

        context["form_icons"] = {
            "title": "fas fa-heading",
            "event_type": "fas fa-calendar-check",
            "start_time": "fas fa-clock",
            "end_time": "fas fa-clock",
            "location": "fas fa-map-marker-alt",
        }

        return context

    def get_form_kwargs(self):
        # Passa o usuário logado para o form
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        print("DEBUG EventUpdateView: Enviando user para form kwargs.")
        return kwargs


class EventDeleteView(EventPlannerOwnerMixin, SuccessMessageMixin, DeleteView):
    """Exclui um evento existente."""
    template_name = "scheduler/schedule_confirm_delete.html"
    success_url = reverse_lazy("scheduler:list")
    pk_url_kwarg = "event_id"
    context_object_name = "event"

    def get_object(self, queryset=None):
        # Obtém o evento e armazena o título para mensagem de sucesso
        obj = super().get_object(queryset=queryset)
        self.object_title = obj.title
        print(f"DEBUG EventDeleteView: Preparando exclusão ID {obj.id} ('{self.object_title}')")
        return obj

    def form_valid(self, form):
        # Mensagem de sucesso após exclusão
        self.success_message = f"Evento '{self.object_title}' excluído com sucesso!"
        print(f"DEBUG EventDeleteView: Evento '{self.object_title}' excluído.")
        response = super().form_valid(form)
        return response

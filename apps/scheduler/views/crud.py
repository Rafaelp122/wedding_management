# scheduler/views/crud.py

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

# Importações relativas
from ..models import Event
from ..forms import EventCrudForm
from .mixins import EventPlannerOwnerMixin

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'scheduler/schedule_list.html' 
    context_object_name = 'events'

    def get_queryset(self):
        print(f"DEBUG EventListView: Buscando eventos para planner ID: {self.request.user.id}") 
        qs = Event.objects.filter(planner=self.request.user).order_by('start_time')
        print(f"DEBUG EventListView: Encontrados {qs.count()} eventos.") 
        return qs

class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = EventCrudForm 
    template_name = 'scheduler/schedule_form.html' 
    success_url = reverse_lazy('scheduler:list') 
    success_message = "Evento '%(title)s' criado com sucesso!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Criar Novo Evento'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        print("DEBUG EventCreateView: Enviando user para form kwargs.") 
        return kwargs

    def form_valid(self, form):
        form.instance.planner = self.request.user
        print(f"DEBUG EventCreateView: Definindo planner {self.request.user.id} para novo evento.") 
        return super().form_valid(form)

class EventUpdateView(EventPlannerOwnerMixin, SuccessMessageMixin, UpdateView):
    form_class = EventCrudForm 
    template_name = 'scheduler/schedule_form.html' 
    success_url = reverse_lazy('scheduler:list') 
    success_message = "Evento '%(title)s' atualizado com sucesso!"
    pk_url_kwarg = 'event_id' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Evento'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        print("DEBUG EventUpdateView: Enviando user para form kwargs.") 
        return kwargs

class EventDeleteView(EventPlannerOwnerMixin, SuccessMessageMixin, DeleteView):
    template_name = 'scheduler/schedule_confirm_delete.html' 
    success_url = reverse_lazy('scheduler:list') 
    pk_url_kwarg = 'event_id' 
    context_object_name = 'event'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self.object_title = obj.title 
        print(f"DEBUG EventDeleteView: Preparando exclusão ID {obj.id} ('{self.object_title}')") 
        return obj

    def form_valid(self, form):
        self.success_message = f"Evento '{self.object_title}' excluído com sucesso!"
        print(f"DEBUG EventDeleteView: Evento '{self.object_title}' excluído.") 
        response = super().form_valid(form)
        return response
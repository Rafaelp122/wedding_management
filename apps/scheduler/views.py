from django.shortcuts import render, get_object_or_404, redirect 
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponseBadRequest, Http404 
from django.views.decorators.http import require_POST 
from django.utils import timezone 
# from django.core.serializers import serialize # Não necessário
import json
from datetime import datetime 
from django.contrib.auth.decorators import login_required 

# Importações dos modelos e formulários corretos (usando Event)
from .models import Event
from apps.weddings.models import Wedding 
from .forms import EventForm, EventCrudForm 

# --- MIXINS E VIEWS DE CRUD (mantidas como na versão anterior) ---
# ... (EventPlannerOwnerMixin, EventListView, EventCreateView, EventUpdateView, EventDeleteView) ...
# (O código destas classes permanece o mesmo da versão anterior com logs)

class EventPlannerOwnerMixin(LoginRequiredMixin):
    model = Event 

    def get_queryset(self):
        print(f"DEBUG EventPlannerOwnerMixin: Filtrando queryset para planner ID: {self.request.user.id}") 
        qs = super().get_queryset().filter(planner=self.request.user)
        print(f"DEBUG EventPlannerOwnerMixin: Queryset filtrada encontrada: {qs.count()} eventos.") 
        return qs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.planner != self.request.user:
            from django.core.exceptions import PermissionDenied
            print(f"DEBUG EventPlannerOwnerMixin: Acesso NEGADO evento ID {obj.id} user ID {self.request.user.id}. Dono: {obj.planner.id}") 
            raise PermissionDenied("Você não tem permissão para acessar este evento.")
        print(f"DEBUG EventPlannerOwnerMixin: Acesso PERMITIDO evento ID {obj.id} user ID {self.request.user.id}") 
        return obj

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        print("DEBUG EventUpdateView: Enviando user para form kwargs.") 
        return kwargs

class EventDeleteView(EventPlannerOwnerMixin, SuccessMessageMixin, DeleteView):
    template_name = 'scheduler/schedule_confirm_delete.html' 
    success_url = reverse_lazy('scheduler:list') 
    pk_url_kwarg = 'event_id' 

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

# ======================================================================
#             VIEWS PARA O CALENDÁRIO INTERATIVO (FullCalendar)
# ======================================================================

@login_required 
def partial_scheduler(request, wedding_id):
    """
    Renderiza APENAS o HTML parcial do calendário. 
    Os dados JSON serão buscados pelo FullCalendar via 'event_api'.
    """
    planner = request.user
    try:
        current_wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)
        print(f"DEBUG partial_scheduler: Carregando parcial para Wedding ID: {current_wedding.id}") 
        context = {'wedding': current_wedding}
    except Http404:
         print(f"ERRO DEBUG partial_scheduler: Casamento ID {wedding_id} não encontrado para planner {planner.id}") 
         return HttpResponseBadRequest("Casamento não encontrado ou não pertence a si.")

    return render(request, 'scheduler/partials/scheduler_partial.html', context)

# ======================================================================
#                    API DE EVENTOS (JSON) - AJUSTES VISUAIS
# ======================================================================
@login_required
def event_api(request, wedding_id):
    """
    Retorna os eventos e dias de casamento do planner em formato JSON 
    para ser consumido pelo FullCalendar. 
    AJUSTADO: Título e cor dos dias de casamento.
    """
    planner = request.user
    print(f"\n--- DEBUG event_api para Wedding ID: {wedding_id}, Planner ID: {planner.id} ---") 

    try:
        current_wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)
        print(f"DEBUG event_api: Casamento atual ({current_wedding.id}) validado.") 
    except Http404:
        print(f"ERRO DEBUG event_api: Casamento ID {wedding_id} inválido/não pertence ao planner {planner.id}.") 
        return JsonResponse({'error': 'Casamento inválido ou não autorizado.'}, status=403)

    # Busca todos os eventos e casamentos do planner
    all_events = Event.objects.filter(planner=planner) 
    all_weddings = Wedding.objects.filter(planner=planner)

    print(f"DEBUG event_api [DB]: Encontrados {all_events.count()} eventos e {all_weddings.count()} casamentos.") 

    calendar_events = [] # Lista para os dados formatados

    # Adiciona os dias de casamento
    for w in all_weddings:
        is_current = (w.id == current_wedding.id)
        # *** ALTERAÇÃO 1: Título do evento de casamento ***
        wedding_title = f"{w.groom_name} & {w.bride_name}" if w.groom_name and w.bride_name else (w.client.name if w.client else 'Casamento')
        calendar_events.append({
            'title': wedding_title, # Título sem o prefixo "Dia Casamento:"
            'start': w.date.isoformat(), 
            'allDay': True,
            'display': 'background', 
            # *** ALTERAÇÃO 2: Cor de fundo amarela para TODOS os casamentos ***
            'color': '#ffc107', # Amarelo Bootstrap para todos
            'extendedProps': { 
                'isWeddingDay': True, 
                'isCurrentWedding': is_current # Mantém a distinção para possível estilo CSS (ex: opacidade)
            }
        })

    # Adiciona os eventos normais (sem alterações aqui)
    for event in all_events:
        is_current_w_event = (event.wedding_id == current_wedding.id) 
        calendar_events.append({
            'id': event.id, 'title': event.title,
            'start': timezone.localtime(event.start_time).isoformat() if event.start_time else None, 
            'end': timezone.localtime(event.end_time).isoformat() if event.end_time else None,
            'allDay': False, 
            'extendedProps': {
                'isWeddingDay': False, 'isCurrentWedding': is_current_w_event, 
                'description': event.description or '', 'location': event.location or '',     
                'type': event.event_type or ''         
            }
        })

    print(f"DEBUG event_api [JSON OK]: Retornando JSON com {len(calendar_events)} entradas.") 
    print(f"--- DEBUG event_api FIM ---") 
    return JsonResponse(calendar_events, safe=False) 

# --- Função manage_event (mantida como na versão anterior) ---
# ... (código da função manage_event permanece o mesmo) ...

def manage_event(request, wedding_id):
    """
    View ÚNICA para GET (buscar forms) e POST (salvar/atualizar/excluir).
    """
    planner = request.user
    wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)
    print(f"\n--- DEBUG manage_event (Wedding: {wedding_id}, Planner: {planner.id}, Método: {request.method}) ---") 

    if request.method == 'GET':
        action = request.GET.get('action')
        print(f"DEBUG manage_event [GET]: Ação={action}") 
        
        if action == 'get_create_form':
            clicked_date_str = request.GET.get('date')
            initial_data = {}
            if clicked_date_str:
                try:
                    initial_data['start_date'] = datetime.strptime(clicked_date_str, '%Y-%m-%d').date()
                    print(f"DEBUG manage_event [GET create]: Data inicial={initial_data['start_date']}") 
                except ValueError:
                    print(f"AVISO DEBUG manage_event [GET create]: Data recebida ('{clicked_date_str}') inválida.") 
                    pass 
            form = EventForm(initial=initial_data) 
            context = { 'form': form, 'wedding': wedding, 'action_url': reverse_lazy('scheduler:manage_event', kwargs={'wedding_id': wedding.id}) }
            print("DEBUG manage_event [GET create]: Renderizando form.") 
            return render(request, 'scheduler/partials/_event_form_modal_content.html', context)

        elif action == 'get_edit_form':
            event_id = request.GET.get('event_id')
            print(f"DEBUG manage_event [GET edit]: Buscando ID={event_id}") 
            event = get_object_or_404(Event, pk=event_id, planner=planner) 
            print(f"DEBUG manage_event [GET edit]: Evento '{event.title}' encontrado.") 
            form = EventForm(instance=event) 
            context = { 'form': form, 'wedding': wedding, 'event': event, 'action_url': reverse_lazy('scheduler:manage_event', kwargs={'wedding_id': wedding.id}) }
            print("DEBUG manage_event [GET edit]: Renderizando form.") 
            return render(request, 'scheduler/partials/_event_form_modal_content.html', context)
            
        else:
            print(f"ERRO DEBUG manage_event [GET]: Ação inválida: '{action}'") 
            return HttpResponseBadRequest("Ação GET inválida.")

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            print(f"DEBUG manage_event [POST]: Ação={action}, Dados={data}") 
            
            if action == 'move_resize':
                event_id = data.get('event_id')
                start_time_iso = data.get('start_time')
                end_time_iso = data.get('end_time')
                print(f"DEBUG manage_event [POST move_resize]: ID={event_id}, Start={start_time_iso}, End={end_time_iso}") 
                event = get_object_or_404(Event, pk=event_id, planner=planner) 
                try:
                    if start_time_iso: event.start_time = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
                    else: raise ValueError("Start time não pode ser nulo.")
                    if end_time_iso: event.end_time = datetime.fromisoformat(end_time_iso.replace('Z', '+00:00'))
                    else: event.end_time = None 
                    event.save()
                    print(f"DEBUG manage_event [POST move_resize OK]: Evento ID {event_id} atualizado.") 
                    return JsonResponse({'status': 'success', 'message': 'Evento atualizado.'})
                except (ValueError, TypeError) as e:
                     print(f"ERRO DEBUG manage_event [POST move_resize FALHA]: Formato data/hora: {e}") 
                     return JsonResponse({'status': 'error', 'message': f'Formato data/hora inválido: {e}'}, status=400)

            elif action == 'modal_save':
                event_id = data.get('event_id') 
                print(f"DEBUG manage_event [POST modal_save]: ID={event_id}") 
                instance = None
                if event_id: instance = get_object_or_404(Event, pk=event_id, planner=planner) 
                else: print("DEBUG manage_event [POST modal_save]: Criando novo.") 
                post_data = data.get('form_data', {}) 
                print(f"DEBUG manage_event [POST modal_save]: Dados form={post_data}") 
                form = EventForm(post_data, instance=instance) 
                if form.is_valid():
                    print("DEBUG manage_event [POST modal_save]: Form VÁLIDO.") 
                    event = form.save(commit=False) 
                    event.planner = planner 
                    event.start_time = form.cleaned_data.get('start_time') 
                    event.end_time = form.cleaned_data.get('end_time')
                    if not event.wedding: event.wedding = wedding 
                    event.save() 
                    print(f"DEBUG manage_event [POST modal_save OK]: Evento ID {event.id} salvo.") 
                    return JsonResponse({'status': 'success', 'message': 'Evento salvo.'})
                else:
                    print(f"ERRO DEBUG manage_event [POST modal_save FALHA]: Form INVÁLIDO: {form.errors.as_json()}") 
                    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400) 

            elif action == 'delete':
                 event_id = data.get('event_id')
                 print(f"DEBUG manage_event [POST delete]: Tentando ID={event_id}") 
                 if not event_id:
                      print("ERRO DEBUG manage_event [POST delete]: ID não fornecido.") 
                      return JsonResponse({'status': 'error', 'message': 'ID do evento não fornecido.'}, status=400)
                 event = get_object_or_404(Event, pk=event_id, planner=planner) 
                 event_title = event.title 
                 event.delete()
                 print(f"DEBUG manage_event [POST delete OK]: Evento ID {event_id} ('{event_title}') excluído.") 
                 return JsonResponse({'status': 'success', 'message': 'Evento excluído.'})

            else:
                print(f"ERRO DEBUG manage_event [POST]: Ação desconhecida: '{action}'") 
                return JsonResponse({'status': 'error', 'message': 'Ação POST desconhecida.'}, status=400)

        except json.JSONDecodeError:
            print("ERRO DEBUG manage_event [POST]: JSON inválido.") 
            return JsonResponse({'status': 'error', 'message': 'JSON inválido.'}, status=400)
        except Http404 as e: 
             object_type = "Casamento" if isinstance(e, Wedding.DoesNotExist) else "Evento"
             # Tenta obter o ID que falhou a partir dos dados recebidos
             failed_id = wedding_id if object_type == "Casamento" else data.get('event_id', 'desconhecido')
             print(f"ERRO DEBUG manage_event [POST]: {object_type} ID {failed_id} não encontrado/não pertence ao planner.")
             return JsonResponse({'status': 'error', 'message': f'{object_type} não encontrado ou não pertence a si.'}, status=404)
        except Exception as e:
            import traceback 
            print("\n!!! ERRO INESPERADO manage_event (POST) !!!") 
            traceback.print_exc() 
            print(f"!!! FIM ERRO INESPERADO !!!\n") 
            return JsonResponse({'status': 'error', 'message': f'Erro interno: {type(e).__name__}'}, status=500)
            
    else:
        print(f"ERRO DEBUG manage_event: Método '{request.method}' não permitido.") 
        return HttpResponseBadRequest(f"Método '{request.method}' não permitido.")

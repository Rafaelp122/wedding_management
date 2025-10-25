from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponseBadRequest
# from django.views.decorators.http import require_POST # Não usado em manage_event
from django.utils import timezone
from django.core.serializers import serialize
import json
from datetime import datetime
from django.core.exceptions import PermissionDenied # Importado para o Mixin

# Importações dos modelos e formulários corretos (usando Event)
from .models import Event
from apps.weddings.models import Wedding # Importa Wedding
from .forms import EventForm, EventCrudForm # Importa AMBOS os formulários

# Mixin para garantir que o planner só veja/edite seus próprios eventos
class EventPlannerOwnerMixin(LoginRequiredMixin):
    """ Garante que o usuário logado (planner) só acesse seus próprios eventos. """
    model = Event # Define o modelo padrão para este Mixin

    def get_queryset(self):
        # Filtra a queryset para retornar apenas eventos do planner logado.
        # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
        return super().get_queryset().filter(planner=self.request.user)

    def get_object(self, queryset=None):
        # Garante que o objeto a ser editado/apagado pertence ao planner logado.
        obj = super().get_object(queryset=queryset)
        # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
        if obj.planner != self.request.user:
            raise PermissionDenied("Você não tem permissão para acessar este evento.")
        return obj

# ======================================================================
#                     VIEWS PARA O CRUD TRADICIONAL
# ======================================================================

class EventListView(LoginRequiredMixin, ListView): # Removido Mixin duplicado, LoginRequiredMixin já basta aqui
    model = Event
    template_name = 'scheduler/schedule_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Lista apenas os eventos do planner logado, ordenados por data/hora
        # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
        return Event.objects.filter(planner=self.request.user).order_by('start_time')

class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = EventCrudForm
    template_name = 'scheduler/schedule_form.html'
    success_url = reverse_lazy('scheduler:list')
    success_message = "Evento '%(title)s' criado com sucesso!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Define o planner do evento como o usuário logado ANTES de salvar
        # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
        form.instance.planner = self.request.user
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
        return kwargs

    # Não precisa de form_valid aqui, o UpdateView já salva a instância

class EventDeleteView(EventPlannerOwnerMixin, SuccessMessageMixin, DeleteView):
    template_name = 'scheduler/schedule_confirm_delete.html'
    success_url = reverse_lazy('scheduler:list')
    # success_message já não é mais necessário aqui, vamos usar form_valid
    pk_url_kwarg = 'event_id'

    def get_object(self, queryset=None):
         obj = super().get_object(queryset=queryset)
         self.object_title = obj.title
         return obj

    def form_valid(self, form):
        # Usamos form_valid para definir a mensagem ANTES da exclusão ocorrer
        from django.contrib import messages # Importa messages aqui
        messages.success(self.request, f"Evento '{self.object_title}' excluído com sucesso!")
        return super().form_valid(form)


# ======================================================================
#             VIEWS PARA O CALENDÁRIO INTERATIVO (FullCalendar)
# ======================================================================

def partial_scheduler(request, wedding_id):
    """
    Renderiza o HTML parcial do calendário e fornece os dados JSON iniciais.
    Agora busca TODOS os eventos e casamentos do planner.
    """
    planner = request.user
    current_wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)
    
    # Busca todos os eventos e casamentos do planner
    # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
    all_events = Event.objects.filter(planner=planner)
    all_weddings = Wedding.objects.filter(planner=planner)

    calendar_events = []

    # Adiciona os dias de casamento
    for w in all_weddings:
        is_current = (w.id == current_wedding.id)
        calendar_events.append({
            'title': f"Dia Casamento: {w.groom_name} & {w.bride_name}" if w.groom_name and w.bride_name else f"Dia Casamento: {w.client.name}",
            'start': w.date.isoformat(),
            'allDay': True,
            'display': 'background',
            'color': '#ffc107' if is_current else '#6c757d',
            'extendedProps': {
                'isWeddingDay': True,
                'isCurrentWedding': is_current
            }
        })

    # Adiciona os eventos normais
    for event in all_events:
        is_current_w_event = (event.wedding_id == current_wedding.id)
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': timezone.localtime(event.start_time).isoformat() if event.start_time else None, 
            'end': timezone.localtime(event.end_time).isoformat() if event.end_time else None,
            'allDay': False,
            'color': '#0d6efd' if is_current_w_event else '#adb5bd',
            'extendedProps': {
                'isWeddingDay': False,
                'isCurrentWedding': is_current_w_event,
                'description': event.description,
                'location': event.location,
                'type': event.event_type
            }
        })

    calendar_events_json = json.dumps(calendar_events)
    
    context = {
        'wedding': current_wedding,
        'calendar_events_json': calendar_events_json,
    }
    return render(request, 'scheduler/partials/scheduler_partial.html', context)


def manage_event(request, wedding_id):
    """
    View ÚNICA para lidar com GET (buscar forms) e POST (salvar/atualizar/excluir).
    """
    planner = request.user
    wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)

    if request.method == 'GET':
        action = request.GET.get('action')
        
        if action == 'get_create_form':
            clicked_date_str = request.GET.get('date')
            initial_data = {}
            if clicked_date_str:
                try:
                    initial_data['start_date'] = datetime.strptime(clicked_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            form = EventForm(initial=initial_data) 
            return render(request, 'scheduler/partials/_event_form_modal_content.html', {'form': form, 'wedding': wedding, 'action_url': reverse_lazy('scheduler:manage_event', kwargs={'wedding_id': wedding.id})})

        elif action == 'get_edit_form':
            event_id = request.GET.get('event_id')
            # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
            event = get_object_or_404(Event, pk=event_id, planner=planner)
            form = EventForm(instance=event) 
            return render(request, 'scheduler/partials/_event_form_modal_content.html', {'form': form, 'wedding': wedding, 'event': event, 'action_url': reverse_lazy('scheduler:manage_event', kwargs={'wedding_id': wedding.id})})
            
        else:
            return HttpResponseBadRequest("Ação GET inválida.")

    elif request.method == 'POST':
        try:
            # Tenta ler como JSON primeiro (para AJAX do FullCalendar)
            try:
                data = json.loads(request.body)
                is_json_request = True
            except json.JSONDecodeError:
                # Se não for JSON, tenta ler como dados de formulário (para HTMX do modal)
                data = request.POST 
                is_json_request = False

            action = data.get('action')
            
            # Ação: Mover ou Redimensionar (JSON do FullCalendar)
            if action == 'move_resize' and is_json_request:
                event_id = data.get('event_id')
                start_time_iso = data.get('start_time')
                end_time_iso = data.get('end_time')
                
                # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
                event = get_object_or_404(Event, pk=event_id, planner=planner)
                
                try:
                    event.start_time = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
                    if end_time_iso:
                        event.end_time = datetime.fromisoformat(end_time_iso.replace('Z', '+00:00'))
                    else:
                        event.end_time = None
                    event.save()
                    return JsonResponse({'status': 'success', 'message': 'Evento atualizado.'})
                except (ValueError, TypeError) as e:
                     return JsonResponse({'status': 'error', 'message': f'Formato de data/hora inválido: {e}'}, status=400)

            # Ação: Salvar via Modal (POST do formulário HTMX ou JS do modal)
            elif action == 'modal_save':
                event_id = data.get('event_id') 
                
                instance = None
                if event_id:
                     # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
                    instance = get_object_or_404(Event, pk=event_id, planner=planner)
                
                # Se for JSON, pega os dados do form_data
                post_data = data.get('form_data') if is_json_request else data
                form = EventForm(post_data, instance=instance)
                
                if form.is_valid():
                    event = form.save(commit=False)
                     # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
                    event.planner = planner # Garante o planner
                    event.start_time = form.cleaned_data.get('start_time') 
                    event.end_time = form.cleaned_data.get('end_time')
                    if not event.wedding: 
                         event.wedding = wedding
                    event.save()
                    # Resposta para AJAX/Fetch
                    if is_json_request or request.headers.get('HX-Request'): # Verifica se é HTMX
                        return JsonResponse({'status': 'success', 'message': 'Evento salvo.'})
                    else: # Resposta para envio normal (menos provável aqui)
                        # Idealmente redirecionar ou retornar algo diferente
                        return redirect(reverse_lazy('scheduler:list')) # Exemplo
                else:
                    # Erro de validação
                    if is_json_request or request.headers.get('HX-Request'):
                        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
                    else:
                        # Se fosse um form normal, renderizaria o form com erros
                        # Mas aqui, vindo do modal, retornar erro JSON é melhor
                         return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


            # Ação: Excluir via Modal (POST do formulário HTMX ou JS do modal)
            elif action == 'delete':
                 event_id = data.get('event_id')
                 if not event_id:
                     resp_kwargs = {'status': 400}
                     if is_json_request or request.headers.get('HX-Request'):
                         return JsonResponse({'status': 'error', 'message': 'ID do evento não fornecido.'}, **resp_kwargs)
                     else:
                         return HttpResponseBadRequest("ID do evento não fornecido.")

                 # CORRIGIDO: Usa 'planner' em vez de 'event_planner'
                 event = get_object_or_404(Event, pk=event_id, planner=planner)
                 event_title = event.title # Guarda para mensagem
                 event.delete()
                 
                 if is_json_request or request.headers.get('HX-Request'):
                     return JsonResponse({'status': 'success', 'message': f'Evento "{event_title}" excluído.'})
                 else:
                     # Redireciona se for um POST normal
                      from django.contrib import messages
                      messages.success(request, f'Evento "{event_title}" excluído.')
                      return redirect(reverse_lazy('scheduler:list')) # Exemplo

            else:
                 resp_kwargs = {'status': 400}
                 if is_json_request or request.headers.get('HX-Request'):
                     return JsonResponse({'status': 'error', 'message': 'Ação POST desconhecida.'}, **resp_kwargs)
                 else:
                    return HttpResponseBadRequest("Ação POST desconhecida.")

        except json.JSONDecodeError:
             # Este erro só acontece se não for POST normal e o JSON for inválido
            return JsonResponse({'status': 'error', 'message': 'JSON inválido recebido.'}, status=400)
        except Wedding.DoesNotExist:
             return JsonResponse({'status': 'error', 'message': 'Casamento não encontrado ou não pertence a si.'}, status=404)
        except Event.DoesNotExist:
             return JsonResponse({'status': 'error', 'message': 'Evento não encontrado ou não pertence a si.'}, status=404)
        except PermissionDenied as e: # Captura erro de permissão do Mixin/get_object
             return JsonResponse({'status': 'error', 'message': str(e)}, status=403) # 403 Forbidden
        except Exception as e:
            import traceback
            traceback.print_exc() 
            return JsonResponse({'status': 'error', 'message': f'Erro interno no servidor: {e}'}, status=500)
            
    else:
        return HttpResponseBadRequest("Método não permitido para esta URL.")
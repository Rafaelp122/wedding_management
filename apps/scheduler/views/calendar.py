# Importações do Django
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseBadRequest, Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView
import json
import traceback
from datetime import datetime

# Importações relativas e de outros apps
from ..models import Event
from apps.weddings.models import Wedding
from ..forms import EventForm

# ---
# MIXIN DE REUTILIZAÇÃO
# ---


class WeddingPlannerMixin(LoginRequiredMixin):
    """
    Mixin para CBVs que atuam sobre um 'Wedding'.

    1. Garante que o usuário esteja logado (via LoginRequiredMixin).
    2. Busca o 'Wedding' pelo 'wedding_id' da URL.
    3. Valida se o 'request.user' é o 'planner' daquele 'Wedding'.
    4. Armazena o objeto 'wedding' em 'self.wedding' para uso nos métodos.
    5. Retorna HttpResponseBadRequest se o casamento não for encontrado
       ou não pertencer ao planner.
    """
    wedding = None

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        try:
            # Tenta carregar o casamento usando o 'wedding_id' da URL
            self.wedding = get_object_or_404(
                Wedding, 
                pk=self.kwargs.get('wedding_id'), 
                planner=request.user
            )
            print(f"DEBUG [CBV Mixin]: Acesso validado ao Casamento ID {self.wedding.id}")
        except Http404:
            # Se não encontrar ou não for o dono, retorna erro
            print(f"ERRO DEBUG [CBV Mixin]: Casamento ID {self.kwargs.get('wedding_id')} não encontrado para planner {request.user.id}")
            return HttpResponseBadRequest("Casamento não encontrado ou não pertence a si.")

        # Se tudo deu certo, continua para o método 'get', 'post', etc.
        return super().dispatch(request, *args, **kwargs)

# ---
# CBVs REATORADAS
# ---


class PartialSchedulerView(WeddingPlannerMixin, TemplateView):
    """
    Substitui a FBV 'partial_scheduler'.

    - Usa WeddingPlannerMixin para validar o acesso.
    - Usa TemplateView para renderizar um template simples.
    """
    template_name = 'scheduler/partials/scheduler_partial.html'

    def get_context_data(self, **kwargs) -> dict:
        # O 'self.wedding' já foi carregado e validado pelo Mixin
        context = super().get_context_data(**kwargs)
        context['wedding'] = self.wedding
        print(f"DEBUG [PartialSchedulerView]: Renderizando parcial para Wedding ID: {self.wedding.id}")
        return context


class ManageEventView(WeddingPlannerMixin, View):
    """
    Substitui a FBV 'manage_event' usando um padrão de roteamento interno.

    - Os métodos 'get' e 'post' agora são "roteadores" limpos.
    - Eles usam dicionários ('get_action_handlers', 'post_action_handlers')
      para mapear a 'action' string diretamente ao método que a executa.
    - A lógica de negócio real permanece em métodos privados (ex: _get_create_form).
    """

    # --- Lógica GET (Roteador + Handlers) ---

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Roteador principal para requisições GET."""
        action = request.GET.get('action')
        print(f"\n--- DEBUG [ManageEventView GET] (Wedding: {self.wedding.id}, Planner: {request.user.id}, Ação: {action}) ---")

        # Mapeia a string 'action' ao método que deve tratá-la
        action_handlers = {
            'get_create_form': self._get_create_form,
            'get_edit_form': self._get_edit_form,
        }

        # Encontra o método handler no dicionário
        handler = action_handlers.get(action)

        if handler:
            return handler(request) # Executa o método encontrado
        else:
            print(f"ERRO DEBUG [ManageEventView GET]: Ação inválida: '{action}'")
            return HttpResponseBadRequest("Ação GET inválida.")

    def _get_create_form(self, request) -> HttpResponse:
        """Handler para 'action=get_create_form'."""
        clicked_date_str = request.GET.get('date')
        initial_data_for_form = {}
        if clicked_date_str:
            try:
                initial_data_for_form['clicked_date'] = datetime.strptime(clicked_date_str, '%Y-%m-%d').date()
                print(f"DEBUG [ManageEventView GET create]: Data inicial={initial_data_for_form['clicked_date']}")
            except ValueError:
                print(f"AVISO DEBUG [ManageEventView GET create]: Data recebida ('{clicked_date_str}') inválida.")

        form = EventForm(**initial_data_for_form)
        context = {
            'form': form,
            'wedding': self.wedding, # self.wedding vem do Mixin
            'action_url': reverse_lazy('scheduler:manage_event', kwargs={'wedding_id': self.wedding.id})
        }
        print("DEBUG [ManageEventView GET create]: Renderizando form.")
        return render(request, 'scheduler/partials/_event_form_modal_content.html', context)

    def _get_edit_form(self, request) -> HttpResponse:
        """Handler para 'action=get_edit_form'."""
        event_id = request.GET.get('event_id')
        print(f"DEBUG [ManageEventView GET edit]: Buscando ID={event_id}")

        event = get_object_or_404(Event, pk=event_id, planner=request.user)
        print(f"DEBUG [ManageEventView GET edit]: Evento '{event.title}' encontrado.")

        form = EventForm(instance=event)
        context = {
            'form': form,
            'wedding': self.wedding, # self.wedding vem do Mixin
            'event': event,
            'action_url': reverse_lazy('scheduler:manage_event', kwargs={'wedding_id': self.wedding.id})
        }
        print("DEBUG [ManageEventView GET edit]: Renderizando form.")
        return render(request, 'scheduler/partials/_event_form_modal_content.html', context)

    # --- Lógica POST (Roteador + Handlers) ---

    def post(self, request, *args, **kwargs) -> JsonResponse:
        """Roteador principal para requisições POST."""
        planner = request.user

        # Mapeia a string 'action' ao método que deve tratá-la
        action_handlers = {
            'move_resize': self._post_move_resize,
            'modal_save': self._post_modal_save,
            'delete': self._post_delete,
        }

        try:
            data = json.loads(request.body)
            action = data.get('action')
            print(f"\n--- DEBUG [ManageEventView POST] (Wedding: {self.wedding.id}, Planner: {planner.id}, Ação: {action}) ---")

            # Encontra o método handler no dicionário
            handler = action_handlers.get(action)

            if handler:
                return handler(data, planner) # Executa o método encontrado
            else:
                print(f"ERRO DEBUG [ManageEventView POST]: Ação desconhecida: '{action}'")
                return JsonResponse({'status': 'error', 'message': 'Ação POST desconhecida.'}, status=400)

        except json.JSONDecodeError:
            print("ERRO DEBUG [ManageEventView POST]: JSON inválido.")
            return JsonResponse({'status': 'error', 'message': 'JSON inválido.'}, status=400)
        except Http404:
            # Esta exceção será para 'Event', já que 'Wedding' foi validado no Mixin
            failed_id = data.get('event_id', 'desconhecido') if 'data' in locals() else 'desconhecido'
            print(f"ERRO DEBUG [ManageEventView POST]: Evento ID {failed_id} não encontrado/não pertence ao planner.")
            return JsonResponse({'status': 'error', 'message': 'Evento não encontrado ou não pertence a si.'}, status=404)
        except Exception as e:
            print("\n!!! ERRO INESPERADO [ManageEventView POST] !!!")
            traceback.print_exc()
            print(f"!!! FIM ERRO INESPERADO !!!\n")
            return JsonResponse({'status': 'error', 'message': f'Erro interno: {type(e).__name__}'}, status=500)

    def _post_move_resize(self, data, planner) -> JsonResponse:
        """Handler para 'action=move_resize'."""
        event_id = data.get('event_id')
        start_time_iso = data.get('start_time')
        end_time_iso = data.get('end_time')
        print(f"DEBUG [ManageEventView POST move_resize]: ID={event_id}")

        event = get_object_or_404(Event, pk=event_id, planner=planner)
        try:
            if start_time_iso: event.start_time = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
            else: raise ValueError("Start time não pode ser nulo.")

            if end_time_iso: event.end_time = datetime.fromisoformat(end_time_iso.replace('Z', '+00:00'))
            else: event.end_time = None

            event.save()
            print(f"DEBUG [ManageEventView POST move_resize OK]: Evento ID {event_id} atualizado.")
            return JsonResponse({'status': 'success', 'message': 'Evento atualizado.'})
        except (ValueError, TypeError) as e:
            print(f"ERRO DEBUG [ManageEventView POST move_resize FALHA]: Formato data/hora: {e}")
            return JsonResponse({'status': 'error', 'message': f'Formato data/hora inválido: {e}'}, status=400)

    def _post_modal_save(self, data, planner) -> JsonResponse:
        """Handler para 'action=modal_save' (Criar ou Editar)."""
        event_id = data.get('event_id')
        print(f"DEBUG [ManageEventView POST modal_save]: ID={event_id}")

        instance = None
        if event_id:
            # Busca para garantir que o evento pertence ao planner antes de editar
            instance = get_object_or_404(Event, pk=event_id, planner=planner)
        else:
            print("DEBUG [ManageEventView POST modal_save]: Criando novo.")

        post_data = data.get('form_data', {})
        print(f"DEBUG [ManageEventView POST modal_save]: Dados form={post_data}")

        form = EventForm(post_data, instance=instance)

        if form.is_valid():
            print("DEBUG [ManageEventView POST modal_save]: Form VÁLIDO.")
            event = form.save(commit=False)
            event.planner = planner
            # A FBV original tinha essa lógica, mantendo
            event.start_time = form.cleaned_data.get('start_time')
            event.end_time = form.cleaned_data.get('end_time')

            # Se for um novo evento, associa ao casamento da URL
            if not event.wedding: 
                event.wedding = self.wedding # self.wedding vem do Mixin

            event.save()

            print(f"DEBUG [ManageEventView POST modal_save OK]: Evento ID {event.id} salvo.")
            return JsonResponse({'status': 'success', 'message': 'Evento salvo.'})
        else:
            print(f"ERRO DEBUG [ManageEventView POST modal_save FALHA]: Form INVÁLIDO: {form.errors.as_json()}")
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def _post_delete(self, data, planner) -> JsonResponse:
        """Handler para 'action=delete'."""
        event_id = data.get('event_id')
        print(f"DEBUG [ManageEventView POST delete]: Tentando ID={event_id}")

        if not event_id:
            print("ERRO DEBUG [ManageEventView POST delete]: ID não fornecido.")
            return JsonResponse({'status': 'error', 'message': 'ID do evento não fornecido.'}, status=400)

        event = get_object_or_404(Event, pk=event_id, planner=planner)
        event_title = event.title
        event.delete()

        print(f"DEBUG [ManageEventView POST delete OK]: Evento ID {event_id} ('{event_title}') excluído.")
        return JsonResponse({'status': 'success', 'message': 'Evento excluído.'})

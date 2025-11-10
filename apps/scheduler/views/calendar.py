import json
import traceback
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View

from apps.weddings.models import Wedding

from ..forms import EventForm
from ..models import Event


class WeddingPlannerMixin(LoginRequiredMixin):
    """
    Mixin usado em CBVs que trabalham com um 'Wedding'.
    Garante que o usuário logado é o planner responsável pelo casamento.
    """

    wedding = None

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        # Verifica se o casamento pertence ao planner logado
        try:
            self.wedding = get_object_or_404(
                Wedding, pk=self.kwargs.get("wedding_id"), planner=request.user
            )
            print(f"DEBUG [CBV Mixin]: Acesso validado ao Casamento ID {self.wedding.id}")
        except Http404:
            print(
                f"ERRO DEBUG [CBV Mixin]: Casamento ID {self.kwargs.get('wedding_id')} não encontrado para planner {request.user.id}"
            )
            return HttpResponseBadRequest(
                "Casamento não encontrado ou não pertence a si."
            )

        # Continua o fluxo normal da view
        return super().dispatch(request, *args, **kwargs)


class PartialSchedulerView(WeddingPlannerMixin, TemplateView):
    """Renderiza o calendário parcial com base no casamento atual."""

    template_name = "scheduler/partials/scheduler_partial.html"

    def get_context_data(self, **kwargs) -> dict:
        # Adiciona o casamento validado no contexto
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.wedding
        print(
            f"DEBUG [PartialSchedulerView]: Renderizando parcial para Wedding ID: {self.wedding.id}"
        )
        return context


class ManageEventView(WeddingPlannerMixin, View):
    """View principal que gerencia a criação, edição, movimentação e exclusão de eventos."""

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Roteia as requisições GET para o método correto."""
        action = request.GET.get("action")
        print(
            f"\n--- DEBUG [ManageEventView GET] (Wedding: {self.wedding.id}, Planner: {request.user.id}, Ação: {action}) ---"
        )

        # Dicionário de ações válidas para GET
        action_handlers = {
            "get_create_form": self._get_create_form,
            "get_edit_form": self._get_edit_form,
        }

        handler = action_handlers.get(action)
        if handler:
            return handler(request)
        else:
            print(f"ERRO DEBUG [ManageEventView GET]: Ação inválida: '{action}'")
            return HttpResponseBadRequest("Ação GET inválida.")

    def _get_create_form(self, request) -> HttpResponse:
        """Exibe o formulário de criação de evento."""
        clicked_date_str = request.GET.get("date")
        initial_data_for_form = {}

        # Define a data inicial caso o usuário tenha clicado em um dia no calendário
        if clicked_date_str:
            try:
                initial_data_for_form["clicked_date"] = datetime.strptime(
                    clicked_date_str, "%Y-%m-%d"
                ).date()
                print(
                    f"DEBUG [ManageEventView GET create]: Data inicial={initial_data_for_form['clicked_date']}"
                )
            except ValueError:
                print(
                    f"AVISO DEBUG [ManageEventView GET create]: Data recebida ('{clicked_date_str}') inválida."
                )

        form = EventForm(**initial_data_for_form)
        context = {
            "form": form,
            "wedding": self.wedding,
            "action_url": reverse_lazy(
                "scheduler:manage_event", kwargs={"wedding_id": self.wedding.id}
            ),
        }
        print("DEBUG [ManageEventView GET create]: Renderizando form.")
        return render(
            request, "scheduler/partials/_event_form_modal_content.html", context
        )

    def _get_edit_form(self, request) -> HttpResponse:
        """Exibe o formulário de edição de evento existente."""
        event_id = request.GET.get("event_id")
        print(f"DEBUG [ManageEventView GET edit]: Buscando ID={event_id}")

        event = get_object_or_404(Event, pk=event_id, planner=request.user)
        print(f"DEBUG [ManageEventView GET edit]: Evento '{event.title}' encontrado.")

        form = EventForm(instance=event)
        context = {
            "form": form,
            "wedding": self.wedding,
            "event": event,
            "action_url": reverse_lazy(
                "scheduler:manage_event", kwargs={"wedding_id": self.wedding.id}
            ),
        }
        print("DEBUG [ManageEventView GET edit]: Renderizando form.")
        return render(
            request, "scheduler/partials/_event_form_modal_content.html", context
        )

    def post(self, request, *args, **kwargs) -> JsonResponse:
        """Roteia as requisições POST para o método correto."""
        planner = request.user

        action_handlers = {
            "move_resize": self._post_move_resize,
            "modal_save": self._post_modal_save,
            "delete": self._post_delete,
        }

        try:
            data = json.loads(request.body)
            action = data.get("action")
            print(
                f"\n--- DEBUG [ManageEventView POST] (Wedding: {self.wedding.id}, Planner: {planner.id}, Ação: {action}) ---"
            )

            handler = action_handlers.get(action)
            if handler:
                return handler(data, planner)
            else:
                print(
                    f"ERRO DEBUG [ManageEventView POST]: Ação desconhecida: '{action}'"
                )
                return JsonResponse(
                    {"status": "error", "message": "Ação POST desconhecida."},
                    status=400,
                )

        except json.JSONDecodeError:
            print("ERRO DEBUG [ManageEventView POST]: JSON inválido.")
            return JsonResponse(
                {"status": "error", "message": "JSON inválido."}, status=400
            )
        except Http404:
            failed_id = (
                data.get("event_id", "desconhecido")
                if "data" in locals()
                else "desconhecido"
            )
            print(
                f"ERRO DEBUG [ManageEventView POST]: Evento ID {failed_id} não encontrado/não pertence ao planner."
            )
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Evento não encontrado ou não pertence a si.",
                },
                status=404,
            )
        except Exception as e:
            # Captura erros inesperados e retorna 500
            print("\n!!! ERRO INESPERADO [ManageEventView POST] !!!")
            traceback.print_exc()
            print(f"!!! FIM ERRO INESPERADO !!!\n")
            return JsonResponse(
                {"status": "error", "message": f"Erro interno: {type(e).__name__}"},
                status=500,
            )

    def _post_move_resize(self, data, planner) -> JsonResponse:
        """Atualiza a posição ou duração de um evento no calendário."""
        event_id = data.get("event_id")
        start_time_iso = data.get("start_time")
        end_time_iso = data.get("end_time")
        print(f"DEBUG [ManageEventView POST move_resize]: ID={event_id}")

        event = get_object_or_404(Event, pk=event_id, planner=planner)
        try:
            if start_time_iso:
                event.start_time = datetime.fromisoformat(
                    start_time_iso.replace("Z", "+00:00")
                )
            else:
                raise ValueError("Start time não pode ser nulo.")

            if end_time_iso:
                event.end_time = datetime.fromisoformat(
                    end_time_iso.replace("Z", "+00:00")
                )
            else:
                event.end_time = None

            event.save()
            print(
                f"DEBUG [ManageEventView POST move_resize OK]: Evento ID {event_id} atualizado."
            )
            return JsonResponse({"status": "success", "message": "Evento atualizado."})
        except (ValueError, TypeError) as e:
            print(
                f"ERRO DEBUG [ManageEventView POST move_resize FALHA]: Formato data/hora: {e}"
            )
            return JsonResponse(
                {"status": "error", "message": f"Formato data/hora inválido: {e}"},
                status=400,
            )

    def _post_modal_save(self, data, planner) -> JsonResponse:
        """Cria ou atualiza um evento a partir do modal."""
        event_id = data.get("event_id")
        print(f"DEBUG [ManageEventView POST modal_save]: ID={event_id}")

        instance = None
        if event_id:
            instance = get_object_or_404(Event, pk=event_id, planner=planner)
        else:
            print("DEBUG [ManageEventView POST modal_save]: Criando novo.")

        post_data = data.get("form_data", {})
        print(f"DEBUG [ManageEventView POST modal_save]: Dados form={post_data}")

        form = EventForm(post_data, instance=instance)

        if form.is_valid():
            print("DEBUG [ManageEventView POST modal_save]: Form VÁLIDO.")
            event = form.save(commit=False)
            event.planner = planner
            event.start_time = form.cleaned_data.get("start_time")
            event.end_time = form.cleaned_data.get("end_time")

            if not event.wedding:
                event.wedding = self.wedding

            event.save()
            print(
                f"DEBUG [ManageEventView POST modal_save OK]: Evento ID {event.id} salvo."
            )
            return JsonResponse({"status": "success", "message": "Evento salvo."})
        else:
            print(
                f"ERRO DEBUG [ManageEventView POST modal_save FALHA]: Form INVÁLIDO: {form.errors.as_json()}"
            )
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)

    def _post_delete(self, data, planner) -> JsonResponse:
        """Exclui um evento existente."""
        event_id = data.get("event_id")
        print(f"DEBUG [ManageEventView POST delete]: Tentando ID={event_id}")

        if not event_id:
            print("ERRO DEBUG [ManageEventView POST delete]: ID não fornecido.")
            return JsonResponse(
                {"status": "error", "message": "ID do evento não fornecido."},
                status=400,
            )

        event = get_object_or_404(Event, pk=event_id, planner=planner)
        event_title = event.title
        event.delete()

        print(
            f"DEBUG [ManageEventView POST delete OK]: Evento ID {event_id} ('{event_title}') excluído."
        )
        return JsonResponse({"status": "success", "message": "Evento excluído."})

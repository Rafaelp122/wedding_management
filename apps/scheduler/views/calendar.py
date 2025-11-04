from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.contrib.auth.decorators import login_required
import json
import traceback
from datetime import datetime

# Importações relativas e de outros apps
from ..models import Event
from apps.weddings.models import Wedding
from ..forms import EventForm


@login_required
def partial_scheduler(request, wedding_id):
    planner = request.user
    try:
        current_wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)
        print(f"DEBUG partial_scheduler: Carregando parcial para Wedding ID: {current_wedding.id}") 
        context = {'wedding': current_wedding}
    except Http404:
        print(f"ERRO DEBUG partial_scheduler: Casamento ID {wedding_id} não encontrado para planner {planner.id}") 
        return HttpResponseBadRequest("Casamento não encontrado ou não pertence a si.")

    return render(request, 'scheduler/partials/scheduler_partial.html', context)


@login_required
def manage_event(request, wedding_id):
    planner = request.user
    wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)
    print(f"\n--- DEBUG manage_event (Wedding: {wedding_id}, Planner: {planner.id}, Método: {request.method}) ---") 

    if request.method == 'GET':
        action = request.GET.get('action')
        print(f"DEBUG manage_event [GET]: Ação={action}") 

        if action == 'get_create_form':
            clicked_date_str = request.GET.get('date')
            initial_data_for_form = {}
            if clicked_date_str:
                try:
                    initial_data_for_form['clicked_date'] = datetime.strptime(clicked_date_str, '%Y-%m-%d').date()
                    print(f"DEBUG manage_event [GET create]: Data inicial (via clicked_date)={initial_data_for_form['clicked_date']}") 
                except ValueError:
                    print(f"AVISO DEBUG manage_event [GET create]: Data recebida ('{clicked_date_str}') inválida.") 
                    pass
            form = EventForm(**initial_data_for_form) 
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
            object_type = "Casamento" if 'Wedding' in str(e) else "Evento"
            failed_id = wedding_id if object_type == "Casamento" else data.get('event_id', 'desconhecido')
            print(f"ERRO DEBUG manage_event [POST]: {object_type} ID {failed_id} não encontrado/não pertence ao planner.")
            return JsonResponse({'status': 'error', 'message': f'{object_type} não encontrado ou não pertence a si.'}, status=4404)
        except Exception as e:
            print("\n!!! ERRO INESPERADO manage_event (POST) !!!") 
            traceback.print_exc() 
            print(f"!!! FIM ERRO INESPERADO !!!\n") 
            return JsonResponse({'status': 'error', 'message': f'Erro interno: {type(e).__name__}'}, status=500)

    else:
        print(f"ERRO DEBUG manage_event: Método '{request.method}' não permitido.")
        return HttpResponseBadRequest(f"Método '{request.method}' não permitido.")

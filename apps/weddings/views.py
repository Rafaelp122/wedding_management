from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import WeddingForm
from .models import Wedding

GRADIENTS = [
    "linear-gradient(135deg, #8e2de2, #4a00e0)",
    "linear-gradient(135deg, #7b1fa2, #512da8)",
    "linear-gradient(135deg, #e91e63, #ff6f61)",
    "linear-gradient(135deg, #009688, #00695c)",
    "linear-gradient(135deg, #3f51b5, #1a237e)",
    "linear-gradient(135deg, #ff9800, #ef6c00)",
    "linear-gradient(135deg, #2196f3, #0d47a1)",
    "linear-gradient(135deg, #4caf50, #1b5e20)",
    "linear-gradient(135deg, #f44336, #b71c1c)",
    "linear-gradient(135deg, #ffeb3b, #fbc02d)",
    "linear-gradient(135deg, #00bcd4, #00838f)",
    "linear-gradient(135deg, #9c27b0, #4a148c)",
    "linear-gradient(135deg, #cddc39, #827717)",
    "linear-gradient(135deg, #795548, #3e2723)",
    "linear-gradient(135deg, #607d8b, #263238)",
    "linear-gradient(135deg, #673ab7, #311b92)",
    "linear-gradient(135deg, #ff5722, #bf360c)",
    "linear-gradient(135deg, #03a9f4, #01579b)",
    "linear-gradient(135deg, #76ff03, #33691e)",
]

class PlannerOwnerMixin:
    """ Mixin que filtra os resultados para mostrar apenas os dados do planner logado. """
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(planner=self.request.user)


class WeddingListView(LoginRequiredMixin, PlannerOwnerMixin, ListView):
    model = Wedding
    template_name = "weddings/list.html"
    context_object_name = "weddings"  # <-- Pode manter, mas veja a próxima função

    def get_queryset(self):
        queryset = super().get_queryset()

        # REMOVIDO: .select_related("client")
        queryset = queryset.annotate(
            items_count=Count('item', distinct=True),
            contracts_count=Count('contract', distinct=True)
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        weddings = self.object_list

        # Renomeei 'weddings_with_clients' para 'wedding_items' para ficar mais claro
        context["wedding_items"] = [
            {
                "wedding": wedding,
                # REMOVIDO: "client": wedding.client,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
            }
            for idx, wedding in enumerate(weddings)
        ]
        
        # Você pode remover o 'context_object_name' e usar só 'wedding_items' no template
        # Ou manter ambos, se preferir.
        
        return context


class WeddingCreateView(LoginRequiredMixin, CreateView):
    model = Wedding
    form_class = WeddingForm
    template_name = 'weddings/partials/_create_wedding_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_layout_dict'] = {
            # REMOVIDO: 'client': 'col-md-12',
            'groom_name': 'col-md-6',
            'bride_name': 'col-md-6',
            'date': 'col-md-6',
            'location': 'col-md-12',
            'budget': 'col-md-6',
        }

        context['default_col_class'] = 'col-12'

        context['form_icons'] = {
            # REMOVIDO: 'client': 'fas fa-id-card',
            'groom_name': 'fas fa-user',
            'bride_name': 'fas fa-user',
            'date': 'fas fa-calendar-days',
            'location': 'fas fa-location-dot',
            'budget': 'fas fa-money-bill-wave',
        }
        return context

    def form_valid(self, form):
        form.instance.planner = self.request.user
        new_wedding = form.save()

        total_weddings = Wedding.objects.filter(planner=self.request.user).count()
        new_card_index = total_weddings - 1

        item_context = {
            'wedding': new_wedding,
            # REMOVIDO: 'client': new_wedding.client,
            'gradient': GRADIENTS[new_card_index % len(GRADIENTS)],
            'items_count': 0,
            'contracts_count': 0,
            'progress': 0
        }

        html = render_to_string(
            'weddings/partials/_wedding_card.html',
            {'item': item_context}
        )
        response = HttpResponse(html)
        response['HX-Trigger'] = '{"weddingCreated": {}, "removeEmptyMessage": {}}'
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 422
        response['HX-Retarget'] = '#modal-container'
        response['HX-Reswap'] = 'innerHTML'
        return response


class WeddingDetailView(LoginRequiredMixin, PlannerOwnerMixin, DetailView):
    model = Wedding
    template_name = "weddings/detail.html"
    context_object_name = "wedding"
    pk_url_kwarg = 'wedding_id'


class WeddingUpdateView(LoginRequiredMixin, PlannerOwnerMixin, UpdateView):
    model = Wedding
    form_class = WeddingForm
    template_name = "weddings/edit.html"
    success_url = reverse_lazy("weddings:my_weddings")
    pk_url_kwarg = 'id'


class WeddingDeleteView(LoginRequiredMixin, PlannerOwnerMixin, DeleteView):
    model = Wedding
    template_name = "weddings/confirm_delete.html"  
    success_url = reverse_lazy("weddings:my_weddings")
    pk_url_kwarg = 'id'
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

from apps.core.utils.constants import GRADIENTS

from .forms import WeddingForm
from .models import Wedding


class PlannerOwnerMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(planner=self.request.user)


class WeddingListView(LoginRequiredMixin, PlannerOwnerMixin, ListView):
    model = Wedding
    template_name = "weddings/list.html"
    context_object_name = "weddings"

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.order_by('id')

        queryset = queryset.select_related("client").annotate(
            items_count=Count('item', distinct=True),
            contracts_count=Count('contract', distinct=True)
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        weddings = self.object_list

        context["weddings_with_clients"] = [
            {
                "wedding": wedding,
                "client": wedding.client,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
            }
            for idx, wedding in enumerate(weddings)
        ]
        return context


class WeddingCreateView(LoginRequiredMixin, CreateView):
    model = Wedding
    form_class = WeddingForm
    template_name = "weddings/partials/_create_wedding_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["form_layout_dict"] = {
            "client": "col-md-12",
            "groom_name": "col-md-6",
            "bride_name": "col-md-6",
            "date": "col-md-6",
            "location": "col-md-12",
            "budget": "col-md-6",
        }

        context["default_col_class"] = "col-12"

        context["form_icons"] = {
            "client": "fas fa-id-card",
            "groom_name": "fas fa-user",
            "bride_name": "fas fa-user",
            "date": "fas fa-calendar-days",
            "location": "fas fa-location-dot",
            "budget": "fas fa-money-bill-wave",
        }

        return context

    def form_valid(self, form):
        form.instance.planner = self.request.user
        new_wedding = form.save()

        total_weddings = Wedding.objects.filter(planner=self.request.user).count()
        new_card_index = total_weddings - 1

        item_context = {
            "wedding": new_wedding,
            "client": new_wedding.client,
            "gradient": GRADIENTS[new_card_index % len(GRADIENTS)],
            "items_count": 0,
            "contracts_count": 0,
            "progress": 0,
        }

        html = render_to_string(
            "weddings/partials/_wedding_card.html",
            {"item": item_context},
            request=self.request,
        )

        response = HttpResponse(html)

        response["HX-Retarget"] = "#wedding-list-container"
        response["HX-Reswap"] = "beforeend"
        response["HX-Trigger"] = '{"weddingCreated": {}, "removeEmptyMessage": {}}'
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response


class WeddingUpdateView(LoginRequiredMixin, PlannerOwnerMixin, UpdateView):
    model = Wedding
    form_class = WeddingForm
    template_name = "weddings/partials/_create_wedding_form.html"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["form_layout_dict"] = {
            "client": "col-md-12",
            "groom_name": "col-md-6",
            "bride_name": "col-md-6",
            "date": "col-md-6",
            "location": "col-md-12",
            "budget": "col-md-6",
        }

        context["default_col_class"] = "col-12"

        context["form_icons"] = {
            "client": "fas fa-id-card",
            "groom_name": "fas fa-user",
            "bride_name": "fas fa-user",
            "date": "fas fa-calendar-days",
            "location": "fas fa-location-dot",
            "budget": "fas fa-money-bill-wave",
        }

        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response

    def form_valid(self, form):
        updated_wedding = form.save()

        planner_weddings = list(
            Wedding.objects.filter(
                planner=self.request.user
            ).order_by(
                'id'
            ).values_list(
                'pk', flat=True
            ))

        card_index = planner_weddings.index(updated_wedding.pk)

        item_context = {
            'wedding': updated_wedding,
            'client': updated_wedding.client,
            'gradient': GRADIENTS[card_index % len(GRADIENTS)],
            'items_count': updated_wedding.item_set.count(),
            'contracts_count': updated_wedding.contract_set.count(),
            'progress': 0
        }

        html = render_to_string(
            "weddings/partials/_wedding_card.html",
            {"item": item_context},
            request=self.request,
        )

        response = HttpResponse(html)

        # Retarget para o card específico que foi editado
        response['HX-Retarget'] = f'#wedding-card-{updated_wedding.pk}'
        # Substitui o card antigo pelo novo
        response['HX-Reswap'] = 'outerHTML'
        # Fecha o modal
        response['HX-Trigger'] = '{"weddingCreated": {}}'

        return response


class WeddingDetailView(LoginRequiredMixin, PlannerOwnerMixin, DetailView):
    model = Wedding
    template_name = "weddings/detail.html"
    context_object_name = "wedding"
    pk_url_kwarg = "wedding_id"


class WeddingDeleteView(LoginRequiredMixin, PlannerOwnerMixin, DeleteView):
    model = Wedding
    template_name = "weddings/confirm_delete.html"
    success_url = reverse_lazy("weddings:my_weddings")
    pk_url_kwarg = "id"

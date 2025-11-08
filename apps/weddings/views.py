from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
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

        queryset = queryset.annotate(
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
            "groom_name": "col-md-6",
            "bride_name": "col-md-6",
            "date": "col-md-6",
            "location": "col-md-12",
            "budget": "col-md-6",
        }

        context["default_col_class"] = "col-12"

        context["form_icons"] = {
            "groom_name": "fas fa-user",
            "bride_name": "fas fa-user",
            "date": "fas fa-calendar-days",
            "location": "fas fa-location-dot",
            "budget": "fas fa-money-bill-wave",
        }

        return context

    def form_valid(self, form):
        form.instance.planner = self.request.user
        # Esta variável está sendo usada, nao remover
        new_wedding = form.save()

        queryset = Wedding.objects.filter(planner=self.request.user)
        queryset = queryset.order_by('id')
        queryset = queryset.annotate(
            items_count=Count('item', distinct=True),
            contracts_count=Count('contract', distinct=True)
        )

        weddings_with_clients = [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
            }
            for idx, wedding in enumerate(queryset)
        ]

        context = {
            "weddings_with_clients": weddings_with_clients
        }

        html = render_to_string(
            "weddings/partials/_wedding_list_content.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)
        response["HX-Retarget"] = '#wedding-list-container'
        response["HX-Reswap"] = 'innerHTML'
        response["HX-Trigger-After-Swap"] = 'weddingCreated'
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
            "groom_name": "col-md-6",
            "bride_name": "col-md-6",
            "date": "col-md-6",
            "location": "col-md-12",
            "budget": "col-md-6",
        }

        context["default_col_class"] = "col-12"

        context["form_icons"] = {
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
        # Esta variável está sendo usada, nao remover
        updated_wedding = form.save()

        queryset = Wedding.objects.filter(planner=self.request.user)
        queryset = queryset.order_by('id')
        queryset = queryset.annotate(
            items_count=Count('item', distinct=True),
            contracts_count=Count('contract', distinct=True)
        )

        weddings_with_clients = [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
            }
            for idx, wedding in enumerate(queryset)
        ]

        context = {
            "weddings_with_clients": weddings_with_clients
        }

        html = render_to_string(
            "weddings/partials/_wedding_list_content.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)
        response["HX-Retarget"] = '#wedding-list-container'
        response["HX-Reswap"] = 'innerHTML'
        response["HX-Trigger-After-Swap"] = 'weddingCreated'
        return response


class WeddingDeleteView(LoginRequiredMixin, PlannerOwnerMixin, DeleteView):
    model = Wedding
    template_name = "partials/confirm_delete_modal.html"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Variáveis passadas para o modal de deleção reutilizável
        context['object_name'] = str(self.object)
        context['object_type'] = 'o casamento'
        context['hx_post_url'] = reverse(
            'weddings:delete_wedding',
            kwargs={'id': self.object.pk}
        )

        context['hx_target_id'] = '#wedding-list-container'

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user

        self.object = self.get_object()
        self.object.delete()

        queryset = Wedding.objects.filter(planner=user)
        queryset = queryset.order_by('id')
        queryset = queryset.annotate(
            items_count=Count('item', distinct=True),
            contracts_count=Count('contract', distinct=True)
        )

        weddings_with_clients = [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
            }
            for idx, wedding in enumerate(queryset)
        ]

        context = {"weddings_with_clients": weddings_with_clients}

        html = render_to_string(
            "weddings/partials/_wedding_list_content.html",
            context
        )

        response = HttpResponse(html)
        response["HX-Trigger-After-Swap"] = 'weddingCreated'
        return response


class WeddingDetailView(LoginRequiredMixin, PlannerOwnerMixin, DetailView):
    model = Wedding
    template_name = "weddings/detail.html"
    context_object_name = "wedding"
    pk_url_kwarg = "wedding_id"

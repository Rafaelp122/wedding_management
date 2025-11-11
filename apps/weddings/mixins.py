from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.db.models import Case, CharField, Count, Q, Value, When
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from apps.core.utils.constants import GRADIENTS

from .forms import WeddingForm
from .models import Wedding


class WeddingBaseMixin(LoginRequiredMixin):
    """
    Unifica:
    - filtro por planner
    - order_by
    - annotate (items_count, contracts_count)
    - geração de weddings_with_clients
    - paginação
    - renderização HTMX da lista
    """

    # Define a quantidade de itens por página
    paginate_by = 6

    def get_queryset(self):
        """
        Método de segurança padrão (usado por UpdateView, DeleteView).
        Garante que o usuário só pode operar em seus próprios objetos.
        """

        if not hasattr(self, 'model'):
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing a 'model' attribute."
            )

        queryset = self.model.objects.all()

        return queryset.filter(planner=self.request.user)

    def get_base_queryset(self):
        sort_option = self.request.GET.get('sort', 'id')
        search_query = self.request.GET.get('q', None)

        # --- NOVO: Pega o filtro de status da URL ---
        status_filter = self.request.GET.get('status', None)

        queryset = Wedding.objects.filter(planner=self.request.user)
        today = timezone.now().date()

        queryset = queryset.annotate(
            effective_status=Case(
                When(status='CANCELED', then=Value('CANCELED')),
                When(status='COMPLETED', then=Value('COMPLETED')),
                When(date__lt=today, then=Value('COMPLETED')),
                default=Value('IN_PROGRESS'),
                output_field=CharField()
            )
        )

        if search_query:
            queryset = queryset.filter(
                Q(groom_name__icontains=search_query) |
                Q(bride_name__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(effective_status=status_filter)

        if sort_option == 'date_desc':
            order_by_field = '-date'
        elif sort_option == 'date_asc':
            order_by_field = 'date'
        elif sort_option == 'name_asc':
            order_by_field = 'groom_name'
        else:
            order_by_field = 'id'

        return (
            queryset
            .order_by(order_by_field)
            .annotate(
                items_count=Count("item", distinct=True),
                contracts_count=Count("contract", distinct=True),
            )
        )

    def build_weddings_with_clients(self, queryset=None):
        qs = queryset if queryset is not None else self.get_base_queryset()
        return [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
                "effective_status": wedding.effective_status,
                # "progress": wedding.progress,
            }
            for idx, wedding in enumerate(qs)
        ]

    def render_wedding_list_response(self, trigger="listUpdated"):
        # Pega o queryset completo, filtrado e ordenado
        full_queryset = self.get_base_queryset()

        # Pagina o queryset
        paginator = Paginator(full_queryset, self.paginate_by)
        page_number = self.request.GET.get('page', 1)  # Pega a página da URL
        page_obj = paginator.get_page(page_number)

        # Formata APENAS os itens da página atual
        paginated_weddings_formatted = self.build_weddings_with_clients(
            queryset=page_obj.object_list
        )

        # Constrói o contexto para os parciais
        context = {
            "page_obj": page_obj,
            "paginated_weddings": paginated_weddings_formatted,
            "current_sort": self.request.GET.get('sort', 'id'),
            "current_search": self.request.GET.get('q', ''),
            "request": self.request  # Passa o request para o partial
        }

        # Renderiza o template que contém a LISTA + PAGINAÇÃO (OOB)
        html = render_to_string(
            "weddings/partials/_list_and_pagination.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)
        response["HX-Retarget"] = '#wedding-list-container'
        response["HX-Reswap"] = 'innerHTML'

        response["HX-Trigger-After-Swap"] = trigger
        return response


class WeddingFormLayoutMixin:
    """
    Define o layout e ícones para o formulário de Casamento.
    """
    form_class = WeddingForm
    template_name = "weddings/partials/_create_wedding_form.html"

    form_layout_dict = {
        "groom_name": "col-md-6",
        "bride_name": "col-md-6",
        "date": "col-md-6",
        "location": "col-md-12",
        "budget": "col-md-6",
    }
    default_col_class = "col-12"
    form_icons = {
        "groom_name": "fas fa-user",
        "bride_name": "fas fa-user",
        "date": "fas fa-calendar-days",
        "location": "fas fa-location-dot",
        "budget": "fas fa-money-bill-wave",
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_layout_dict"] = self.form_layout_dict
        ctx["default_col_class"] = self.default_col_class
        ctx["form_icons"] = self.form_icons
        return ctx

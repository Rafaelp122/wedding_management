from django.db import models
from django.db.models import Case, CharField, Count, F, IntegerField, Q, Value, When
from django.utils import timezone

from apps.users.models import User


class WeddingQuerySet(models.QuerySet):
    """
    QuerySet customizado para o modelo Wedding,
    contém toda a lógica de negócio de filtragem e anotação.
    """

    def with_counts_and_progress(self):
        """
        Anota o queryset com contagens de itens, contratos,
        e o progresso calculado (baseado nos itens 'DONE').
        """
        return self.annotate(
            # Conta o total de itens
            items_count=Count("item", distinct=True),

            # Conta o total de contratos
            contracts_count=Count("contract", distinct=True),

            # Conta apenas itens "Concluídos"
            done_items_count=Count(
                'item',
                filter=Q(item__status='DONE'),
                distinct=True
            ),

            # Calcula a porcentagem (0-100)
            progress=Case(
                # Se não houver itens, o progresso é 0
                When(items_count=0, then=Value(0)),
                # Caso contrário, calcula (Concluídos * 100) / Total
                default=(
                    (F('done_items_count') * 100) / F('items_count')
                ),
                output_field=IntegerField()
            )
        )

    def with_effective_status(self):
        """Anota o status 'real' (manual ou automático pela data)"""
        today = timezone.now().date()
        return self.annotate(
            effective_status=Case(
                When(status='CANCELED', then=Value('CANCELED')),
                When(status='COMPLETED', then=Value('COMPLETED')),
                When(date__lt=today, then=Value('COMPLETED')),
                default=Value('IN_PROGRESS'),
                output_field=CharField()
            )
        )

    def apply_search(self, search_query):
        """Filtra por nome do noivo ou noiva"""
        if search_query:
            return self.filter(
                Q(groom_name__icontains=search_query) |
                Q(bride_name__icontains=search_query)
            )
        return self  # Retorna o queryset inalterado

    def apply_sort(self, sort_option):
        """Ordena o queryset com base na opção de sort"""
        if sort_option == 'date_desc':
            order_by_field = '-date'
        elif sort_option == 'date_asc':
            order_by_field = 'date'
        elif sort_option == 'name_asc':
            order_by_field = 'groom_name'
        else:
            order_by_field = 'id'
        return self.order_by(order_by_field)


class Wedding(models.Model):
    planner = models.ForeignKey(User, on_delete=models.CASCADE)
    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'Em Andamento'),
        ('COMPLETED', 'Concluído'),
        ('CANCELED', 'Cancelado'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='IN_PROGRESS'
    )

    objects = WeddingQuerySet.as_manager()

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name}"

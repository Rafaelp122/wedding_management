from django.db import models
from django.db.models import (
    Case,
    CharField,
    Count,
    F,
    IntegerField,
    Q,
    Value,
    When,
    Subquery,
    OuterRef,
)
from django.utils import timezone
from django.db.models.functions import Coalesce


class WeddingQuerySet(models.QuerySet):
    """
    QuerySet customizado para o modelo Wedding,
    otimizado com Subqueries para contagens de performance.
    """

    def with_counts_and_progress(self):
        """
        Anota o queryset com contagens e progresso,
        usando Subqueries para performance e precisão.
        """

        # Colocado aqui para evitar import circular
        from apps.items.models import Item
        from apps.contracts.models import Contract

        # Subquery para contar TODOS os itens do casamento
        # OuterRef('pk') refere-se ao 'id' do Wedding na consulta principal
        item_count_sq = Subquery(
            Item.objects.filter(wedding=OuterRef("pk"))
            .values("wedding")  # Agrupa pela FK
            .annotate(c=Count("pk"))  # Conta os itens
            .values("c")
        )

        # Subquery para contar itens 'DONE'
        done_item_count_sq = Subquery(
            Item.objects.filter(wedding=OuterRef("pk"), status="DONE")
            .values("wedding")
            .annotate(c=Count("pk"))
            .values("c")
        )

        # Subquery para contar contratos
        contract_count_sq = Subquery(
            Contract.objects.filter(wedding=OuterRef("pk"))
            .values("wedding")
            .annotate(c=Count("pk"))
            .values("c")
        )

        # Primeiro .annotate() com as contagens
        # Usamos Coalesce para garantir que o valor seja 0 em vez de None
        # se não houver itens/contratos, evitando erros no cálculo.
        annotated_queryset = self.annotate(
            items_count=Coalesce(item_count_sq, 0, output_field=IntegerField()),
            done_items_count=Coalesce(
                done_item_count_sq, 0, output_field=IntegerField()
            ),
            contracts_count=Coalesce(contract_count_sq, 0, output_field=IntegerField()),
        )

        # Segundo .annotate() para calcular o progresso
        return annotated_queryset.annotate(
            progress=Case(
                When(items_count=0, then=Value(0)),
                default=((F("done_items_count") * 100) / F("items_count")),
                output_field=IntegerField(),
            )
        )

    def with_effective_status(self):
        """Anota o status 'real' (manual ou automático pela data)"""
        today = timezone.now().date()
        return self.annotate(
            effective_status=Case(
                When(status="CANCELED", then=Value("CANCELED")),
                When(status="COMPLETED", then=Value("COMPLETED")),
                When(date__lt=today, then=Value("COMPLETED")),
                default=Value("IN_PROGRESS"),
                output_field=CharField(),
            )
        )

    def apply_search(self, search_query):
        """
        Filtra por nome do noivo ou noiva (otimizado com 'istartswith')
        """
        if search_query:
            # 'istartswith' (LIKE 'query%') é muito mais rápido que
            # 'icontains' (LIKE '%query%') pois usa índices do DB.
            return self.filter(
                Q(groom_name__istartswith=search_query)
                | Q(bride_name__istartswith=search_query)
            )
        return self

    def apply_sort(self, sort_option):
        """Ordena o queryset com base na opção de sort (refatorado)"""

        SORT_MAP = {
            "date_desc": "-date",
            "date_asc": "date",
            "name_asc": "groom_name",
        }

        # .get() busca a opção no mapa. Se não encontrar,
        # usa o valor padrão 'id'.
        order_by_field = SORT_MAP.get(sort_option, "id")

        return self.order_by(order_by_field)

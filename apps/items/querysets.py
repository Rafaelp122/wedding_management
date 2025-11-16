from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Sum


class ItemQuerySet(models.QuerySet):
    """QuerySet personalizado com métodos de cálculo para os itens"""

    def total_spent(self):
        """Calcula o custo total dos itens neste QuerySet."""
        total = self.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("unit_price") * F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
        )["total"]
        return total or 0

    def category_expenses(self):
        """Agrupa os custos por categoria e retorna o total de cada uma."""
        return (
            self.values("category")
            .annotate(
                total_cost=Sum(
                    ExpressionWrapper(
                        F("unit_price") * F("quantity"),
                        output_field=DecimalField(max_digits=10, decimal_places=2),
                    )
                )
            )
            .order_by("-total_cost")
        )

    def apply_search(self, search_query):
        """Filtra por nome do item (otimizado com istartswith)"""
        if search_query:
            return self.filter(name__istartswith=search_query)
        return self

    def apply_sort(self, sort_option):
        """Ordena o queryset de itens (refatorado com um mapa)"""

        # Mapeia as opções de string para os campos reais do DB
        SORT_MAP = {
            "name_asc": "name",
            "status": "status",
            "price_desc": "-unit_price",
            "price_asc": "unit_price",
            "date_desc": "-created_at",
            "date_asc": "created_at",
        }

        # .get() busca a opção no mapa.
        # Se não encontrar, usa o valor padrão ('id').
        order_by_field = SORT_MAP.get(sort_option, "id")

        return self.order_by(order_by_field)

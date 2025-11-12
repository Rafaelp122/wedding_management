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
                        output_field=DecimalField(
                            max_digits=10, decimal_places=2
                        ),
                    )
                )
            )
            .order_by("-total_cost")
        )

    def apply_search(self, search_query):
        """Filtra por nome do item"""
        if search_query:
            return self.filter(name__icontains=search_query)
        return self

    def apply_sort(self, sort_option):
        """Ordena o queryset de itens com base na opção de sort, incluindo preço e data."""
        if sort_option == 'name_asc':
            order_by_field = 'name'
        elif sort_option == 'status':
            order_by_field = 'status'

        elif sort_option == 'price_desc':
            order_by_field = '-unit_price'
        elif sort_option == 'price_asc':
            order_by_field = 'unit_price'

        # NOVAS OPÇÕES: Data de Criação
        elif sort_option == 'date_desc':
            order_by_field = '-created_at'
        elif sort_option == 'date_asc':
            order_by_field = 'created_at'

        else:
            order_by_field = 'id'  # Padrão
        return self.order_by(order_by_field)

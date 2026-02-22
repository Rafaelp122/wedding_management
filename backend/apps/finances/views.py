from drf_spectacular.utils import extend_schema

from apps.core.viewsets import BaseViewSet

from .models import Budget, BudgetCategory, Expense, Installment
from .serializers import (
    BudgetCategorySerializer,
    BudgetSerializer,
    ExpenseSerializer,
    InstallmentSerializer,
)
from .services import (
    BudgetCategoryService,
    BudgetService,
    ExpenseService,
    InstallmentService,
)


@extend_schema(tags=["Finances"])
class BudgetViewSet(BaseViewSet):
    """
    Gestão do orçamento mestre do casamento (RF03).

    Define o teto global e centraliza as notas financeiras.
    Otimizado para evitar N+1 na resolução do casamento vinculado.
    """

    queryset = Budget.objects.select_related("wedding").all()
    serializer_class = BudgetSerializer
    service_class = BudgetService


@extend_schema(tags=["Finances"])
class BudgetCategoryViewSet(BaseViewSet):
    """
    Categorias orçamentárias para agrupamento de gastos (RF03).

    Permite a alocação de verba específica por área (ex: Buffet, Decoração).
    Valida automaticamente se a soma das categorias não excede o orçamento mestre.
    """

    queryset = BudgetCategory.objects.select_related("budget", "wedding").all()
    serializer_class = BudgetCategorySerializer
    service_class = BudgetCategoryService


@extend_schema(tags=["Finances"])
class ExpenseViewSet(BaseViewSet):
    """
    Gestão de despesas e compromissos financeiros (RF04, RF05).

    Vincula o planejado ao executado, permitindo associação com contratos.
    Implementa a regra de 'Tolerância Zero' na integridade de parcelas via Service.
    """

    queryset = Expense.objects.select_related("category", "contract", "wedding").all()
    serializer_class = ExpenseSerializer
    service_class = ExpenseService


@extend_schema(tags=["Finances"])
class InstallmentViewSet(BaseViewSet):
    """
    Controle de parcelamentos e fluxos de caixa (RF04).

    Gerencia datas de vencimento, pagamentos e status automáticos.
    Garante que a soma das parcelas seja sempre idêntica ao valor total da despesa.
    """

    queryset = Installment.objects.select_related("expense", "wedding").all()
    serializer_class = InstallmentSerializer
    service_class = InstallmentService

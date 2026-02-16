from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BudgetCategoryViewSet,
    BudgetViewSet,
    ExpenseViewSet,
    InstallmentViewSet,
)


router = DefaultRouter()
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(r"categories", BudgetCategoryViewSet, basename="budget-category")
router.register(r"expenses", ExpenseViewSet, basename="expense")
router.register(r"installments", InstallmentViewSet, basename="installment")

urlpatterns = [
    path("", include(router.urls)),
]

from decimal import Decimal
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.finances.models import Installment
from apps.finances.services.installment_service import InstallmentService
from apps.finances.tests.factories import ExpenseFactory, InstallmentFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestInstallmentService:
    """Testes de lógica de negócio para InstallmentService - Foco em Cobertura."""

    def test_list_installments(self, user):
        wedding = WeddingFactory(planner=user)
        exp = ExpenseFactory(wedding=wedding)
        InstallmentFactory(expense=exp)

        qs = InstallmentService.list(user)
        assert qs.count() == 1

    def test_update_installment_success(self, user):
        wedding = WeddingFactory(planner=user)
        # Despesa de 1000 com uma parcela de 1000
        expense = ExpenseFactory(wedding=wedding, actual_amount=Decimal("1000.00"))
        inst = InstallmentFactory(expense=expense, amount=Decimal("1000.00"))

        updated = InstallmentService.update(inst, {"notes": "Pago em dinheiro"})
        assert updated.notes == "Pago em dinheiro"

    def test_update_installment_math_violation(self, user):
        wedding = WeddingFactory(planner=user)
        expense = ExpenseFactory(wedding=wedding, actual_amount=Decimal("1000.00"))
        inst = InstallmentFactory(expense=expense, amount=Decimal("1000.00"))

        with pytest.raises(BusinessRuleViolation, match="viola as regras matemáticas"):
            InstallmentService.update(inst, {"amount": Decimal("500.00")})

    def test_delete_installment_protected_error(self, user):
        inst = InstallmentFactory(expense__wedding__planner=user)

        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar esta parcela no momento"
        ):
            with patch.object(
                Installment, "delete", side_effect=ProtectedError("Erro", [])
            ):
                InstallmentService.delete(inst)

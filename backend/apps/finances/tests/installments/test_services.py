from decimal import Decimal
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.events.tests.factories import EventFactory
from apps.finances.models import Installment
from apps.finances.services.installment_service import InstallmentService
from apps.finances.tests.factories import ExpenseFactory, InstallmentFactory


@pytest.mark.django_db
@pytest.mark.service
class TestInstallmentService:
    """Testes de lógica de negócio para InstallmentService - Foco em Cobertura."""

    def test_list_installments(self, user):
        event = EventFactory(company=user.company)
        exp = ExpenseFactory(event=event)
        InstallmentFactory(expense=exp)

        qs = InstallmentService.list(user)
        assert qs.count() == 1

    def test_update_installment_success(self, user):
        event = EventFactory(company=user.company)
        # Despesa de 1000 com uma parcela de 1000
        expense = ExpenseFactory(event=event, actual_amount=Decimal("1000.00"))
        inst = InstallmentFactory(expense=expense, amount=Decimal("1000.00"))

        updated = InstallmentService.update(inst, {"notes": "Pago em dinheiro"})
        assert updated.notes == "Pago em dinheiro"

    def test_update_installment_math_violation(self, user):
        event = EventFactory(company=user.company)
        expense = ExpenseFactory(event=event, actual_amount=Decimal("1000.00"))
        inst = InstallmentFactory(expense=expense, amount=Decimal("1000.00"))

        with pytest.raises(BusinessRuleViolation, match="viola as regras matemáticas"):
            InstallmentService.update(inst, {"amount": Decimal("500.00")})

    def test_delete_installment_protected_error(self, user):
        inst = InstallmentFactory(expense__event__company=user.company)

        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar esta parcela no momento"
        ):
            with patch.object(
                Installment, "delete", side_effect=ProtectedError("Erro", [])
            ):
                InstallmentService.delete(inst)

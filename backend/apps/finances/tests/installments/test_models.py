import pytest
from django.core.exceptions import ValidationError

from apps.finances.models import Installment
from apps.finances.tests.factories import ExpenseFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestInstallmentModel:
    """Testes de integridade física e lógica da Installment."""

    def test_installment_str(self):
        expense = ExpenseFactory.build(description="Buffet")
        installment = Installment(
            expense=expense,
            installment_number=1,
            status=Installment.StatusChoices.PENDING,
        )
        assert "Parcela 1 - Buffet" in str(installment)

    def test_clean_validates_paid_date_consistency(self, user):
        """Garante que status PAGO e paid_date andam juntos."""
        wedding = WeddingFactory(planner=user)
        # Usamos uma instância real da factory para garantir consistência de Tenancy
        expense = ExpenseFactory(wedding=wedding)

        installment = Installment(
            wedding=wedding,
            expense=expense,
            status=Installment.StatusChoices.PAID,
            paid_date=None,  # ERRO
        )
        with pytest.raises(ValidationError, match="precisa ter data de pagamento"):
            installment.clean()

    def test_clean_validates_pending_status_with_date(self, user):
        """Garante que status PENDENTE não aceite paid_date."""
        from datetime import date

        wedding = WeddingFactory(planner=user)
        expense = ExpenseFactory(wedding=wedding)

        installment = Installment(
            wedding=wedding,
            expense=expense,
            status=Installment.StatusChoices.PENDING,
            paid_date=date.today(),  # ERRO
        )
        with pytest.raises(ValidationError, match="deve ter status PAGO"):
            installment.clean()

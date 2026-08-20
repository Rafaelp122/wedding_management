from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Budget, BudgetCategory
from apps.finances.tests.factories import (
    BudgetFactory,
)
from apps.logistics.tests.factories import ContractFactory
from apps.scheduler.models import Event
from apps.users.tests.factories import UserFactory
from apps.weddings.models import Wedding
from apps.weddings.schemas import WeddingIn, WeddingPatchIn
from apps.weddings.services import WeddingService
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingService:
    """Testes de mutação do WeddingService (create, update, delete)."""

    def test_update_wedding_with_empty_bride_name_raises_business_rule_violation(
        self, user
    ):
        """update() com dado inválido deve levantar BusinessRuleViolation."""
        wedding = WeddingFactory(company=user.company, bride_name="Antiga")

        with pytest.raises(BusinessRuleViolation, match="não pode estar vazio"):
            WeddingService.update(
                instance=wedding,
                company=user.company,
                payload=WeddingPatchIn(**{"bride_name": ""}),
            )

    def test_create_wedding_does_not_create_financial_data_eagerly(
        self, user, wedding_payload
    ):
        """
        Com lazy loading ativo, criar casamento NÃO deve criar Budget/Categorias.
        """
        # Setup: inclui campo legado para garantir que seja ignorado com segurança
        wedding_payload["total_estimated"] = Decimal("75000.50")

        # Execução
        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        # Asserções: Wedding criado
        assert Wedding.objects.count() == 1
        assert wedding.company == user.company
        assert wedding.bride_name == wedding_payload["bride_name"]
        assert wedding.status == Wedding.StatusChoices.IN_PROGRESS

        # Asserções: camada financeira fica vazia até chamada lazy
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_update_wedding_ignores_budget_field(self, user):
        """
        ADR-006: Garante que o update do casamento é isolado e não
        tenta (ou falha) ao receber campos financeiros.
        """
        wedding = WeddingFactory(company=user.company, bride_name="Antiga")
        initial_value = Decimal("50000.00")
        BudgetFactory(wedding=wedding, total_estimated=initial_value)

        update_data = {
            "bride_name": "Nova Maria",
            "total_estimated": Decimal("999999.99"),  # Campo "intruso"
        }

        # Execução
        updated_wedding = WeddingService.update(
            company=user.company,
            instance=wedding,
            payload=WeddingPatchIn(**update_data),
        )

        # Asserção
        assert updated_wedding.bride_name == "Nova Maria"

        budget = Budget.objects.get(wedding=updated_wedding)
        assert budget.total_estimated == initial_value

    def test_update_wedding_cross_tenant(self, user):
        """Casamento de outro tenant não pode ser atualizado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            WeddingService.update(
                company=user.company,
                instance=other_wedding,
                payload=WeddingPatchIn(**{"bride_name": "Hack"}),
            )

    def test_create_wedding_fail_fast_validation_error(self, user, wedding_payload):
        """
        Cenário 2: Garante que dados inválidos no casamento interrompem o processo
        antes de tocar na parte financeira (Fail Fast).
        """
        wedding_payload["bride_name"] = ""

        with pytest.raises(BusinessRuleViolation, match="não pode estar vazio"):
            WeddingService.create(
                company=user.company, payload=WeddingIn(**wedding_payload)
            )

        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_create_wedding_fail_with_invalid_date(self, user, wedding_payload):
        """
        Cenário 2.1: Garante que uma data passada ou inválida também trava a criação.
        """
        wedding_payload["date"] = timezone.now().date() - timedelta(days=1)

        with pytest.raises(BusinessRuleViolation, match="não pode ser no passado"):
            WeddingService.create(
                company=user.company, payload=WeddingIn(**wedding_payload)
            )

        assert Wedding.objects.count() == 0

    def test_create_wedding_does_not_call_budget_service(self, user, wedding_payload):
        """Com lazy loading, create de Wedding não deve acionar BudgetService."""
        with patch(
            "apps.finances.services.budget_service.BudgetService.create"
        ) as mock_budget:
            wedding = WeddingService.create(
                company=user.company, payload=WeddingIn(**wedding_payload)
            )

        assert wedding.uuid is not None
        assert Wedding.objects.count() == 1
        mock_budget.assert_not_called()
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_wedding_service_multitenancy_isolation(self, user, wedding_payload):
        """
        Cenário 4: Garante que dados de diferentes usuários fiquem isolados.
        """
        planner_a = user
        planner_b = UserFactory()

        payload_a = {
            **wedding_payload,
            "bride_name": "Noiva A",
            "total_estimated": 10000,
        }
        payload_b = {
            **wedding_payload,
            "bride_name": "Noiva B",
            "total_estimated": 20000,
        }

        wedding_a = WeddingService.create(
            company=planner_a.company, payload=WeddingIn(**payload_a)
        )
        wedding_b = WeddingService.create(
            company=planner_b.company, payload=WeddingIn(**payload_b)
        )

        assert wedding_a.company == planner_a.company
        assert Wedding.objects.all().for_tenant(planner_a.company).count() == 1
        assert Wedding.objects.all().for_tenant(planner_b.company).count() == 1
        assert (
            Wedding.objects.all()
            .for_tenant(planner_a.company)
            .filter(uuid=wedding_b.uuid)
            .exists()
            is False
        )

    def test_delete_wedding_protected_by_contracts(self, user):
        """
        Cenário 6: Impede a deleção de um casamento que possui contratos vinculados.
        """
        wedding = WeddingFactory(company=user.company)
        BudgetFactory(wedding=wedding)
        ContractFactory(wedding=wedding)

        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar este casamento"
        ):
            WeddingService.delete(company=user.company, instance=wedding)

        assert Wedding.objects.filter(uuid=wedding.uuid).exists()

    def test_delete_wedding_full_clean_cascade(self, user, wedding_payload):
        """
        Cenário 7: Deleção total (Hard Delete) funciona quando não há travas.
        """
        payload = {**wedding_payload, "total_estimated": Decimal("50000.00")}

        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**payload)
        )

        WeddingService.delete(company=user.company, instance=wedding)

        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_delete_wedding_cross_tenant(self, user):
        """Casamento de outro tenant não pode ser deletado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            WeddingService.delete(company=user.company, instance=other_wedding)


@pytest.mark.django_db
class TestWeddingTemplateApplication:
    """Testes de aplicação de templates de cronograma na criação do casamento."""

    def test_create_wedding_with_religious_12m_template(self, user, wedding_payload):
        """Template 'religious_12m' gera eventos com offset antes da data."""
        wedding_payload["template"] = "religious_12m"

        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        events = Event.objects.filter(wedding=wedding).order_by("start_time")
        assert len(events) == 10

        first_event = events.first()
        assert first_event.title == "Definir local da cerimônia"
        assert first_event.event_type == Event.TypeChoices.MEETING
        assert first_event.start_time.date() == wedding.date - timedelta(days=365)

        last_event = events.last()
        assert last_event.title == "Reunião final com fornecedores"
        assert last_event.start_time.date() == wedding.date - timedelta(days=7)

    def test_create_wedding_with_beach_6m_template(self, user, wedding_payload):
        """Template 'beach_6m' gera eventos corretamente."""
        wedding_payload["template"] = "beach_6m"

        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        events = Event.objects.filter(wedding=wedding)
        assert len(events) == 8
        assert all(e.company == user.company for e in events)
        assert all(e.wedding == wedding for e in events)

    def test_create_wedding_with_civil_buffet_3m_template(self, user, wedding_payload):
        """Template 'civil_buffet_3m' gera eventos corretamente."""
        wedding_payload["template"] = "civil_buffet_3m"

        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        events = Event.objects.filter(wedding=wedding)
        assert len(events) == 7

    def test_create_wedding_with_no_template(self, user, wedding_payload):
        """Sem template, nenhum evento é criado."""
        wedding_payload.pop("template", None)

        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        events = Event.objects.filter(wedding=wedding)
        assert events.count() == 0

    def test_create_wedding_with_none_template_value(self, user, wedding_payload):
        """Template=None não gera eventos."""
        wedding_payload["template"] = None

        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        events = Event.objects.filter(wedding=wedding)
        assert events.count() == 0

    def test_create_wedding_with_invalid_template_raises(self, user, wedding_payload):
        """Template inválido levanta BusinessRuleViolation."""
        wedding_payload["template"] = "nonexistent_template"

        with pytest.raises(BusinessRuleViolation) as exc_info:
            WeddingService.create(
                company=user.company, payload=WeddingIn(**wedding_payload)
            )

        assert "nonexistent_template" in str(exc_info.value.detail)
        assert exc_info.value.code == "template_not_found"
        assert Wedding.objects.count() == 0

    def test_template_events_are_correctly_offset(self, user, wedding_payload):
        """Cada evento tem offset_days correto em relação à data do casamento."""
        wedding_payload["date"] = timezone.now().date() + timedelta(days=200)
        wedding_payload["template"] = "religious_12m"

        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        events = Event.objects.filter(wedding=wedding).order_by("start_time")
        offsets = [365, 330, 300, 270, 240, 180, 150, 90, 30, 7]

        for event, offset in zip(events, offsets, strict=True):
            expected_date = wedding.date - timedelta(days=offset)
            assert event.start_time.date() == expected_date

    def test_template_does_not_mutate_shared_data(self, user, wedding_payload):
        """Aplicar o mesmo template duas vezes não corrompe os dados."""
        wedding_payload["template"] = "beach_6m"

        wedding1 = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )
        wedding2 = WeddingService.create(
            company=user.company, payload=WeddingIn(**wedding_payload)
        )

        events1 = Event.objects.filter(wedding=wedding1).count()
        events2 = Event.objects.filter(wedding=wedding2).count()

        assert events1 == 8
        assert events2 == 8

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Budget, BudgetCategory
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.scheduler.models import Event
from apps.scheduler.tests.factories import TaskFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.models import Wedding
from apps.weddings.schemas import WeddingIn, WeddingPatchIn
from apps.weddings.services import (
    ContractSummaryService,
    DashboardService,
    FinancialSummaryService,
    TaskSummaryService,
    WeddingService,
)
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


@pytest.mark.django_db
class TestDashboardService:
    """Testes para o DashboardService delegando para selectors."""

    def test_get_summary_delegation(self, user):
        """get_summary() delega para dashboard_summary_selector."""
        with patch(
            "apps.weddings.services.dashboard_service.dashboard_summary_selector"
        ) as mock_selector:
            mock_selector.return_value = {"mocked": True}
            result = DashboardService.get_summary(company=user.company)

        mock_selector.assert_called_once_with(company=user.company)
        assert result == {"mocked": True}

    def test_get_wedding_overview_delegation(self, user):
        """get_wedding_overview() delega para wedding_overview_selector."""
        test_uuid = uuid4()
        with patch(
            "apps.weddings.services.dashboard_service.wedding_overview_selector"
        ) as mock_selector:
            mock_selector.return_value = {"mocked_overview": True}
            result = DashboardService.get_wedding_overview(
                company=user.company, wedding_uuid=test_uuid
            )

        mock_selector.assert_called_once_with(
            company=user.company, wedding_uuid=test_uuid
        )
        assert result == {"mocked_overview": True}


@pytest.mark.django_db
class TestFinancialSummaryService:
    def test_pending_installments_7d_returns_total(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)

        InstallmentFactory(
            expense=expense,
            amount=2500.00,
            due_date=today + timedelta(days=3),
            status="PENDING",
        )
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today + timedelta(days=10),
            status="PENDING",
        )

        result = FinancialSummaryService.pending_installments_7d(
            company=user.company, today=today
        )
        assert result == Decimal("2500.00")

    def test_pending_installments_7d_includes_today(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)
        InstallmentFactory(
            expense=expense,
            amount=500.00,
            due_date=today,
            status="PENDING",
        )

        result = FinancialSummaryService.pending_installments_7d(
            company=user.company, today=today
        )
        assert result == Decimal("500.00")

    def test_pending_installments_7d_includes_last_day(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)
        InstallmentFactory(
            expense=expense,
            amount=500.00,
            due_date=today + timedelta(days=7),
            status="PENDING",
        )

        result = FinancialSummaryService.pending_installments_7d(
            company=user.company, today=today
        )
        assert result == Decimal("500.00")

    def test_pending_installments_7d_empty(self, user):
        result = FinancialSummaryService.pending_installments_7d(
            company=user.company, today=date.today()
        )
        assert result == Decimal("0.00")

    def test_overdue_installments_returns_amount_and_count(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)

        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today - timedelta(days=5),
            status="PENDING",
        )
        InstallmentFactory(
            expense=expense,
            amount=500.00,
            due_date=today - timedelta(days=10),
            status="OVERDUE",
        )

        amount, count = FinancialSummaryService.overdue_installments(
            company=user.company, today=today
        )
        assert amount == Decimal("1500.00")
        assert count == 2

    def test_overdue_installments_empty(self, user):
        amount, count = FinancialSummaryService.overdue_installments(
            company=user.company, today=date.today()
        )
        assert amount == Decimal("0.00")
        assert count == 0

    def test_budget_percentage_used(self, user):
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(
            wedding=wedding, company=user.company, total_estimated=10000.00
        )
        category = BudgetCategoryFactory(
            wedding=wedding, budget=budget, allocated_budget=5000.00
        )
        expense = ExpenseFactory(
            wedding=wedding, category=category, actual_amount=2000.00, contract=None
        )
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=date.today() - timedelta(days=5),
            status="PAID",
            paid_date=date.today() - timedelta(days=5),
            wedding=wedding,
            company=user.company,
        )

        pct = FinancialSummaryService.budget_percentage_used(
            company=user.company, wedding=wedding
        )
        assert pct == 10.0

    def test_budget_percentage_used_capped(self, user):
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(
            wedding=wedding, company=user.company, total_estimated=1000.00
        )
        category = BudgetCategoryFactory(
            wedding=wedding, budget=budget, allocated_budget=5000.00
        )
        expense = ExpenseFactory(
            wedding=wedding, category=category, actual_amount=5000.00, contract=None
        )
        InstallmentFactory(
            expense=expense,
            amount=5000.00,
            due_date=date.today() - timedelta(days=5),
            status="PAID",
            paid_date=date.today() - timedelta(days=5),
            wedding=wedding,
            company=user.company,
        )

        pct = FinancialSummaryService.budget_percentage_used(
            company=user.company, wedding=wedding
        )
        assert pct == 100.0

    def test_budget_percentage_used_no_budget(self, user):
        wedding = WeddingFactory(company=user.company)
        pct = FinancialSummaryService.budget_percentage_used(
            company=user.company, wedding=wedding
        )
        assert pct == 0.0

    def test_upcoming_installments_returns_list(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)
        inst = InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today + timedelta(days=15),
            status="PENDING",
            wedding=wedding,
            company=user.company,
        )

        result = FinancialSummaryService.upcoming_installments(
            company=user.company, wedding=wedding, today=today
        )
        assert len(result) == 1
        assert result[0]["uuid"] == inst.uuid
        assert result[0]["amount"] == "1000.00"

    def test_upcoming_installments_excludes_paid(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today + timedelta(days=5),
            status="PAID",
            paid_date=today,
            wedding=wedding,
            company=user.company,
        )

        result = FinancialSummaryService.upcoming_installments(
            company=user.company, wedding=wedding, today=today
        )
        assert len(result) == 0

    def test_categories_summary_empty(self, user):
        wedding = WeddingFactory(company=user.company)
        result = FinancialSummaryService.categories_summary(
            company=user.company, wedding=wedding
        )
        assert result == []

    def test_categories_summary(self, user):
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(
            wedding=wedding, company=user.company, total_estimated=10000.00
        )
        category = BudgetCategoryFactory(
            wedding=wedding, budget=budget, allocated_budget=5000.00
        )
        expense = ExpenseFactory(
            wedding=wedding, category=category, actual_amount=1000.00, contract=None
        )
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=date.today() - timedelta(days=5),
            status="PAID",
            paid_date=date.today() - timedelta(days=5),
            wedding=wedding,
            company=user.company,
        )

        result = FinancialSummaryService.categories_summary(
            company=user.company, wedding=wedding
        )
        assert len(result) == 1
        assert result[0]["name"] == category.name
        assert result[0]["percentage"] == 20


@pytest.mark.django_db
class TestTaskSummaryService:
    def test_urgent_tasks_count(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today - timedelta(days=1),
        )
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=True,
            due_date=today - timedelta(days=1),
        )

        count = TaskSummaryService.urgent_tasks_count(company=user.company, today=today)
        assert count == 1

    def test_urgent_tasks_count_zero(self, user):
        count = TaskSummaryService.urgent_tasks_count(
            company=user.company, today=date.today()
        )
        assert count == 0

    def test_wedding_task_stats(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=True,
            due_date=today - timedelta(days=1),
        )
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today + timedelta(days=1),
        )

        completed, total = TaskSummaryService.wedding_task_stats(
            company=user.company, wedding=wedding
        )
        assert completed == 1
        assert total == 2

    def test_wedding_task_stats_no_tasks(self, user):
        wedding = WeddingFactory(company=user.company)
        completed, total = TaskSummaryService.wedding_task_stats(
            company=user.company, wedding=wedding
        )
        assert completed == 0
        assert total == 0

    def test_urgent_tasks_returns_overdue_first(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today - timedelta(days=2),
            title="Urgent",
        )
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today + timedelta(days=5),
            title="Future",
        )

        result = TaskSummaryService.urgent_tasks(
            company=user.company, wedding=wedding, today=today
        )
        assert len(result) == 1
        assert result[0]["title"] == "Urgent"

    def test_urgent_tasks_empty(self, user):
        wedding = WeddingFactory(company=user.company)
        result = TaskSummaryService.urgent_tasks(
            company=user.company, wedding=wedding, today=date.today()
        )
        assert result == []


@pytest.mark.django_db
class TestContractSummaryService:
    def test_pending_contracts_count(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        ContractFactory(
            wedding=wedding, company=user.company, supplier=supplier, status="PENDING"
        )
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="SIGNED",
            pdf_file="contracts/x.pdf",
            signed_date=date.today(),
        )

        count = ContractSummaryService.pending_contracts_count(company=user.company)
        assert count == 1

    def test_pending_contracts_count_includes_draft(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        ContractFactory(
            wedding=wedding, company=user.company, supplier=supplier, status="DRAFT"
        )
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="SIGNED",
            pdf_file="contracts/x.pdf",
            signed_date=date.today(),
        )

        count = ContractSummaryService.pending_contracts_count(company=user.company)
        assert count == 1

    def test_pending_contracts_count_zero(self, user):
        count = ContractSummaryService.pending_contracts_count(company=user.company)
        assert count == 0

    def test_wedding_contract_stats(self, user):
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="SIGNED",
            total_amount=5000.00,
            pdf_file="contracts/x.pdf",
            signed_date=today,
        )
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="PENDING",
            total_amount=3000.00,
        )

        signed, total = ContractSummaryService.wedding_contract_stats(
            company=user.company, wedding=wedding
        )
        assert signed == 1
        assert total == 2

    def test_wedding_contract_stats_no_contracts(self, user):
        wedding = WeddingFactory(company=user.company)
        signed, total = ContractSummaryService.wedding_contract_stats(
            company=user.company, wedding=wedding
        )
        assert signed == 0
        assert total == 0

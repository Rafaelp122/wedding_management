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
from apps.finances.models import Budget, BudgetCategory, Installment
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
    def test_get_wedding_success(self, user):
        """get() com uuid existente deve retornar o Wedding correto."""
        wedding = WeddingFactory(company=user.company, bride_name="Noiva Get")

        result = WeddingService.get(company=user.company, uuid=wedding.uuid)

        assert result.uuid == wedding.uuid
        assert result.bride_name == "Noiva Get"
        assert result.company == user.company

    def test_get_wedding_not_found_raises_object_not_found(self, user):
        """get() com uuid inexistente deve levantar ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError) as exc_info:
            WeddingService.get(company=user.company, uuid=uuid4())

        assert "Casamento não encontrado ou acesso negado" in str(exc_info.value)
        assert exc_info.value.code == "wedding_not_found_or_denied"

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
        # Setup: Casamento já existente

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
        from apps.users.tests.factories import UserFactory

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
        # 1. Setup: Payload com dado inválido (nome da noiva vazio)
        # Nota: bride_name é campo obrigatório no Model
        wedding_payload["bride_name"] = ""

        # 2. Execução e Asserção de Erro
        with pytest.raises(BusinessRuleViolation, match="não pode estar vazio"):
            WeddingService.create(
                company=user.company, payload=WeddingIn(**wedding_payload)
            )

        # 3. Validação de Banco de Dados Limpo
        # Nada deve ter sido criado devido à falha precoce
        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_create_wedding_fail_with_invalid_date(self, user, wedding_payload):
        """
        Cenário 2.1: Garante que uma data passada (se houver regra no Model)
        ou inválida também trava a criação.
        """
        from datetime import timedelta

        # Criando um payload com data de ontem (assumindo que seu model proíbe
        # datas passadas)
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
        from apps.users.tests.factories import UserFactory

        # 1. Setup: Planners distintos
        planner_a = user
        planner_b = UserFactory()

        # Criamos payloads distintos a partir da base explícita
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

        # 2. Execução
        wedding_a = WeddingService.create(
            company=planner_a.company, payload=WeddingIn(**payload_a)
        )
        wedding_b = WeddingService.create(
            company=planner_b.company, payload=WeddingIn(**payload_b)
        )

        # 3. Asserções (O coração do teste)
        assert wedding_a.company == planner_a.company
        assert Wedding.objects.all().for_tenant(planner_a.company).count() == 1
        assert Wedding.objects.all().for_tenant(planner_b.company).count() == 1

        # 4. O Teste de Ouro: Isolamento via Manager. Se o Manager .for_tenant()
        # estiver correto, o Planner A nunca verá o Casamento B.
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
        Valida a proteção contra perda de dados financeiros/logísticos.
        """
        # 1. Cria o casamento e orçamento
        wedding = WeddingFactory(company=user.company)
        BudgetFactory(wedding=wedding)

        # 2. Cria o contrato passando apenas o wedding principal.
        # As sub-fábricas agora sabem se auto-ajustar.
        ContractFactory(wedding=wedding)

        # 3. O resto permanece igual
        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar este casamento"
        ):
            WeddingService.delete(company=user.company, instance=wedding)

        assert Wedding.objects.filter(uuid=wedding.uuid).exists()

    def test_delete_wedding_full_clean_cascade(self, user, wedding_payload):
        """
        Cenário 7: Deleção total (Hard Delete) funciona quando não há travas.
        Garante que Orçamento e Categorias são limpos (Cascade).
        """
        # 1. Setup: Criar casamento sem efeitos financeiros automáticos.
        payload = {**wedding_payload, "total_estimated": Decimal("50000.00")}

        # O serviço cria apenas o Wedding; a camada financeira é lazy.
        wedding = WeddingService.create(
            company=user.company, payload=WeddingIn(**payload)
        )

        # 2. Execução: Deletar o casamento
        WeddingService.delete(company=user.company, instance=wedding)

        # 3. Asserções: O banco de dados deve estar limpo
        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_delete_wedding_cross_tenant(self, user):
        """Casamento de outro tenant não pode ser deletado."""
        from apps.users.tests.factories import UserFactory

        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            WeddingService.delete(company=user.company, instance=other_wedding)

    def test_list_lookup_success(self, user):
        """list_lookup() deve retornar apenas os casamentos da empresa
        do usuário, ordenados pelo nome da noiva.
        """
        WeddingFactory(company=user.company, bride_name="Zulmira", groom_name="Beto")
        WeddingFactory(company=user.company, bride_name="Ana", groom_name="Carlos")

        result = WeddingService.list_lookup(company=user.company)

        assert result.count() == 2
        assert result[0].bride_name == "Ana"
        assert result[1].bride_name == "Zulmira"

    def test_list_lookup_multitenancy_isolation(self, user):
        """list_lookup() deve isolar os casamentos por tenant."""
        from apps.users.tests.factories import UserFactory

        other_user = UserFactory()
        WeddingFactory(company=user.company, bride_name="Noiva A")
        WeddingFactory(company=other_user.company, bride_name="Noiva B")

        result = WeddingService.list_lookup(company=user.company)

        assert result.count() == 1
        assert result[0].bride_name == "Noiva A"


@pytest.mark.django_db
class TestWeddingServiceListAnnotations:
    """Testes para as annotations do método list()."""

    def test_list_includes_annotation_fields(self, user):
        """list() retorna weddings com total_budget, overdue_installments e
        incomplete_tasks populados."""
        wedding = WeddingFactory(company=user.company)
        BudgetFactory(wedding=wedding, company=user.company, total_estimated=50000)

        qs = WeddingService.list(company=user.company)
        result = qs.first()

        assert result is not None
        assert float(result.total_budget) == 50000.0
        assert result.overdue_installments == 0
        assert result.incomplete_tasks == 0

    def test_list_total_budget_none_without_budget(self, user):
        """total_budget é None quando o casamento não tem Budget."""
        WeddingFactory(company=user.company)

        qs = WeddingService.list(company=user.company)
        result = qs.first()

        assert result is not None
        assert result.total_budget is None

    def test_list_counts_overdue_and_incomplete(self, user):
        """overdue_installments e incomplete_tasks refletem os dados reais."""
        from datetime import date, timedelta

        today = date.today()
        wedding = WeddingFactory(company=user.company)

        budget = BudgetFactory(wedding=wedding, company=user.company)
        category = BudgetCategoryFactory(
            budget=budget, wedding=wedding, company=user.company
        )
        expense = ExpenseFactory(
            wedding=wedding, category=category, contract=None, company=user.company
        )

        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=1000,
            due_date=today - timedelta(days=10),
            status="OVERDUE",
        )

        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
        )

        qs = WeddingService.list(company=user.company)
        result = qs.first()

        assert result is not None
        assert result.overdue_installments == 1
        assert result.incomplete_tasks == 1

    def test_list_multitenancy_isolates_annotations(self, user):
        """Annotations respeitam o isolamento multi-tenant."""
        from apps.users.tests.factories import UserFactory

        other_user = UserFactory()
        WeddingFactory(company=user.company)
        WeddingFactory(company=other_user.company)

        qs = WeddingService.list(company=user.company)

        assert qs.count() == 1

    def test_list_filters_by_search(self, user):
        """list() filtra por groom_name, bride_name e location."""
        WeddingFactory(
            company=user.company,
            groom_name="Xablau",
            bride_name="Xablau",
            location="Xablau",
        )
        WeddingFactory(
            company=user.company,
            groom_name="Ciclano",
            bride_name="Fulana",
            location="Belo Horizonte",
        )

        by_groom = WeddingService.list(company=user.company, search="Ciclano")
        by_bride = WeddingService.list(company=user.company, search="Fulana")
        by_location = WeddingService.list(company=user.company, search="Belo")
        by_none = WeddingService.list(company=user.company, search="Inexistente")

        assert by_groom.count() == 1
        assert by_bride.count() == 1
        assert by_location.count() == 1
        assert by_none.count() == 0

    def test_list_filters_by_status(self, user):
        """list() filtra corretamente por status."""
        from datetime import date, timedelta

        WeddingFactory(company=user.company, status="IN_PROGRESS")
        completed = WeddingFactory(company=user.company, status="IN_PROGRESS")
        Wedding.objects.filter(pk=completed.pk).update(
            status="COMPLETED", date=date.today() - timedelta(days=30)
        )

        in_progress = WeddingService.list(company=user.company, status="IN_PROGRESS")
        completed_qs = WeddingService.list(company=user.company, status="COMPLETED")

        assert in_progress.count() == 1
        assert completed_qs.count() == 1

    def test_list_raises_on_invalid_status(self, user):
        """list() rejeita status inválido com BusinessRuleViolation."""
        WeddingFactory(company=user.company)

        with pytest.raises(BusinessRuleViolation, match="Status inválido"):
            WeddingService.list(company=user.company, status="INVALIDO")

    def test_overview_success(self, user):
        """overview() com dados completos deve retornar WeddingOverviewOut com métricas."""
        wedding = WeddingFactory(company=user.company, bride_name="Overview Bride", date=date.today() + timedelta(days=60))

        budget = BudgetFactory(wedding=wedding, company=user.company, total_estimated=Decimal("10000.00"))
        BudgetCategoryFactory(budget=budget, name="Buffet", allocated_budget=Decimal("5000.00"), spent_amount=Decimal("2500.00"))
        ExpenseFactory(wedding=wedding, company=user.company, category=budget.categories.first(), actual_amount=Decimal("2500.00"))
        InstallmentFactory(wedding=wedding, company=user.company, installment_number=1, amount=Decimal("1000.00"), status="PENDING")
        InstallmentFactory(wedding=wedding, company=user.company, installment_number=2, amount=Decimal("1000.00"), status="OVERDUE")
        TaskFactory(wedding=wedding, company=user.company, title="Task 1", is_completed=True)
        TaskFactory(wedding=wedding, company=user.company, title="Task 2", is_completed=False)
        supplier = SupplierFactory(company=user.company)
        ContractFactory(wedding=wedding, company=user.company, supplier=supplier, status="SIGNED")
        ContractFactory(wedding=wedding, company=user.company, supplier=supplier, status="DRAFT")

        result = WeddingService.overview(company=user.company, uuid=wedding.uuid)

        assert result.wedding.uuid == wedding.uuid
        assert result.wedding.bride_name == "Overview Bride"
        assert result.wedding.groom_name == wedding.groom_name

        overview = result.overview
        assert overview.days_until_wedding == 60
        assert overview.budget_percentage_used == 25.0
        assert overview.tasks_completed == 1
        assert overview.tasks_total == 2
        assert overview.contracts_signed == 1
        assert overview.contracts_total == 2
        assert len(overview.upcoming_installments) == 2
        assert len(overview.urgent_tasks) == 1
        assert len(overview.categories_summary) == 1

        # WeddingOut fields
        assert result.wedding.total_budget == 10000.0
        assert result.wedding.overdue_installments == 1
        assert result.wedding.incomplete_tasks == 1

    def test_overview_wedding_not_found_raises_object_not_found(self, user):
        """overview() com uuid inexistente deve levantar ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError) as exc_info:
            WeddingService.overview(company=user.company, uuid=uuid4())

        assert exc_info.value.code == "wedding_not_found_or_denied"

    def test_overview_other_tenant_raises_object_not_found(self, user):
        """overview() de casamento de outro tenant deve levantar ObjectNotFoundError."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)

        with pytest.raises(ObjectNotFoundError) as exc_info:
            WeddingService.overview(company=user.company, uuid=other_wedding.uuid)

        assert exc_info.value.code == "wedding_not_found_or_denied"


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
        assert len(events) == 10  # religious_12m tem 10 eventos

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
            assert event.start_time.date() == expected_date, (
                f"Evento '{event.title}' deveria estar em {expected_date}, "
                f"mas está em {event.start_time.date()} (offset esperado: {offset})"
            )

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
    def test_get_summary_success(self, user):
        """Calcula corretamente as estatísticas do painel incluindo novas métricas."""
        # Setup supporting data
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense1 = ExpenseFactory(wedding=wedding, category=category, contract=None)

        # 1. Overdue installment (amount: 1000.00)
        InstallmentFactory(
            expense=expense1,
            amount=1000.00,
            due_date=today - timedelta(days=5),
            status="PENDING",
        )

        # 2. Upcoming installment in 7 days (amount: 2500.00)
        InstallmentFactory(
            expense=expense1,
            amount=2500.00,
            due_date=today + timedelta(days=3),
            status="PENDING",
        )

        # 3. Urgent tasks
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today - timedelta(days=1),
        )

        # 4. Pending contract
        supplier = SupplierFactory(company=user.company)
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="PENDING",
            total_amount=5000.00,
        )

        summary = DashboardService.get_summary(company=user.company)

        assert summary["overdue_installments_count"] == 1
        assert summary["overdue_installments_amount"] == "1000.00"
        assert summary["pending_installments_7d"] == "2500.00"
        assert summary["urgent_tasks_count"] == 1
        assert summary["pending_contracts_count"] == 1

    def test_get_wedding_overview_success(self, user):
        """Retorna corretamente o panorama detalhado de um casamento específico."""

        today = date.today()
        # Setup: casamento, orçamento, categoria, despesa, tarefa e contrato
        wedding = WeddingFactory(company=user.company, date=today + timedelta(days=60))
        budget = BudgetFactory(
            wedding=wedding, company=user.company, total_estimated=10000.00
        )
        category = BudgetCategoryFactory(budget=budget, allocated_budget=5000.00)
        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            company=user.company,
            actual_amount=2000.00,
            contract=None,
        )

        # 1. Tarefa
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
            due_date=today - timedelta(days=2),  # tarefa urgente
            title="Tarefa Urgente",
        )

        # 2. Contrato
        supplier = SupplierFactory(company=user.company)
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="SIGNED",
            total_amount=5000.00,
            pdf_file="contracts/dummy.pdf",
            signed_date=today,
        )
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="PENDING",
            total_amount=3000.00,
        )

        # 3. Parcelas
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today - timedelta(days=10),
            status=Installment.StatusChoices.PAID,
            paid_date=today - timedelta(days=10),
            wedding=wedding,
            company=user.company,
        )
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today + timedelta(days=30),
            status=Installment.StatusChoices.PENDING,
            wedding=wedding,
            company=user.company,
        )

        overview = DashboardService.get_wedding_overview(
            company=user.company, wedding_uuid=wedding.uuid
        )

        assert overview["days_until_wedding"] == 60
        assert overview["budget_percentage_used"] == 10.0  # 1000 paid / 10000 estimated
        assert overview["tasks_completed"] == 1
        assert overview["tasks_total"] == 2
        assert overview["contracts_signed"] == 1
        assert overview["contracts_total"] == 2
        assert len(overview["upcoming_installments"]) == 1
        assert len(overview["urgent_tasks"]) == 1
        assert overview["urgent_tasks"][0]["title"] == "Tarefa Urgente"
        assert len(overview["categories_summary"]) == 1
        assert overview["categories_summary"][0]["name"] == category.name
        assert (
            overview["categories_summary"][0]["percentage"] == 20
        )  # 1000 paid / 5000 allocated

    def test_get_wedding_overview_not_found(self, user):
        """
        Tenta buscar casamento de outro tenant ou inexistente e falha
        com ObjectNotFoundError.
        """
        from apps.tenants.tests.factories import CompanyFactory

        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)

        with pytest.raises(ObjectNotFoundError):
            DashboardService.get_wedding_overview(
                company=user.company, wedding_uuid=other_wedding.uuid
            )

    def test_get_summary_logs_entry_and_exit(self, user):
        """Logs de entrada e saída devem ser emitidos em get_summary."""
        with patch("apps.weddings.services.dashboard_service.logger") as mock_logger:
            DashboardService.get_summary(company=user.company)

        mock_logger.info.assert_any_call(
            f"Computando resumo do dashboard para company_id={user.company.id}"
        )
        assert any(
            "Dashboard resumo computado" in call[0][0]
            for call in mock_logger.info.call_args_list
        )

    def test_get_wedding_overview_logs_entry_and_exit(self, user):
        """Logs de entrada e saída devem ser emitidos em get_wedding_overview."""
        wedding = WeddingFactory(company=user.company)
        with patch("apps.weddings.services.dashboard_service.logger") as mock_logger:
            DashboardService.get_wedding_overview(
                company=user.company, wedding_uuid=wedding.uuid
            )

        assert any(
            f"uuid={wedding.uuid}" in call[0][0]
            for call in mock_logger.info.call_args_list
        )
        assert any(
            "Visão geral do casamento" in call[0][0]
            for call in mock_logger.info.call_args_list
        )

    def test_get_summary_empty_company(self, user):
        """Dashboard sem casamentos deve retornar zeros."""
        summary = DashboardService.get_summary(company=user.company)

        assert summary["pending_installments_7d"] == "0.00"
        assert summary["urgent_tasks_count"] == 0
        assert summary["overdue_installments_amount"] == "0.00"
        assert summary["overdue_installments_count"] == 0
        assert summary["pending_contracts_count"] == 0
        assert summary["critical_weddings"] == []


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


@pytest.mark.django_db
class TestWeddingServiceCountByMonth:
    def test_count_by_month_returns_counts_grouped_by_month(self, user):
        """count_by_month() agrupa casamentos por mês no ano dado."""
        FUTURE_YEAR = date.today().year + 1
        for month in [1, 1, 3, 6]:
            WeddingFactory(
                company=user.company,
                date=date(FUTURE_YEAR, month, 15),
            )
        result = WeddingService.count_by_month(company=user.company, year=FUTURE_YEAR)
        assert len(result) == 3
        assert {"month": 1, "count": 2} in result
        assert {"month": 3, "count": 1} in result
        assert {"month": 6, "count": 1} in result

    def test_count_by_month_returns_empty_list_for_year_without_weddings(self, user):
        """count_by_month() retorna lista vazia quando não há casamentos no ano."""
        result = WeddingService.count_by_month(company=user.company, year=2000)
        assert result == []

    def test_count_by_month_multitenancy(self):
        """count_by_month() só conta casamentos do tenant."""
        FUTURE_YEAR = date.today().year + 1
        user_a = UserFactory()
        user_b = UserFactory()
        WeddingFactory(company=user_a.company, date=date(FUTURE_YEAR, 1, 15))
        WeddingFactory(company=user_b.company, date=date(FUTURE_YEAR, 1, 20))
        WeddingFactory(company=user_b.company, date=date(FUTURE_YEAR, 3, 10))

        result_a = WeddingService.count_by_month(
            company=user_a.company, year=FUTURE_YEAR
        )
        result_b = WeddingService.count_by_month(
            company=user_b.company, year=FUTURE_YEAR
        )

        assert result_a == [{"month": 1, "count": 1}]
        assert len(result_b) == 2

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
from apps.weddings.models import Wedding
from apps.weddings.services import DashboardService, WeddingService
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
                data={"bride_name": ""},
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
        wedding = WeddingService.create(company=user.company, data=wedding_payload)

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
            instance=wedding, company=user.company, data=update_data
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
                company=user.company, instance=other_wedding, data={"bride_name": "Hack"}
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
            WeddingService.create(company=user.company, data=wedding_payload)

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
            WeddingService.create(company=user.company, data=wedding_payload)

        assert Wedding.objects.count() == 0

    def test_create_wedding_does_not_call_budget_service(self, user, wedding_payload):
        """Com lazy loading, create de Wedding não deve acionar BudgetService."""
        with patch(
            "apps.finances.services.budget_service.BudgetService.create"
        ) as mock_budget:
            wedding = WeddingService.create(company=user.company, data=wedding_payload)

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
        wedding_a = WeddingService.create(company=planner_a.company, data=payload_a)
        wedding_b = WeddingService.create(company=planner_b.company, data=payload_b)

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
        wedding = WeddingService.create(company=user.company, data=payload)

        # 2. Execução: Deletar o casamento
        WeddingService.delete(company=user.company, instance=wedding)

        # 3. Asserções: O banco de dados deve estar limpo
        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0


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


@pytest.mark.django_db
class TestWeddingTemplateApplication:
    """Testes de aplicação de templates de cronograma na criação do casamento."""

    def test_create_wedding_with_religious_12m_template(self, user, wedding_payload):
        """Template 'religious_12m' gera eventos com offset antes da data."""
        wedding_payload["template"] = "religious_12m"

        wedding = WeddingService.create(company=user.company, data=wedding_payload)

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

        wedding = WeddingService.create(company=user.company, data=wedding_payload)

        events = Event.objects.filter(wedding=wedding)
        assert len(events) == 8
        assert all(e.company == user.company for e in events)
        assert all(e.wedding == wedding for e in events)

    def test_create_wedding_with_civil_buffet_3m_template(self, user, wedding_payload):
        """Template 'civil_buffet_3m' gera eventos corretamente."""
        wedding_payload["template"] = "civil_buffet_3m"

        wedding = WeddingService.create(company=user.company, data=wedding_payload)

        events = Event.objects.filter(wedding=wedding)
        assert len(events) == 7

    def test_create_wedding_with_no_template(self, user, wedding_payload):
        """Sem template, nenhum evento é criado."""
        wedding_payload.pop("template", None)

        wedding = WeddingService.create(company=user.company, data=wedding_payload)

        events = Event.objects.filter(wedding=wedding)
        assert events.count() == 0

    def test_create_wedding_with_none_template_value(self, user, wedding_payload):
        """Template=None não gera eventos."""
        wedding_payload["template"] = None

        wedding = WeddingService.create(company=user.company, data=wedding_payload)

        events = Event.objects.filter(wedding=wedding)
        assert events.count() == 0

    def test_create_wedding_with_invalid_template_raises(self, user, wedding_payload):
        """Template inválido levanta BusinessRuleViolation."""
        wedding_payload["template"] = "nonexistent_template"

        with pytest.raises(BusinessRuleViolation) as exc_info:
            WeddingService.create(company=user.company, data=wedding_payload)

        assert "nonexistent_template" in str(exc_info.value.detail)
        assert exc_info.value.code == "template_not_found"
        assert Wedding.objects.count() == 0

    def test_template_events_are_correctly_offset(self, user, wedding_payload):
        """Cada evento tem offset_days correto em relação à data do casamento."""
        wedding_payload["date"] = timezone.now().date() + timedelta(days=200)
        wedding_payload["template"] = "religious_12m"

        wedding = WeddingService.create(company=user.company, data=wedding_payload)

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

        wedding1 = WeddingService.create(company=user.company, data=wedding_payload)
        wedding2 = WeddingService.create(company=user.company, data=wedding_payload)

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

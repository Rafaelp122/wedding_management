from decimal import Decimal
from uuid import uuid4

import pytest

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Budget, BudgetCategory
from apps.finances.schemas import BudgetCategoryIn, BudgetCategoryPatchIn
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
)
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


def _setup_budget(user, **kwargs):
    """Helper: cria wedding + budget no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding, **kwargs)
    return wedding, budget


@pytest.mark.django_db
class TestBudgetCategoryServiceCreate:
    """Testes de criação de categorias via BudgetCategoryService."""

    def test_create_category_success(self, user):
        """Criação de categoria vinculada ao budget do casamento."""
        wedding, budget = _setup_budget(user)

        data = {
            "budget": budget.uuid,
            "name": "Decoração",
            "allocated_budget": Decimal("5000.00"),
        }

        category = BudgetCategoryService.create(user.company, BudgetCategoryIn(**data))

        assert category.budget == budget
        assert category.wedding == wedding
        assert category.name == "Decoração"
        assert category.allocated_budget == Decimal("5000.00")

    def test_create_category_with_budget_instance(self, user):
        """create() aceita instância de Budget, não só UUID."""
        _, budget = _setup_budget(user)

        data = {
            "budget": budget.uuid,
            "name": "Fotografia",
            "allocated_budget": Decimal("3000.00"),
        }

        category = BudgetCategoryService.create(user.company, BudgetCategoryIn(**data))
        assert category.budget == budget

    def test_create_category_budget_not_found(self, user):
        """UUID de orçamento inexistente levanta ObjectNotFoundError."""
        data = {
            "budget": uuid4(),
            "name": "Fantasma",
            "allocated_budget": Decimal("1000.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetCategoryService.create(user.company, BudgetCategoryIn(**data))

        assert "budget_not_found_or_denied" in str(exc_info.value.code)

    def test_create_category_multitenancy(self):
        """Usuário A não pode criar categoria com budget do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, budget_b = _setup_budget(user_b)

        data = {
            "budget": budget_b.uuid,
            "name": "Invasão",
            "allocated_budget": Decimal("1000.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetCategoryService.create(user_a.company, BudgetCategoryIn(**data))

        assert "budget_not_found_or_denied" in str(exc_info.value.code)

    def test_create_category_rejects_budget_instance_from_other_tenant(self):
        """Instância de Budget pré-carregada também passa por validação tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, budget_b = _setup_budget(user_b)
        payload = BudgetCategoryIn.model_construct(
            budget=budget_b,
            name="Invasão por instância",
            description="",
            allocated_budget=Decimal("1000.00"),
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetCategoryService.create(user_a.company, payload)

        assert exc_info.value.code == "budget_not_found_or_denied"

    def test_create_category_exceeds_budget_cap_raises_error(self, user):
        """
        TOCTOU: criar categoria que ultrapassa o teto do orçamento
        levanta BusinessRuleViolation.
        """
        wedding, budget = _setup_budget(user, total_estimated=Decimal("10000.00"))
        BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
            allocated_budget=Decimal("9000.00"),
        )

        data = {
            "budget": budget.uuid,
            "name": "Excedente",
            "allocated_budget": Decimal("2000.00"),
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            BudgetCategoryService.create(user.company, BudgetCategoryIn(**data))

        assert "budget_cap_exceeded" in str(exc_info.value.code)

    def test_create_category_uses_select_for_update(self, user, mocker):
        """
        TOCTOU: create() deve usar select_for_update() no budget
        para evitar race condition na leitura da soma das categorias.
        """
        _, budget = _setup_budget(user)
        data = {
            "budget": budget.uuid,
            "name": "Teste Lock",
            "allocated_budget": Decimal("1000.00"),
        }

        mock_qs = mocker.MagicMock()
        mock_qs.select_for_update.return_value = mock_qs
        mock_qs.get.return_value = budget
        mocker.patch.object(Budget.objects, "for_tenant", return_value=mock_qs)

        BudgetCategoryService.create(user.company, BudgetCategoryIn(**data))

        mock_qs.select_for_update.assert_called_once()


@pytest.mark.django_db
class TestBudgetCategoryServiceUpdate:
    """Testes de atualização de categorias via BudgetCategoryService."""

    def test_update_category_name(self, user):
        """Atualização de campos simples é permitida."""
        wedding, budget = _setup_budget(user)
        category = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
            name="Antiga",
        )

        updated = BudgetCategoryService.update(
            user.company, category, BudgetCategoryPatchIn(name="Nova Categoria")
        )

        assert updated.name == "Nova Categoria"

    def test_update_category_allocated_budget_exceeds_cap_raises_error(self, user):
        """
        TOCTOU: atualizar allocated_budget ultrapassando o teto
        levanta BusinessRuleViolation.
        """
        wedding, budget = _setup_budget(user, total_estimated=Decimal("10000.00"))
        _ = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
            allocated_budget=Decimal("9000.00"),
        )
        category2 = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
            allocated_budget=Decimal("500.00"),
            name="Outra",
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            BudgetCategoryService.update(
                user.company,
                category2,
                BudgetCategoryPatchIn(allocated_budget=Decimal("2000.00")),
            )

        assert "budget_cap_exceeded" in str(exc_info.value.code)

    def test_update_category_uses_select_for_update(self, user, mocker):
        """
        TOCTOU: update() deve usar select_for_update() no budget
        para evitar race condition na leitura da soma das categorias.
        """
        wedding, budget = _setup_budget(user)
        category = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
        )

        mock_qs = mocker.MagicMock()
        mock_qs.select_for_update.return_value = mock_qs
        mock_qs.get.return_value = budget
        mocker.patch.object(Budget.objects, "for_tenant", return_value=mock_qs)

        BudgetCategoryService.update(
            user.company, category, BudgetCategoryPatchIn(name="Renomeada")
        )
        mock_qs.select_for_update.assert_called_once()

    def test_update_category_cross_tenant(self, user):
        """Categoria de outro tenant não pode ser atualizada."""
        from apps.users.tests.factories import UserFactory

        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_budget = BudgetFactory(wedding=other_wedding)
        other_category = BudgetCategoryFactory(
            budget=other_budget, wedding=other_wedding
        )

        with pytest.raises(ObjectNotFoundError):
            BudgetCategoryService.update(
                user.company, other_category, BudgetCategoryPatchIn(name="Hack")
            )


@pytest.mark.django_db
class TestBudgetCategoryServiceDelete:
    """Testes de deleção de categorias via BudgetCategoryService."""

    def test_delete_category_success(self, user):
        """Deleção de categoria sem despesas vinculadas é permitida."""
        wedding, budget = _setup_budget(user)
        category = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
        )

        BudgetCategoryService.delete(user.company, category)

        assert BudgetCategory.objects.filter(uuid=category.uuid).count() == 0

    def test_delete_category_with_expenses_fails(self, user):
        """Categoria com despesas vinculadas não pode ser deletada (PROTECT)."""
        wedding, budget = _setup_budget(user)
        category = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
        )
        ExpenseFactory(
            wedding=wedding,
            category=category,
            contract=None,
        )

        with pytest.raises(DomainIntegrityError) as exc_info:
            BudgetCategoryService.delete(user.company, category)

        assert "category_protected_error" in str(exc_info.value.code)
        assert BudgetCategory.objects.filter(uuid=category.uuid).count() == 1

    def test_delete_category_cross_tenant(self, user):
        """Categoria de outro tenant não pode ser deletada."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_budget = BudgetFactory(wedding=other_wedding)
        other_category = BudgetCategoryFactory(
            budget=other_budget, wedding=other_wedding
        )

        with pytest.raises(ObjectNotFoundError):
            BudgetCategoryService.delete(user.company, instance=other_category)


@pytest.mark.django_db
class TestBudgetCategoryServiceListAndGet:
    """Testes de listagem e obtenção de categorias."""

    def test_list_categories_multitenancy(self):
        """list() retorna apenas categorias do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, budget_a = _setup_budget(user_a)
        _, budget_b = _setup_budget(user_b)

        BudgetCategoryFactory(budget=budget_a, wedding=budget_a.wedding, name="Cat A")
        BudgetCategoryFactory(budget=budget_b, wedding=budget_b.wedding, name="Cat B")

        qs_a = BudgetCategoryService.list(user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().name == "Cat A"

        qs_b = BudgetCategoryService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().name == "Cat B"

    def test_list_categories_filter_by_wedding(self, user):
        """list() com wedding_id filtra por casamento."""
        wedding1, budget1 = _setup_budget(user)
        wedding2, budget2 = _setup_budget(user)

        BudgetCategoryFactory(budget=budget1, wedding=wedding1, name="Cat Wedding 1")
        BudgetCategoryFactory(budget=budget2, wedding=wedding2, name="Cat Wedding 2")

        qs = BudgetCategoryService.list(user.company, wedding_id=wedding1.uuid)
        assert qs.count() == 1
        assert qs.first().name == "Cat Wedding 1"

    def test_get_category_success(self, user):
        """get() retorna categoria por UUID."""
        wedding, budget = _setup_budget(user)
        category = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
            name="Buffet",
        )

        result = BudgetCategoryService.get(user.company, category.uuid)
        assert result.uuid == category.uuid
        assert result.name == "Buffet"

    def test_get_category_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetCategoryService.get(user.company, uuid4())

        assert str(exc_info.value.detail) == "Categoria de orçamento não encontrada."

    def test_get_category_multitenancy(self):
        """Usuário A não pode acessar categoria do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, budget_b = _setup_budget(user_b)
        category_b = BudgetCategoryFactory(
            budget=budget_b,
            wedding=budget_b.wedding,
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetCategoryService.get(user_a.company, category_b.uuid)

        assert str(exc_info.value.detail) == "Categoria de orçamento não encontrada."


@pytest.mark.django_db
class TestBudgetCategoryServiceSetupDefaults:
    """Testes de criação de categorias padrão via setup_defaults()."""

    def test_setup_defaults_creates_six_categories(self, user):
        """setup_defaults() deve criar 6 categorias padrão."""
        wedding, budget = _setup_budget(user)

        BudgetCategoryService.setup_defaults(user.company, wedding, budget)

        categories = BudgetCategory.objects.filter(budget=budget)
        assert categories.count() == 6

    def test_setup_defaults_expected_names(self, user):
        """Categorias padrão devem ter os nomes esperados."""
        wedding, budget = _setup_budget(user)

        BudgetCategoryService.setup_defaults(user.company, wedding, budget)

        names = set(
            BudgetCategory.objects.filter(budget=budget).values_list("name", flat=True)
        )
        expected = {
            "Espaço e Buffet",
            "Decoração e Flores",
            "Fotografia e Vídeo",
            "Música e Iluminação",
            "Assessoria",
            "Trajes e Beleza",
        }
        assert names == expected

    def test_setup_defaults_allocated_budget_is_zero(self, user):
        """Categorias padrão são criadas com allocated_budget = 0."""
        wedding, budget = _setup_budget(user)

        BudgetCategoryService.setup_defaults(user.company, wedding, budget)

        categories = BudgetCategory.objects.filter(budget=budget)
        for cat in categories:
            assert cat.allocated_budget == Decimal("0.00")

    def test_setup_defaults_is_idempotent(self, user):
        """
        TOCTOU: setup_defaults() não duplica categorias quando chamado
        múltiplas vezes.
        """
        wedding, budget = _setup_budget(user)

        BudgetCategoryService.setup_defaults(user.company, wedding, budget)
        assert BudgetCategory.objects.filter(budget=budget).count() == 6

        BudgetCategoryService.setup_defaults(user.company, wedding, budget)
        assert BudgetCategory.objects.filter(budget=budget).count() == 6

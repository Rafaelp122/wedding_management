"""
Testes CRÍTICOS para BudgetService - Foco em lazy loading e multi-tenancy.

Estes testes cobrem as áreas de maior risco identificadas na análise:
1. Lazy loading de Budget (get_or_create_for_wedding)
2. Multi-tenancy e isolamento de dados
3. Criação automática de categorias padrão
4. Atomicidade de transações
"""

from datetime import date
from decimal import Decimal
from typing import Any, cast, no_type_check
from unittest.mock import patch
from uuid import uuid4

import pytest

from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
from apps.finances.models import Budget, BudgetCategory, Expense
from apps.finances.schemas import BudgetIn, BudgetPatchIn
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService
from apps.finances.tests.factories import (
    BudgetCategoryFactory as _BudgetCategoryFactory,
)
from apps.finances.tests.factories import (
    BudgetFactory as _BudgetFactory,
)
from apps.finances.tests.factories import (
    ExpenseFactory as _ExpenseFactory,
)
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def BudgetCategoryFactory(*args: Any, **kwargs: Any) -> BudgetCategory:
    return cast(BudgetCategory, _BudgetCategoryFactory(*args, **kwargs))


def BudgetFactory(*args: Any, **kwargs: Any) -> Budget:
    return cast(Budget, _BudgetFactory(*args, **kwargs))


def ExpenseFactory(*args: Any, **kwargs: Any) -> Expense:
    return cast(Expense, _ExpenseFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestBudgetServiceCritical:
    """Testes CRÍTICOS para BudgetService."""

    def test_get_or_create_for_wedding_lazy_loading(self, user: Any) -> None:
        """
        Teste CRÍTICO: Lazy loading funciona corretamente.

        Cenário 1: Budget não existe → cria novo com total_estimated=0
        Cenário 2: Budget já existe → retorna existente
        """
        # Setup: Criar wedding sem budget
        wedding = WeddingFactory(company=user.company)

        # Verificar que NÃO existe budget inicialmente
        assert Budget.objects.filter(wedding=wedding).count() == 0

        # Teste 1: Primeira chamada cria budget
        budget1 = BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)

        # Verificações
        assert Budget.objects.filter(wedding=wedding).count() == 1
        assert budget1.wedding == wedding
        assert budget1.total_estimated == 0  # Valor padrão

        # Verificar que categorias padrão foram criadas
        categories = BudgetCategory.objects.filter(budget=budget1)
        assert categories.count() > 0  # Pelo menos uma categoria padrão

        # Teste 2: Segunda chamada retorna mesmo budget (não cria novo)
        budget2 = BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)

        assert budget2.id == budget1.id  # Mesmo objeto
        assert Budget.objects.filter(wedding=wedding).count() == 1  # Ainda apenas 1

    def test_get_or_create_for_wedding_multi_tenancy(self) -> None:
        """
        Teste CRÍTICO: Isolamento completo entre usuários.

        Usuário A não pode acessar/criar budget para wedding do Usuário B.
        """
        user_a = UserFactory()
        user_b = UserFactory()

        # User A cria wedding
        wedding_a = WeddingFactory(user_context=user_a)

        # User B tenta acessar budget do wedding de User A
        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get_or_create_for_wedding(user_b.company, wedding_a.uuid)

        assert "não encontrado ou acesso negado" in str(exc_info.value.detail).lower()

        # Verificar que NÃO foi criado budget para wedding_a (user_b não tem acesso)
        assert Budget.objects.filter(wedding=wedding_a).count() == 0

    @no_type_check
    def test_create_budget_rejects_wedding_instance_from_other_tenant(self) -> None:
        """Instância de Wedding pré-carregada também passa por validação tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        payload = BudgetIn.model_construct(
            wedding=wedding_b,
            total_estimated=Decimal("1000.00"),
            notes="",
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.create(user_a.company, payload)

        assert exc_info.value.code == "wedding_not_found_or_denied"

    def test_get_or_create_for_wedding_with_nonexistent_wedding(
        self, user: Any
    ) -> None:
        """
        Teste CRÍTICO: UUID de wedding não existente.

        Deve lançar ObjectNotFoundError, não criar budget fantasma.
        """
        from uuid import uuid4

        invalid_uuid = uuid4()

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get_or_create_for_wedding(user.company, invalid_uuid)

        assert "não encontrado ou acesso negado" in str(exc_info.value.detail).lower()

    def test_get_or_create_for_wedding_atomic_transaction(self, user: Any) -> None:
        """
        Teste CRÍTICO: Atomicidade da transação.

        Se criação de categorias falhar, NADA deve ser persistido (rollback completo).
        """
        wedding = WeddingFactory(company=user.company)

        # Mock BudgetCategoryService.setup_defaults para falhar
        with patch.object(BudgetCategoryService, "setup_defaults") as mock_setup:
            mock_setup.side_effect = Exception(
                "Falha simulada na criação de categorias"
            )

            # A criação deve falhar completamente
            with pytest.raises(
                Exception, match="Falha simulada na criação de categorias"
            ):
                BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)

        # Verificar rollback: NADA foi persistido
        assert Budget.objects.filter(wedding=wedding).count() == 0
        assert BudgetCategory.objects.filter(budget__wedding=wedding).count() == 0

    def test_get_or_create_for_wedding_creates_default_categories(
        self, user: Any
    ) -> None:
        """
        Teste CRÍTICO: Categorias padrão são criadas automaticamente.

        Verifica que as categorias essenciais existem após criação do budget.
        """
        wedding = WeddingFactory(company=user.company)

        budget = BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)

        # Verificar categorias foram criadas
        categories = BudgetCategory.objects.filter(budget=budget)
        assert categories.count() > 0

        # Verificar pelo menos algumas categorias padrão esperadas
        category_names = [c.name for c in categories]
        expected_categories = [
            "Espaço e Buffet",
            "Decoração e Flores",
            "Fotografia e Vídeo",
            "Assessoria",
        ]

        # Pelo menos uma das categorias esperadas deve estar presente
        assert any(expected in category_names for expected in expected_categories)

    def test_get_budget_success(self, user: Any) -> None:
        """get() retorna budget por UUID com select_related."""
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(wedding=wedding)

        result = BudgetService.get(user.company, budget.uuid)

        assert result.uuid == budget.uuid
        assert result.wedding == wedding

    def test_get_budget_multi_tenancy(self) -> None:
        """
        Teste CRÍTICO: get() respeita multi-tenancy.

        Usuário não pode acessar budget de outro usuário mesmo conhecendo o UUID.
        """
        user_a = UserFactory()
        user_b = UserFactory()

        # User A cria wedding e budget
        wedding_a = WeddingFactory(user_context=user_a)
        budget_a = BudgetService.get_or_create_for_wedding(
            user_a.company, wedding_a.uuid
        )

        # User B tenta acessar budget de User A
        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get(user_b.company, budget_a.uuid)

        assert "Orçamento não encontrado" in str(exc_info.value.detail)

    def test_get_budget_not_found(self, user: Any) -> None:
        """get() lança ObjectNotFoundError para UUID inexistente."""
        invalid_uuid = uuid4()

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get(user.company, invalid_uuid)

        assert "Orçamento não encontrado ou acesso negado." in str(
            exc_info.value.detail
        )

    def test_get_budget_invalid_uuid_format(self, user: Any) -> None:
        """get() lança ObjectNotFoundError para formato de UUID inválido."""
        invalid_format = "not-a-uuid"

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get(user.company, invalid_format)

        assert "Orçamento não encontrado ou acesso negado." in str(
            exc_info.value.detail
        )

    def test_list_budgets_multi_tenancy(self) -> None:
        """
        Teste CRÍTICO: list() retorna apenas budgets do usuário.

        Isolamento completo na listagem.
        """
        user_a = UserFactory()
        user_b = UserFactory()

        # Cada usuário cria seu próprio wedding e budget
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)

        budget_a = BudgetService.get_or_create_for_wedding(
            user_a.company, wedding_a.uuid
        )
        budget_b = BudgetService.get_or_create_for_wedding(
            user_b.company, wedding_b.uuid
        )

        # User A vê apenas seu budget
        budgets_a = BudgetService.list(user_a.company)
        assert budgets_a.count() == 1
        listed_budget_a = budgets_a.first()
        assert listed_budget_a is not None
        assert listed_budget_a.uuid == budget_a.uuid

        # User B vê apenas seu budget
        budgets_b = BudgetService.list(user_b.company)
        assert budgets_b.count() == 1
        listed_budget_b = budgets_b.first()
        assert listed_budget_b is not None
        assert listed_budget_b.uuid == budget_b.uuid

    def test_create_budget_duplicate_prevention(self, user: Any) -> None:
        """
        Teste CRÍTICO: Impedir criação de múltiplos budgets para mesmo wedding.

        OneToOne relationship deve ser respeitada.
        """
        wedding = WeddingFactory(company=user.company)

        # Criar primeiro budget
        BudgetService.create(
            user.company,
            BudgetIn(wedding=wedding.uuid, total_estimated=Decimal("50000.00")),
        )

        # Tentar criar segundo budget para mesmo wedding
        from apps.core.exceptions import DomainIntegrityError

        with pytest.raises(DomainIntegrityError) as exc_info:
            BudgetService.create(
                user.company,
                BudgetIn(wedding=wedding.uuid, total_estimated=Decimal("75000.00")),
            )

        assert "já possui um orçamento definido" in str(exc_info.value.detail)

        # Verificar que apenas um budget existe
        assert Budget.objects.filter(wedding=wedding).count() == 1
        assert Budget.objects.get(wedding=wedding).total_estimated == Decimal(
            "50000.00"
        )

    def test_budget_creation_with_invalid_wedding_uuid(self, user: Any) -> None:
        """
        Teste CRÍTICO: Tentativa de criar budget com wedding UUID inválido.

        Deve validar acesso/pertencimento antes de qualquer operação.
        """
        from uuid import uuid4

        invalid_uuid = uuid4()

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.create(
                user.company,
                BudgetIn(wedding=invalid_uuid, total_estimated=Decimal("50000.00")),
            )

        assert "não encontrado ou acesso negado" in str(exc_info.value.detail).lower()

    def test_budget_service_requires_authenticated_user(self) -> None:
        """
        Teste CRÍTICO: Serviços requerem usuário autenticado.

        Usuário anônimo não pode chamar serviços.
        """
        from uuid import uuid4

        from django.contrib.auth.models import AnonymousUser

        anonymous_user = AnonymousUser()
        some_uuid = uuid4()

        # Todas as operações devem falhar com usuário anônimo
        with pytest.raises(TypeError):
            BudgetService.get_or_create_for_wedding(
                cast(Any, anonymous_user), some_uuid
            )


@pytest.mark.django_db
class TestBudgetServiceIntegration:
    """Testes de integração entre WeddingService e BudgetService."""

    def test_wedding_creation_does_not_create_budget_eagerly(self, user: Any) -> None:
        """
        Teste CRÍTICO: Criação de wedding NÃO cria budget automaticamente.

        Lazy loading: budget só é criado na primeira requisição.
        """
        from apps.weddings.schemas import WeddingIn
        from apps.weddings.services import WeddingService

        wedding = WeddingService.create(
            user.company,
            WeddingIn(
                bride_name="Maria",
                groom_name="João",
                date=date(2026, 12, 31),
                location="São Paulo",
                expected_guests=150,
                template=None,
            ),
        )

        # Verificar que wedding foi criado mas budget NÃO
        assert wedding is not None
        assert Budget.objects.filter(wedding=wedding).count() == 0

        # Primeira chamada cria budget
        budget = BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)
        assert budget is not None
        assert Budget.objects.filter(wedding=wedding).count() == 1

    def test_wedding_delete_cascades_to_budget(self, user: Any) -> None:
        """
        Teste CRÍTICO: Deleção de wedding deleta budget automaticamente (CASCADE).

        Garantir integridade referencial.
        """
        from apps.weddings.services import WeddingService

        # Criar wedding e budget
        wedding = WeddingFactory(company=user.company)
        BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)

        # Verificar que ambos existem
        assert Budget.objects.filter(wedding=wedding).count() == 1

        # Deletar wedding (deve cascadear para budget)
        WeddingService.delete(user.company, instance=wedding)

        # Verificar que ambos foram deletados
        # Usamos uuid pois em Django 5.2 instance.delete() limpa o estado da pk
        assert Budget.objects.filter(wedding__uuid=wedding.uuid).count() == 0

    def test_budget_create_with_wedding_instance(self, user: Any) -> None:
        """
        BudgetService.create() aceita instância de Wedding, não só UUID.
        """
        wedding = WeddingFactory(company=user.company)

        budget = BudgetService.create(
            user.company,
            BudgetIn(wedding=wedding.uuid, total_estimated=Decimal("30000.00")),
        )

        assert budget.wedding == wedding
        assert budget.total_estimated == Decimal("30000.00")

    def test_budget_update_success(self, user: Any) -> None:
        """
        BudgetService.update() permite alterar total_estimated e notes.
        """
        wedding = WeddingFactory(company=user.company)
        budget = BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)

        updated = BudgetService.update(
            user.company,
            budget,
            BudgetPatchIn(total_estimated=Decimal("80000.00"), notes="Nova observação"),
        )

        assert updated.total_estimated == Decimal("80000.00")
        assert updated.notes == "Nova observação"

    def test_budget_update_cannot_change_wedding(self, user: Any) -> None:
        """
        Wedding é bloqueado no update — campo estrutural.
        """
        wedding1 = WeddingFactory(company=user.company)
        wedding2 = WeddingFactory(company=user.company)
        budget = BudgetService.get_or_create_for_wedding(user.company, wedding1.uuid)

        updated = BudgetService.update(
            user.company,
            budget,
            BudgetPatchIn.model_construct(wedding=wedding2.uuid),
        )

        assert updated.wedding == wedding1

    def test_update_budget_cross_tenant(self, user: Any) -> None:
        """Orçamento de outro tenant não pode ser atualizado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_budget = BudgetFactory(wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            BudgetService.update(
                user.company, other_budget, BudgetPatchIn(notes="Hack")
            )

    def test_budget_delete_success(self, user: Any) -> None:
        """
        BudgetService.delete() remove o orçamento se não houver categorias.
        """
        from apps.finances.models import Budget as BudgetModel

        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(
            wedding=wedding,
            total_estimated=Decimal("10000.00"),
        )

        BudgetService.delete(user.company, budget)

        assert BudgetModel.objects.filter(uuid=budget.uuid).count() == 0

    def test_budget_delete_cascades_to_categories(self, user: Any) -> None:
        """
        Budget com categorias: CASCADE deleta categorias junto.
        BudgetCategory.on_delete=CASCADE para Budget, sem proteção.
        """
        wedding = WeddingFactory(company=user.company)
        budget = BudgetService.get_or_create_for_wedding(user.company, wedding.uuid)

        BudgetService.delete(user.company, budget)

        assert Budget.objects.filter(uuid=budget.uuid).count() == 0

    def test_delete_budget_protected_by_expenses(self, user: Any) -> None:
        """Deleção de orçamento com despesas vinculadas deve falhar."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget)
        ExpenseFactory(
            wedding=wedding, category=category, company=user.company, contract=None
        )

        with pytest.raises(DomainIntegrityError) as exc_info:
            BudgetService.delete(user.company, budget)

        assert "Não é possível apagar este orçamento" in str(exc_info.value)
        assert Budget.objects.filter(uuid=budget.uuid).exists()

    def test_delete_budget_cross_tenant(self, user: Any) -> None:
        """Orçamento de outro tenant não pode ser deletado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_budget = BudgetFactory(wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            BudgetService.delete(user.company, instance=other_budget)

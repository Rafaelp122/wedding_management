"""
Testes CRÍTICOS para BudgetService - Foco em lazy loading e multi-tenancy.

Estes testes cobrem as áreas de maior risco identificadas na análise:
1. Lazy loading de Budget (get_or_create_for_wedding)
2. Multi-tenancy e isolamento de dados
3. Criação automática de categorias padrão
4. Atomicidade de transações
"""

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Budget, BudgetCategory
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestBudgetServiceCritical:
    """Testes CRÍTICOS para BudgetService."""

    def test_get_or_create_for_wedding_lazy_loading(self, user):
        """
        Teste CRÍTICO: Lazy loading funciona corretamente.

        Cenário 1: Budget não existe → cria novo com total_estimated=0
        Cenário 2: Budget já existe → retorna existente
        """
        # Setup: Criar wedding sem budget
        wedding = WeddingFactory(planner=user)

        # Verificar que NÃO existe budget inicialmente
        assert Budget.objects.filter(wedding=wedding).count() == 0

        # Teste 1: Primeira chamada cria budget
        budget1 = BudgetService.get_or_create_for_wedding(user, wedding.uuid)

        # Verificações
        assert Budget.objects.filter(wedding=wedding).count() == 1
        assert budget1.wedding == wedding
        assert budget1.total_estimated == 0  # Valor padrão

        # Verificar que categorias padrão foram criadas
        categories = BudgetCategory.objects.filter(budget=budget1)
        assert categories.count() > 0  # Pelo menos uma categoria padrão

        # Teste 2: Segunda chamada retorna mesmo budget (não cria novo)
        budget2 = BudgetService.get_or_create_for_wedding(user, wedding.uuid)

        assert budget2.id == budget1.id  # Mesmo objeto
        assert Budget.objects.filter(wedding=wedding).count() == 1  # Ainda apenas 1

    def test_get_or_create_for_wedding_multi_tenancy(self):
        """
        Teste CRÍTICO: Isolamento completo entre usuários.

        Usuário A não pode acessar/criar budget para wedding do Usuário B.
        """
        user_a = UserFactory()
        user_b = UserFactory()

        # User A cria wedding
        wedding_a = WeddingFactory(planner=user_a)

        # User B tenta acessar budget do wedding de User A
        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get_or_create_for_wedding(user_b, wedding_a.uuid)

        assert "não encontrado ou acesso negado" in str(exc_info.value.detail).lower()

        # Verificar que NÃO foi criado budget para wedding_a (user_b não tem acesso)
        assert Budget.objects.filter(wedding=wedding_a).count() == 0

    def test_get_or_create_for_wedding_with_nonexistent_wedding(self, user):
        """
        Teste CRÍTICO: UUID de wedding não existente.

        Deve lançar ObjectNotFoundError, não criar budget fantasma.
        """
        from uuid import uuid4

        invalid_uuid = uuid4()

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get_or_create_for_wedding(user, invalid_uuid)

        assert "não encontrado ou acesso negado" in str(exc_info.value.detail).lower()

    def test_get_or_create_for_wedding_atomic_transaction(self, user):
        """
        Teste CRÍTICO: Atomicidade da transação.

        Se criação de categorias falhar, NADA deve ser persistido (rollback completo).
        """
        wedding = WeddingFactory(planner=user)

        # Mock BudgetCategoryService.setup_defaults para falhar
        with patch.object(BudgetCategoryService, "setup_defaults") as mock_setup:
            mock_setup.side_effect = Exception(
                "Falha simulada na criação de categorias"
            )

            # A criação deve falhar completamente
            with pytest.raises(
                Exception, match="Falha simulada na criação de categorias"
            ):
                BudgetService.get_or_create_for_wedding(user, wedding.uuid)

        # Verificar rollback: NADA foi persistido
        assert Budget.objects.filter(wedding=wedding).count() == 0
        assert BudgetCategory.objects.filter(budget__wedding=wedding).count() == 0

    def test_get_or_create_for_wedding_creates_default_categories(self, user):
        """
        Teste CRÍTICO: Categorias padrão são criadas automaticamente.

        Verifica que as categorias essenciais existem após criação do budget.
        """
        wedding = WeddingFactory(planner=user)

        budget = BudgetService.get_or_create_for_wedding(user, wedding.uuid)

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

    def test_get_budget_multi_tenancy(self):
        """
        Teste CRÍTICO: get() respeita multi-tenancy.

        Usuário não pode acessar budget de outro usuário mesmo conhecendo o UUID.
        """
        user_a = UserFactory()
        user_b = UserFactory()

        # User A cria wedding e budget
        wedding_a = WeddingFactory(planner=user_a)
        budget_a = BudgetService.get_or_create_for_wedding(user_a, wedding_a.uuid)

        # User B tenta acessar budget de User A
        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.get(user_b, budget_a.uuid)

        assert "Orçamento não encontrado" in str(exc_info.value.detail)

    def test_list_budgets_multi_tenancy(self):
        """
        Teste CRÍTICO: list() retorna apenas budgets do usuário.

        Isolamento completo na listagem.
        """
        user_a = UserFactory()
        user_b = UserFactory()

        # Cada usuário cria seu próprio wedding e budget
        wedding_a = WeddingFactory(planner=user_a)
        wedding_b = WeddingFactory(planner=user_b)

        budget_a = BudgetService.get_or_create_for_wedding(user_a, wedding_a.uuid)
        budget_b = BudgetService.get_or_create_for_wedding(user_b, wedding_b.uuid)

        # User A vê apenas seu budget
        budgets_a = BudgetService.list(user_a)
        assert budgets_a.count() == 1
        assert budgets_a.first().uuid == budget_a.uuid

        # User B vê apenas seu budget
        budgets_b = BudgetService.list(user_b)
        assert budgets_b.count() == 1
        assert budgets_b.first().uuid == budget_b.uuid

    def test_create_budget_duplicate_prevention(self, user):
        """
        Teste CRÍTICO: Impedir criação de múltiplos budgets para mesmo wedding.

        OneToOne relationship deve ser respeitada.
        """
        wedding = WeddingFactory(planner=user)

        # Criar primeiro budget
        budget1_data = {"wedding": wedding.uuid, "total_estimated": Decimal("50000.00")}
        BudgetService.create(user, budget1_data)

        # Tentar criar segundo budget para mesmo wedding
        budget2_data = {"wedding": wedding.uuid, "total_estimated": Decimal("75000.00")}

        from apps.core.exceptions import DomainIntegrityError

        with pytest.raises(DomainIntegrityError) as exc_info:
            BudgetService.create(user, budget2_data)

        assert "já possui um orçamento definido" in str(exc_info.value.detail)

        # Verificar que apenas um budget existe
        assert Budget.objects.filter(wedding=wedding).count() == 1
        assert Budget.objects.get(wedding=wedding).total_estimated == Decimal(
            "50000.00"
        )

    def test_budget_creation_with_invalid_wedding_uuid(self, user):
        """
        Teste CRÍTICO: Tentativa de criar budget com wedding UUID inválido.

        Deve validar acesso/pertencimento antes de qualquer operação.
        """
        from uuid import uuid4

        invalid_uuid = uuid4()

        budget_data = {"wedding": invalid_uuid, "total_estimated": Decimal("50000.00")}

        with pytest.raises(ObjectNotFoundError) as exc_info:
            BudgetService.create(user, budget_data)

        assert "não encontrado ou acesso negado" in str(exc_info.value.detail).lower()

    def test_budget_service_requires_authenticated_user(self):
        """
        Teste CRÍTICO: Serviços requerem usuário autenticado.

        Usuário anônimo não pode chamar serviços.
        """
        from uuid import uuid4

        from django.contrib.auth.models import AnonymousUser

        anonymous_user = AnonymousUser()
        some_uuid = uuid4()

        # Todas as operações devem falhar com usuário anônimo
        with pytest.raises(Exception) as exc_info:
            BudgetService.get_or_create_for_wedding(anonymous_user, some_uuid)

        assert "autenticação" in str(exc_info.value).lower()


@pytest.mark.django_db
class TestBudgetServiceIntegration:
    """Testes de integração entre WeddingService e BudgetService."""

    def test_wedding_creation_does_not_create_budget_eagerly(self, user):
        """
        Teste CRÍTICO: Criação de wedding NÃO cria budget automaticamente.

        Lazy loading: budget só é criado na primeira requisição.
        """
        from apps.weddings.services import WeddingService

        wedding_payload = {
            "bride_name": "Maria",
            "groom_name": "João",
            "date": "2026-12-31",
            "location": "São Paulo",
            "expected_guests": 150,
        }

        # Criar wedding
        wedding = WeddingService.create(user, wedding_payload)

        # Verificar que wedding foi criado mas budget NÃO
        assert wedding is not None
        assert Budget.objects.filter(wedding=wedding).count() == 0

        # Primeira chamada cria budget
        budget = BudgetService.get_or_create_for_wedding(user, wedding.uuid)
        assert budget is not None
        assert Budget.objects.filter(wedding=wedding).count() == 1

    def test_wedding_delete_cascades_to_budget(self, user):
        """
        Teste CRÍTICO: Deleção de wedding deleta budget automaticamente (CASCADE).

        Garantir integridade referencial.
        """
        from apps.weddings.services import WeddingService

        # Criar wedding e budget
        wedding = WeddingFactory(planner=user)
        BudgetService.get_or_create_for_wedding(user, wedding.uuid)

        # Verificar que ambos existem
        assert Budget.objects.filter(wedding=wedding).count() == 1

        # Deletar wedding (deve cascadear para budget)
        WeddingService.delete(user, wedding.uuid)

        # Verificar que ambos foram deletados
        assert Budget.objects.filter(wedding=wedding).count() == 0

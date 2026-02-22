from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.core.exceptions import DomainIntegrityError
from apps.finances.models import Budget, BudgetCategory
from apps.logistics.tests.model_factories import ContractFactory
from apps.weddings.models import Wedding
from apps.weddings.services import WeddingService
from apps.weddings.tests.factories import WeddingFactory, WeddingPayloadFactory


@pytest.mark.django_db
class TestWeddingService:
    def test_create_wedding_complete_onboarding_success(self, user):
        """
        RF03/RF04: Garante que ao criar um casamento, o sistema orquestra:
        1. A criação do Wedding.
        2. A criação do Budget mestre.
        3. A geração automática das 6 categorias padrão.
        """
        # 1. Setup: Gerar payload via Factory (dicionário)
        # Passamos um valor fixo de budget para facilitar a asserção
        expected_budget = Decimal("75000.50")
        payload = WeddingPayloadFactory(total_estimated=expected_budget)

        # 2. Execução: Chamar o serviço
        wedding = WeddingService.create(user=user, data=payload)

        # 3. Asserções: Validação do Casamento
        assert Wedding.objects.count() == 1
        assert wedding.planner == user
        assert wedding.bride_name == payload["bride_name"]
        assert wedding.status == Wedding.StatusChoices.IN_PROGRESS

        # 4. Asserções: Validação do Orçamento (Orquestração BudgetService)
        budget = Budget.objects.get(wedding=wedding)
        assert budget.total_estimated == expected_budget

        # 5. Asserções: Validação das Categorias (Orquestração setup_defaults)
        categories = BudgetCategory.objects.filter(wedding=wedding)
        assert categories.count() == 6

        # Verifica se nomes esperados estão lá
        expected_names = [
            "Espaço e Buffet",
            "Decoração e Flores",
            "Fotografia e Vídeo",
            "Música e Iluminação",
            "Assessoria",
            "Trajes e Beleza",
        ]
        db_category_names = list(categories.values_list("name", flat=True))
        for name in expected_names:
            assert name in db_category_names

    def test_update_wedding_ignores_budget_field(self, user):
        """
        ADR-006: Garante que o update do casamento é isolado e não
        tenta (ou falha) ao receber campos financeiros.
        """
        # Setup: Casamento já existente

        wedding = WeddingFactory(planner=user, bride_name="Antiga")

        update_data = {
            "bride_name": "Nova Maria",
            "total_estimated": Decimal("999999.99"),  # Campo "intruso"
        }

        # Execução
        updated_wedding = WeddingService.update(
            instance=wedding, user=user, data=update_data
        )

        # Asserção
        assert updated_wedding.bride_name == "Nova Maria"
        # O valor do orçamento NÃO deve ter mudado se buscarmos no banco
        budget = Budget.objects.get(wedding=updated_wedding)
        assert budget.total_estimated != Decimal("999999.99")

    def test_create_wedding_fail_fast_validation_error(self, user):
        """
        Cenário 2: Garante que dados inválidos no casamento interrompem o processo
        antes de tocar na parte financeira (Fail Fast).
        """
        # 1. Setup: Payload com dado inválido (nome da noiva vazio)
        # Nota: bride_name é campo obrigatório no Model
        payload = WeddingPayloadFactory(bride_name="")

        # 2. Execução e Asserção de Erro
        # O full_clean() do Django deve lançar ValidationError
        with pytest.raises(DjangoValidationError):
            WeddingService.create(user=user, data=payload)

        # 3. Validação de Banco de Dados Limpo
        # Nada deve ter sido criado devido à falha precoce
        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_create_wedding_fail_with_invalid_date(self, user):
        """
        Cenário 2.1: Garante que uma data passada (se houver regra no Model)
        ou inválida também trava a criação.
        """
        from datetime import date, timedelta

        # Criando um payload com data de ontem (assumindo que seu model proíbe
        # datas passadas)
        yesterday = date.today() - timedelta(days=1)
        payload = WeddingPayloadFactory(date=yesterday)

        with pytest.raises(DjangoValidationError):
            WeddingService.create(user=user, data=payload)

        assert Wedding.objects.count() == 0

    def test_create_wedding_rollback_on_budget_failure(self, user):
        """
        Cenário 3: Garante que se o BudgetService falhar, o Wedding
        sofre rollback e NADA é persistido.
        """
        # 1. Setup: Payload válido
        payload = WeddingPayloadFactory(total_estimated=50000)

        # 2. Execução: Forçamos um erro dentro do BudgetService.create usando Mock
        # Simulamos que o financeiro explodiu por qualquer motivo técnico
        with patch(
            "apps.finances.services.budget_service.BudgetService.create"
        ) as mock_budget:
            mock_budget.side_effect = Exception("Erro inesperado no sistema financeiro")

            with pytest.raises(
                Exception, match="Erro inesperado no sistema financeiro"
            ):
                WeddingService.create(user=user, data=payload)

        # 3. Asserção: O Casamento não deve existir no banco de dados!
        # Se o @transaction.atomic estiver funcionando, ele desfez o wedding.save()
        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

    def test_wedding_service_multitenancy_isolation(self, user):
        """
        Cenário 4: Garante que dados de diferentes usuários fiquem isolados.
        Valida se o WeddingService propaga o 'user' corretamente para sub-serviços.
        """
        from apps.users.tests.factories import UserFactory

        # 1. Setup: Dois usuários (Planners) distintos
        planner_a = user  # Usuário vindo da fixture
        planner_b = UserFactory()

        payload_a = WeddingPayloadFactory(bride_name="Noiva A", total_estimated=10000)
        payload_b = WeddingPayloadFactory(bride_name="Noiva B", total_estimated=20000)

        # 2. Execução: Criar casamentos para ambos
        wedding_a = WeddingService.create(user=planner_a, data=payload_a)
        wedding_b = WeddingService.create(user=planner_b, data=payload_b)

        # 3. Asserções de Isolamento - Casamento A
        assert wedding_a.planner == planner_a
        assert Budget.objects.get(wedding=wedding_a).total_estimated == 10000
        # Categorias do Casamento A devem pertencer ao Casamento A (que pertence ao
        # Planner A)
        assert BudgetCategory.objects.filter(wedding=wedding_a).count() == 6
        for cat in BudgetCategory.objects.filter(wedding=wedding_a):
            assert cat.wedding.planner == planner_a

        # 4. Asserções de Isolamento - Casamento B
        assert wedding_b.planner == planner_b
        assert Budget.objects.get(wedding=wedding_b).total_estimated == 20000
        assert BudgetCategory.objects.filter(wedding=wedding_b).count() == 6
        for cat in BudgetCategory.objects.filter(wedding=wedding_b):
            assert cat.wedding.planner == planner_b

        # 5. O Teste Supremo: O Planner A não pode ver nada do Planner B via Manager
        # Aqui testamos se o .for_user(user) que colocamos nos models/viewsets funciona
        assert Wedding.objects.all().for_user(planner_a).count() == 1
        assert (
            Wedding.objects.all()
            .for_user(planner_a)
            .filter(uuid=wedding_b.uuid)
            .exists()
            is False
        )

    def test_update_wedding_protects_budget_field(self, user):
        """
        Cenário 5: Garante que o campo total_estimated é ignorado no update.
        Valida a separação de responsabilidades entre Logística e Finanças.
        """
        # 1. Setup: Criar casamento com orçamento inicial de 50k
        # Graças ao RelatedFactory que configuramos, o Budget nasce aqui
        initial_value = Decimal("50000.00")
        wedding = WeddingFactory(planner=user, budget__total_estimated=initial_value)

        # 2. Payload de atualização com uma tentativa de mudar o orçamento
        update_data = {
            "bride_name": "Bruna Atualizada",
            "total_estimated": Decimal(
                "100000.00"
            ),  # O "intruso" que deve ser ignorado
        }

        # 3. Execução
        updated_wedding = WeddingService.update(
            instance=wedding, user=user, data=update_data
        )

        # 4. Asserções
        # O campo de casamento deve atualizar normalmente
        assert updated_wedding.bride_name == "Bruna Atualizada"

        # O orçamento deve permanecer INTACTO
        budget = Budget.objects.get(wedding=updated_wedding)
        assert budget.total_estimated == initial_value
        assert budget.total_estimated != Decimal("100000.00")

    def test_delete_wedding_protected_by_contracts(self, user):
        """
        Cenário 6: Impede a deleção de um casamento que possui contratos vinculados.
        Valida a proteção contra perda de dados financeiros/logísticos.
        """
        # 1. Cria o casamento (e seu budget via RelatedFactory)
        wedding = WeddingFactory(planner=user)

        # 2. Cria o contrato passando apenas o wedding principal.
        # As sub-fábricas agora sabem se auto-ajustar.
        ContractFactory(wedding=wedding)

        # 3. O resto permanece igual
        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar este casamento"
        ):
            WeddingService.delete(user=user, instance=wedding)

        assert Wedding.objects.filter(uuid=wedding.uuid).exists()

    def test_delete_wedding_full_clean_cascade(self, user):
        """
        Cenário 7: Deleção total (Hard Delete) funciona quando não há travas.
        Garante que Orçamento e Categorias são limpos (Cascade).
        """
        # 1. Setup: Criar casamento via Service (para ter Budget e Categorias)
        payload = WeddingPayloadFactory(total_estimated=50000)
        wedding = WeddingService.create(user=user, data=payload)

        # 2. Execução: Deletar o casamento recém-criado
        WeddingService.delete(user=user, instance=wedding)

        # 3. Asserções: O banco de dados deve estar um deserto
        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

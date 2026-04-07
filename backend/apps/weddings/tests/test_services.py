from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.finances.models import Budget, BudgetCategory
from apps.finances.tests.factories import BudgetFactory
from apps.logistics.tests.factories import ContractFactory
from apps.weddings.models import Wedding
from apps.weddings.services import WeddingService
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingService:
    def test_create_wedding_does_not_create_financial_data_eagerly(
        self, user, wedding_payload
    ):
        """
        Com lazy loading ativo, criar casamento NÃO deve criar Budget/Categorias.
        """
        # Setup: inclui campo legado para garantir que seja ignorado com segurança
        wedding_payload["total_estimated"] = Decimal("75000.50")

        # Execução
        wedding = WeddingService.create(user=user, data=wedding_payload)

        # Asserções: Wedding criado
        assert Wedding.objects.count() == 1
        assert wedding.planner == user
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

        wedding = WeddingFactory(planner=user, bride_name="Antiga")
        BudgetFactory(wedding=wedding)

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
            WeddingService.create(user=user, data=wedding_payload)

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
            WeddingService.create(user=user, data=wedding_payload)

        assert Wedding.objects.count() == 0

    def test_create_wedding_does_not_call_budget_service(self, user, wedding_payload):
        """Com lazy loading, create de Wedding não deve acionar BudgetService."""
        with patch(
            "apps.finances.services.budget_service.BudgetService.create"
        ) as mock_budget:
            wedding = WeddingService.create(user=user, data=wedding_payload)

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
        wedding_a = WeddingService.create(user=planner_a, data=payload_a)
        wedding_b = WeddingService.create(user=planner_b, data=payload_b)

        # 3. Asserções (O coração do teste)
        assert wedding_a.planner == planner_a
        assert Wedding.objects.all().for_user(planner_a).count() == 1
        assert Wedding.objects.all().for_user(planner_b).count() == 1

        # 4. O Teste de Ouro: Isolamento via Manager
        # Se o Manager .for_user() estiver correto, o Planner A nunca verá o Casamento B
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
        """
        # 1. Setup: Criar casamento e orçamento separadamente
        initial_value = Decimal("50000.00")

        # O casamento nasce limpo, sem efeitos colaterais
        wedding = WeddingFactory(planner=user)

        # O orçamento é criado explicitamente para este teste
        BudgetFactory(wedding=wedding, total_estimated=initial_value)

        # 2. Payload de atualização com uma tentativa de mudar o orçamento
        update_data = {
            "bride_name": "Bruna Atualizada",
            "total_estimated": Decimal("100000.00"),
        }

        # 3. Execução
        updated_wedding = WeddingService.update(
            instance=wedding, user=user, data=update_data
        )

        # 4. Asserções
        assert updated_wedding.bride_name == "Bruna Atualizada"
        budget = Budget.objects.get(wedding=updated_wedding)
        assert budget.total_estimated == initial_value

    def test_delete_wedding_protected_by_contracts(self, user):
        """
        Cenário 6: Impede a deleção de um casamento que possui contratos vinculados.
        Valida a proteção contra perda de dados financeiros/logísticos.
        """
        # 1. Cria o casamento e orçamento
        wedding = WeddingFactory(planner=user)
        BudgetFactory(wedding=wedding)

        # 2. Cria o contrato passando apenas o wedding principal.
        # As sub-fábricas agora sabem se auto-ajustar.
        ContractFactory(wedding=wedding)

        # 3. O resto permanece igual
        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar este casamento"
        ):
            WeddingService.delete(user=user, uuid=wedding.uuid)

        assert Wedding.objects.filter(uuid=wedding.uuid).exists()

    def test_delete_wedding_full_clean_cascade(self, user, wedding_payload):
        """
        Cenário 7: Deleção total (Hard Delete) funciona quando não há travas.
        Garante que Orçamento e Categorias são limpos (Cascade).
        """
        # 1. Setup: Criar casamento sem efeitos financeiros automáticos.
        payload = {**wedding_payload, "total_estimated": Decimal("50000.00")}

        # O serviço cria apenas o Wedding; a camada financeira é lazy.
        wedding = WeddingService.create(user=user, data=payload)

        # 2. Execução: Deletar o casamento
        WeddingService.delete(user=user, uuid=wedding.uuid)

        # 3. Asserções: O banco de dados deve estar limpo
        assert Wedding.objects.count() == 0
        assert Budget.objects.count() == 0
        assert BudgetCategory.objects.count() == 0

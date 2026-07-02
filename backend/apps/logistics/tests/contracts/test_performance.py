import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.logistics.schemas import ContractOut
from apps.logistics.services.contract_service import ContractService
from apps.logistics.tests.factories import ContractFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestContractPerformance:
    def test_list_contracts_serialization_queries(self, user):
        """
        Verifica se a serialização de uma lista de contratos gera N+1 queries.
        """
        wedding = WeddingFactory(user_context=user)
        # Cria 5 contratos
        ContractFactory.create_batch(5, wedding=wedding, company=user.company)

        # Busca os contratos usando o serviço que já faz select_related e annotate
        contracts = list(ContractService.list(user.company, wedding_id=wedding.uuid))

        assert len(contracts) == 5

        # Mede as queries durante a serialização
        with CaptureQueriesContext(connection) as queries:
            for contract in contracts:
                # Simula o que o Django Ninja faz internamente
                data = ContractOut.from_orm(contract).dict()
                # Acessa os campos para garantir que os resolvers foram chamados
                _ = data["supplier_name"]
                _ = data["addendums_count"]

        # Atualmente, deve haver queries extras por causa do N+1 nos resolvers
        # Se houver 5 contratos, e 4 resolvers problemáticos
        # (supplier_name, phone, email, addendums_count)
        # Poderíamos esperar pelo menos 5 * X queries extras.
        # Na verdade, supplier_name/phone/email acessam obj.supplier.name, etc.
        # Se supplier já foi carregado via select_related, talvez não gere
        # queries extras para eles, MAS obj.addendums.count() certamente
        # gerará uma query por contrato.

        # O ideal seria 0 queries aqui, pois tudo deveria estar no objeto.
        msg = f"Deveria ter 0 queries na serialização, mas obteve {len(queries)}"
        assert len(queries) == 0, msg

    def test_single_contract_serialization_efficiency(self, user):
        """
        Verifica se a serialização de um único contrato é eficiente.
        """
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, company=user.company)

        # Busca com o serviço
        db_contract = ContractService.get(user.company, contract.uuid)

        with CaptureQueriesContext(connection) as queries:
            data = ContractOut.from_orm(db_contract).dict()
            _ = data["addendums_count"]

        # Mesmo para um único, o resolver agora deve ser eficiente se anotado
        assert len(queries) == 0, f"Deveria ter 0 queries, mas obteve {len(queries)}"

"""
Testes de rotas da API Ninja para Contratos e Termos Aditivos (/contracts/).
"""

from __future__ import annotations

import datetime as dt
from typing import Any, cast

import pytest
from django.test import Client

from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.contracts.models import Contract, ContractAddendum
from apps.contracts.tests.factories import (
    ContractAddendumFactory as _ContractAddendumFactory,
)
from apps.contracts.tests.factories import (
    ContractFactory as _ContractFactory,
)
from apps.contracts.tests.factories import SupplierFactory as _SupplierFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def ContractAddendumFactory(*args: Any, **kwargs: Any) -> ContractAddendum:
    return cast(ContractAddendum, _ContractAddendumFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Any:
    return _SupplierFactory(*args, **kwargs)


def ClientFactory(*args: Any, **kwargs: Any) -> Any:
    return _ClientFactory(*args, **kwargs)


def WeddingFactory(*args: Any, **kwargs: Any) -> Any:
    return _WeddingFactory(*args, **kwargs)


@pytest.mark.django_db
class TestContractsAPI:
    """Testes de integração dos endpoints HTTP de Contratos."""

    def test_list_contracts_api(self, auth_client: Client, user: Any) -> None:
        """GET /api/v1/contracts/ lista os contratos do tenant autenticado."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        ContractFactory(company=user.company, wedding=wedding)
        ContractFactory(company=user.company, wedding=wedding)

        response = auth_client.get("/api/v1/contracts/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 2

    def test_create_contract_api_supplier_and_planner(
        self, auth_client: Client, user: Any
    ) -> None:
        """POST /api/v1/contracts/ cria contratos de fornecedor e de assessoria."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        supplier = SupplierFactory(company=user.company)
        client = ClientFactory(company=user.company)

        # 1. Contrato de fornecedor
        supplier_payload = {
            "wedding": str(wedding.uuid),
            "supplier": str(supplier.uuid),
            "contract_type": "SUPPLIER",
            "name": "Bolo e Doces",
            "total_amount": "3200.00",
            "status": "DRAFT",
        }
        res_supplier = auth_client.post(
            "/api/v1/contracts/",
            data=supplier_payload,
            content_type="application/json",
        )
        assert res_supplier.status_code == 201
        data_sup = res_supplier.json()
        assert data_sup["contract_type"] == "SUPPLIER"
        assert data_sup["total_amount"] == "3200.00"

        # 2. Contrato de assessoria
        planner_payload = {
            "wedding": str(wedding.uuid),
            "client": str(client.uuid),
            "contract_type": "PLANNER",
            "service_tier": "COMPLETA",
            "name": "Assessoria Completa dos Sonhos",
            "total_amount": "8000.00",
            "installments_count": 5,
            "status": "DRAFT",
        }
        res_planner = auth_client.post(
            "/api/v1/contracts/",
            data=planner_payload,
            content_type="application/json",
        )
        assert res_planner.status_code == 201
        data_plan = res_planner.json()
        assert data_plan["contract_type"] == "PLANNER"
        assert data_plan["service_tier"] == "COMPLETA"
        assert data_plan["total_amount"] == "8000.00"

    def test_retrieve_contract_and_details_api(
        self, auth_client: Client, user: Any
    ) -> None:
        """GET /api/v1/contracts/{uuid}/ e /details/ retornam os dados consolidados."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        res_single = auth_client.get(f"/api/v1/contracts/{contract.uuid}/")
        assert res_single.status_code == 200
        assert res_single.json()["uuid"] == str(contract.uuid)

        res_details = auth_client.get(f"/api/v1/contracts/{contract.uuid}/details/")
        assert res_details.status_code == 200
        assert "contract" in res_details.json()
        assert "items" in res_details.json()
        assert "addendums" in res_details.json()

    def test_update_and_sign_contract_api(self, auth_client: Client, user: Any) -> None:
        """PATCH e POST sign atualizam e formalizam contrato."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        patch_res = auth_client.patch(
            f"/api/v1/contracts/{contract.uuid}/",
            data={"total_amount": "9500.00"},
            content_type="application/json",
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["total_amount"] == "9500.00"

        sign_res = auth_client.post(
            f"/api/v1/contracts/{contract.uuid}/sign/",
            data={"signed_date": str(dt.date.today())},
            content_type="application/json",
        )
        assert sign_res.status_code == 200
        assert sign_res.json()["status"] == "SIGNED"

    def test_contract_addendums_crud_api(self, auth_client: Client, user: Any) -> None:
        """Rotas de aditivos: criação, listagem, assinatura e cancelamento."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        # 1. Criação de aditivo
        addendum_payload = {
            "amount": "1800.00",
            "justification": "Inclusão de iluminação cênica",
        }
        res_create = auth_client.post(
            f"/api/v1/contracts/{contract.uuid}/addendums/",
            data=addendum_payload,
            content_type="application/json",
        )
        assert res_create.status_code == 201
        addendum_data = res_create.json()
        addendum_uuid = addendum_data["uuid"]
        assert addendum_data["amount"] == "1800.00"
        assert addendum_data["status"] == "PENDING"

        # 2. Listagem de aditivos
        res_list = auth_client.get(f"/api/v1/contracts/{contract.uuid}/addendums/")
        assert res_list.status_code == 200
        assert len(res_list.json()) == 1

        # 3. Assinatura de aditivo
        res_sign = auth_client.post(
            f"/api/v1/contracts/{contract.uuid}/addendums/{addendum_uuid}/sign/",
            data={"signed_date": str(dt.date.today())},
            content_type="application/json",
        )
        assert res_sign.status_code == 200
        assert res_sign.json()["status"] == "SIGNED"

        # 4. Cancelamento de aditivo
        res_cancel = auth_client.post(
            f"/api/v1/contracts/{contract.uuid}/addendums/{addendum_uuid}/cancel/",
        )
        assert res_cancel.status_code == 200
        assert res_cancel.json()["status"] == "CANCELED"

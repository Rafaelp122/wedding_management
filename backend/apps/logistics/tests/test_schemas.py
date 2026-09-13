"""Testes unitários para os schemas Pydantic/Ninja do domínio de logística."""

import uuid
from decimal import Decimal

import pytest
from pydantic import ValidationError

from apps.logistics.schemas import (
    ContractFullCreateIn,
    ContractIn,
    ContractPatchIn,
    ContractStatusTransitionIn,
    ContractUploadIn,
    ContractUploadUrlIn,
    ItemIn,
    ItemPatchIn,
    ItemStatusTransitionIn,
    SupplierIn,
    SupplierPatchIn,
)


class TestSupplierSchemas:
    """Testes para os schemas de Supplier."""

    def test_supplier_in_valid(self) -> None:
        schema = SupplierIn(
            name="  Buffet Estrela  ",
            cnpj="  00.000.000/0001-00  ",
            phone="  11999999999  ",
            email="  contato@estrela.com  ",
            address="  Rua das Flores, 123  ",
            city="  São Paulo  ",
            state="SP",
            website="https://estrela.com",
            notes="Observação",
        )
        assert schema.name == "Buffet Estrela"
        assert schema.cnpj == "00.000.000/0001-00"
        assert schema.phone == "11999999999"
        assert schema.email == "contato@estrela.com"
        assert schema.address == "Rua das Flores, 123"
        assert schema.city == "São Paulo"
        assert schema.state == "SP"

    def test_supplier_in_invalid_cnpj(self) -> None:
        with pytest.raises(ValidationError) as exc:
            SupplierIn(
                name="Fornecedor",
                cnpj="12345678000199",
                phone="11999999999",
                email="a@b.com",
            )
        assert "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX" in str(exc.value)

    def test_supplier_in_invalid_website(self) -> None:
        with pytest.raises(ValidationError):
            SupplierIn(
                name="Fornecedor",
                cnpj="00.000.000/0001-00",
                phone="11999999999",
                email="a@b.com",
                website="not-a-valid-url",
            )

    def test_supplier_patch_in_whitespace_and_validations(self) -> None:
        schema = SupplierPatchIn(
            name="  Buffet Lunar  ",
            cnpj="  00.000.000/0001-00  ",
            website="https://lunar.com",
        )
        assert schema.name == "Buffet Lunar"
        assert schema.cnpj == "00.000.000/0001-00"

        with pytest.raises(ValidationError):
            SupplierPatchIn(cnpj="invalido")

        with pytest.raises(ValidationError):
            SupplierPatchIn(website="url_invalida")


class TestContractSchemas:
    """Testes para os schemas de Contract."""

    def test_contract_in_valid(self) -> None:
        w_id = uuid.uuid4()
        s_id = uuid.uuid4()
        schema = ContractIn(
            wedding=w_id,
            supplier=s_id,
            name="  Contrato de Fotografia  ",
            total_amount=Decimal("5000.00"),
        )
        assert schema.name == "Contrato de Fotografia"
        assert schema.total_amount == Decimal("5000.00")

    def test_contract_in_name_validation(self) -> None:
        w_id = uuid.uuid4()
        s_id = uuid.uuid4()
        # Nome vazio
        with pytest.raises(ValidationError):
            ContractIn(
                wedding=w_id,
                supplier=s_id,
                name="",
                total_amount=Decimal("100.00"),
            )

        # Nome apenas espaços em branco é rejeitado devido ao
        # strip_whitespace + min_length=1
        with pytest.raises(ValidationError):
            ContractIn(
                wedding=w_id,
                supplier=s_id,
                name="   ",
                total_amount=Decimal("100.00"),
            )

    def test_contract_in_negative_amount_rejected(self) -> None:
        w_id = uuid.uuid4()
        s_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ContractIn(
                wedding=w_id,
                supplier=s_id,
                name="Contrato",
                total_amount=Decimal("-10.00"),
            )

    def test_contract_patch_in_validations(self) -> None:
        schema = ContractPatchIn(
            name="  Novo Nome  ",
            total_amount=Decimal("0.00"),
        )
        assert schema.name == "Novo Nome"
        assert schema.total_amount == Decimal("0.00")

        with pytest.raises(ValidationError):
            ContractPatchIn(name="")

        with pytest.raises(ValidationError):
            ContractPatchIn(total_amount=Decimal("-1.00"))

    def test_contract_status_transition_in(self) -> None:
        schema = ContractStatusTransitionIn(status="  SIGNED  ")
        assert schema.status == "SIGNED"

        with pytest.raises(ValidationError):
            ContractStatusTransitionIn(status="")

        with pytest.raises(ValidationError):
            ContractStatusTransitionIn(status="   ")

    def test_contract_full_create_in_validations(self) -> None:
        w_id = uuid.uuid4()
        s_id = uuid.uuid4()
        c_id = uuid.uuid4()

        # Sucesso
        schema = ContractFullCreateIn(
            wedding=w_id,
            supplier=s_id,
            name="  Contrato Completo  ",
            total_amount=Decimal("2500.00"),
            items_data='[{"name": "Item 1", "quantity": 2}]',
            create_expense=True,
            expense_category=c_id,
        )
        assert schema.name == "Contrato Completo"

        # JSON inválido em items_data
        with pytest.raises(ValidationError):
            ContractFullCreateIn(
                wedding=w_id,
                supplier=s_id,
                name="Contrato",
                total_amount=Decimal("100.00"),
                items_data="invalido",
            )

        # create_expense sem categoria
        with pytest.raises(ValidationError):
            ContractFullCreateIn(
                wedding=w_id,
                supplier=s_id,
                name="Contrato",
                total_amount=Decimal("100.00"),
                create_expense=True,
                expense_category=None,
            )

    def test_contract_upload_schemas(self) -> None:
        w_id = uuid.uuid4()
        url_in = ContractUploadUrlIn(
            filename="  documento.pdf  ",
            wedding_id=w_id,
        )
        assert url_in.filename == "documento.pdf"

        upload_in = ContractUploadIn(pdf_file_key="  path/to/key.pdf  ")
        assert upload_in.pdf_file_key == "path/to/key.pdf"


class TestItemSchemas:
    """Testes para os schemas de Item."""

    def test_item_in_valid(self) -> None:
        schema = ItemIn(
            name="  Cadeiras Tiffany  ",
            description="  Brancas de madeira  ",
            quantity=150,
        )
        assert schema.name == "Cadeiras Tiffany"
        assert schema.description == "Brancas de madeira"
        assert schema.quantity == 150

    def test_item_in_name_and_quantity_validation(self) -> None:
        # Nome vazio
        with pytest.raises(ValidationError):
            ItemIn(name="", quantity=1)

        # Quantidade 0 ou negativa
        with pytest.raises(ValidationError):
            ItemIn(name="Item", quantity=0)

        with pytest.raises(ValidationError):
            ItemIn(name="Item", quantity=-5)

    def test_item_patch_in_validations(self) -> None:
        schema = ItemPatchIn(name="  Mesa  ", quantity=2)
        assert schema.name == "Mesa"
        assert schema.quantity == 2

        with pytest.raises(ValidationError):
            ItemPatchIn(name="")

        with pytest.raises(ValidationError):
            ItemPatchIn(quantity=0)

    def test_item_status_transition_in(self) -> None:
        schema = ItemStatusTransitionIn(acquisition_status="  DONE  ")
        assert schema.acquisition_status == "DONE"

        with pytest.raises(ValidationError):
            ItemStatusTransitionIn(acquisition_status="")

        with pytest.raises(ValidationError):
            ItemStatusTransitionIn(acquisition_status="   ")

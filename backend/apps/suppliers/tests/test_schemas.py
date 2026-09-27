"""Testes unitários para os schemas Pydantic de fornecedores (apps.suppliers.schemas)."""

import pytest
from pydantic import ValidationError

from apps.suppliers.schemas import (
    PagedSupplierOut,
    SupplierIn,
    SupplierPatchIn,
)


class TestSupplierSchemas:
    """Suíte de testes para validação e serialização de schemas de fornecedor."""

    def test_supplier_in_valid(self) -> None:
        """SupplierIn aceita dados válidos com CNPJ canônico."""
        payload = SupplierIn(
            name="Buffet Elegance",
            cnpj="11.222.333/0001-81",
            phone="(11) 98765-4321",
            email="contato@elegance.com.br",
            state="SP",
            website="https://elegance.com.br",
        )
        assert payload.name == "Buffet Elegance"
        assert payload.cnpj == "11.222.333/0001-81"

    def test_supplier_in_invalid_cnpj_format(self) -> None:
        """SupplierIn rejeita CNPJ fora do padrão."""
        with pytest.raises(ValidationError):
            SupplierIn(
                name="Buffet Erro",
                cnpj="12345",
                phone="123",
                email="erro@buffet.com",
            )

    def test_supplier_in_invalid_cnpj_modulo11(self) -> None:
        """SupplierIn rejeita CNPJ com dígitos verificadores incorretos."""
        with pytest.raises(ValidationError) as exc_info:
            SupplierIn(
                name="Buffet Erro",
                cnpj="00.000.000/0001-00",
                phone="123",
                email="erro@buffet.com",
            )
        assert "CNPJ" in str(exc_info.value)

    def test_supplier_in_invalid_website(self) -> None:
        """SupplierIn rejeita website sem formato http/https."""
        with pytest.raises(ValidationError):
            SupplierIn(
                name="Buffet Erro",
                phone="123",
                email="erro@buffet.com",
                website="ftp://invalido.com",
            )

    def test_supplier_patch_in_partial(self) -> None:
        """SupplierPatchIn aceita campos opcionais parciais."""
        patch = SupplierPatchIn(name="Novo Nome", is_active=False)
        assert patch.name == "Novo Nome"
        assert patch.is_active is False
        assert patch.cnpj is None

    def test_paged_supplier_out_structure(self) -> None:
        """PagedSupplierOut valida envelope com items e count."""
        paged = PagedSupplierOut(items=[], count=0)
        assert paged.count == 0
        assert paged.items == []

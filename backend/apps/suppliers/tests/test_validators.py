"""Testes unitários para validação de CNPJ via Módulo 11 (apps.suppliers.validators)."""

import pytest
from django.core.exceptions import ValidationError

from apps.suppliers.validators import validate_cnpj_modulo11


class TestValidateCnpjModulo11:
    """Suíte de testes para a função canônica validate_cnpj_modulo11."""

    @pytest.mark.parametrize(
        "valid_cnpj",
        [
            "11.222.333/0001-81",
            "00.000.000/0001-91",
            "04.252.011/0001-10",
            "11222333000181",
            "00000000000191",
            "",
            None,
        ],
    )
    def test_valid_cnpjs_pass(self, valid_cnpj: str | None) -> None:
        """CNPJs válidos com ou sem máscara e valores vazios não devem levantar exceção."""
        validate_cnpj_modulo11(valid_cnpj)  # type: ignore[arg-type]

    def test_invalid_length_raises_validation_error(self) -> None:
        """CNPJ com quantidade de dígitos diferente de 14 deve levantar ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj_modulo11("123.456.789/00")
        assert "14 dígitos" in str(exc_info.value.message)
        assert exc_info.value.code == "invalid_cnpj_length"

    @pytest.mark.parametrize(
        "homogeneous",
        [
            "00.000.000/0000-00",
            "11.111.111/1111-11",
            "22.222.222/2222-22",
            "99.999.999/9999-99",
            "00000000000000",
        ],
    )
    def test_homogeneous_digits_rejected(self, homogeneous: str) -> None:
        """Sequências homogêneas devem ser rejeitadas."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj_modulo11(homogeneous)
        assert "repetidos" in str(exc_info.value.message)
        assert exc_info.value.code == "invalid_cnpj_homogeneous"

    def test_invalid_first_check_digit(self) -> None:
        """DV1 incorreto deve ser rejeitado."""
        # 11.222.333/0001-81 -> mudando 8 para 7
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj_modulo11("11.222.333/0001-71")
        assert "primeiro dígito verificador" in str(exc_info.value.message)
        assert exc_info.value.code == "invalid_cnpj_dv1"

    def test_invalid_second_check_digit(self) -> None:
        """DV2 incorreto deve ser rejeitado."""
        # 11.222.333/0001-81 -> mudando 1 para 2
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj_modulo11("11.222.333/0001-82")
        assert "segundo dígito verificador" in str(exc_info.value.message)
        assert exc_info.value.code == "invalid_cnpj_dv2"

    def test_legacy_fictitious_cnpj_is_rejected(self) -> None:
        """CNPJ fictício legado '00.000.000/0001-00' deve ser rejeitado pelo Módulo 11."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj_modulo11("00.000.000/0001-00")
        assert exc_info.value.code in ("invalid_cnpj_dv1", "invalid_cnpj_dv2")

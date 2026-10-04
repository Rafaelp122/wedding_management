"""Validadores canônicos para o domínio de Fornecedores."""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError


def validate_cnpj_modulo11(value: str) -> None:
    """Valida um número de CNPJ utilizando a regra canônica do Módulo 11 da Receita Federal.

    Regra de Negócio:
        BR-SUP-CNPJ-01: Exige 14 dígitos numéricos e rejeita dígitos homogêneos repetidos.
        BR-SUP-CNPJ-02: Validação dos dois dígitos verificadores via pesos do módulo 11.

    Args:
        value: Número de CNPJ com ou sem máscara de pontuação.

    Raises:
        ValidationError: Se o CNPJ for matematicamente inválido ou possuir formato incompatível.
    """
    if not value:
        return

    # Limpa pontuação mantendo apenas dígitos numéricos
    digits = re.sub(r"\D", "", value)

    if not digits:
        return

    if len(digits) != 14:
        raise ValidationError(
            "CNPJ deve conter exatamente 14 dígitos numéricos.",
            code="invalid_cnpj_length",
        )

    # Rejeita sequências homogêneas (ex: 00000000000000, 11111111111111, etc.)
    if digits == digits[0] * 14:
        raise ValidationError(
            "CNPJ não pode ser composto por dígitos repetidos.",
            code="invalid_cnpj_homogeneous",
        )

    # Cálculo do primeiro dígito verificador (DV1)
    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum1 = sum(
        int(digit) * weight
        for digit, weight in zip(digits[:12], weights_first, strict=True)
    )
    remainder1 = sum1 % 11
    expected_dv1 = 0 if remainder1 < 2 else 11 - remainder1

    if int(digits[12]) != expected_dv1:
        raise ValidationError(
            "CNPJ inválido (primeiro dígito verificador não confere).",
            code="invalid_cnpj_dv1",
        )

    # Cálculo do segundo dígito verificador (DV2)
    weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum2 = sum(
        int(digit) * weight
        for digit, weight in zip(digits[:13], weights_second, strict=True)
    )
    remainder2 = sum2 % 11
    expected_dv2 = 0 if remainder2 < 2 else 11 - remainder2

    if int(digits[13]) != expected_dv2:
        raise ValidationError(
            "CNPJ inválido (segundo dígito verificador não confere).",
            code="invalid_cnpj_dv2",
        )

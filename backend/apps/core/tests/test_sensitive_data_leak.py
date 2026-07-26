"""
Auditoria dinâmica contra vazamento de dados sensíveis em schemas de resposta da API.

Inspeciona todas as rotas e schemas de saída (response models) registrados na
instância da API Ninja para garantir que nenhum endpoint expõe campos sensíveis
como senhas, chaves privadas ou tokens em respostas públicas.
"""

import inspect
import typing
from typing import Any

import pydantic
import pytest

from config.api import api


SENSITIVE_FIELDS: set[str] = {
    "password",
    "password_hash",
    "raw_password",
    "secret_key",
    "private_key",
    "auth_token",
    "reset_token",
}


def _extract_pydantic_models(
    target: Any, visited: set[Any] | None = None
) -> set[type[pydantic.BaseModel]]:
    """
    Extrai recursivamente classes Pydantic/Ninja BaseModel a partir de qualquer
    anotação de tipo ou objeto de schema (incluindo List[Schema], Union, etc.).
    """
    if visited is None:
        visited = set()

    models: set[type[pydantic.BaseModel]] = set()
    if target is None or target in visited:
        return models

    visited.add(target)

    # Se for diretamente uma subclasse de BaseModel
    if inspect.isclass(target) and issubclass(target, pydantic.BaseModel):
        models.add(target)
        return models

    # Se for um wrapper Ninja ResponseModel com atributo .model ou .schema
    target_model = getattr(target, "model", None)
    if target_model is not None and inspect.isclass(target_model):
        if issubclass(target_model, pydantic.BaseModel):
            models.add(target_model)

    # Trata generics de typings (List[T], Union[T1, T2], etc.)
    origin = typing.get_origin(target)
    if origin is not None:
        for arg in typing.get_args(target):
            models.update(_extract_pydantic_models(arg, visited))

    return models


def _find_sensitive_fields_in_schema(
    schema_cls: type[pydantic.BaseModel],
    visited: set[type[pydantic.BaseModel]] | None = None,
) -> list[tuple[str, str]]:
    """
    Verifica se um schema Pydantic ou seus schemas aninhados contêm campos sensíveis.

    Returns:
        list[tuple[str, str]]: Lista de tuplas (nome_do_schema, nome_do_campo_sensível).
    """
    if visited is None:
        visited = set()

    if schema_cls in visited:
        return []

    visited.add(schema_cls)
    leaks: list[tuple[str, str]] = []
    model_fields = getattr(schema_cls, "model_fields", {})

    for field_name, field_info in model_fields.items():
        name_lower = field_name.lower()
        if name_lower in SENSITIVE_FIELDS:
            leaks.append((f"{schema_cls.__module__}.{schema_cls.__name__}", field_name))

        # Inspeciona tipos aninhados para detectar leakers em sub-schemas
        nested_models = _extract_pydantic_models(field_info.annotation)
        for nested in nested_models:
            leaks.extend(_find_sensitive_fields_in_schema(nested, visited))

    return leaks


@pytest.mark.django_db
class TestSensitiveDataLeak:
    """
    Suíte de testes para prevenir vazamento acidental de credenciais e segredos.
    """

    def test_no_public_response_schemas_contain_sensitive_fields(self) -> None:
        """
        Garante que 100% das rotas possuem schemas de resposta sem campos sensíveis.
        """
        violations: list[str] = []
        tested_schemas_count = 0

        for prefix, router in api._routers:
            for path, path_op in router.path_operations.items():
                full_path = f"{prefix}{path}"
                for op in path_op.operations:
                    response_models = getattr(op, "response_models", {})
                    if not response_models:
                        continue

                    for status_code, resp_model in response_models.items():
                        extracted_schemas = _extract_pydantic_models(resp_model)
                        for schema_cls in extracted_schemas:
                            tested_schemas_count += 1
                            leaks = _find_sensitive_fields_in_schema(schema_cls)
                            for schema_name, field_name in leaks:
                                msg = (
                                    f"Rota [{op.methods}] '{full_path}' "
                                    f"status {status_code} utiliza schema "
                                    f"'{schema_name}' com o campo '{field_name}'."
                                )
                                violations.append(msg)

        assert tested_schemas_count > 0, "Nenhum schema de resposta foi encontrado."
        assert not violations, (
            "Vazamento de dados sensíveis detectado nos schemas de resposta da API:\n"
            + "\n".join(violations)
        )

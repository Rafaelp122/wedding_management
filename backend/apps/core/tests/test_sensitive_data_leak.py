"""
Auditoria dinâmica contra vazamento de dados sensíveis em schemas de resposta da API.

Inspeciona dinamicamente os schemas de saída (Out DTOs / Response Models) dos módulos
da aplicação para garantir que nenhum endpoint expõe campos sensíveis como senhas,
chaves privadas ou tokens em respostas públicas.
"""

import importlib
import inspect
import typing
from pathlib import Path
from typing import Any

import pydantic
import pytest


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

        # Inspeciona tipos aninhados para detectar vazamentos em sub-schemas
        nested_models = _extract_pydantic_models(field_info.annotation)
        for nested in nested_models:
            leaks.extend(_find_sensitive_fields_in_schema(nested, visited))

    return leaks


def _discover_app_response_schemas() -> list[type[pydantic.BaseModel]]:
    """
    Descobre dinamicamente todas as classes de schema de saída (Out)
    nos módulos de schemas da aplicação.
    """
    apps_dir = Path(__file__).resolve().parent.parent.parent
    schemas: set[type[pydantic.BaseModel]] = set()

    for path in sorted(apps_dir.glob("**/*.py")):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue

        if path.name == "schemas.py" or "schemas" in path.parts:
            rel_path = path.relative_to(apps_dir.parent)
            module_name = str(rel_path.with_suffix("")).replace("/", ".")
            try:
                mod = importlib.import_module(module_name)
            except (ImportError, AttributeError):
                continue

            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if inspect.isclass(attr) and issubclass(attr, pydantic.BaseModel):
                    if attr.__module__.startswith("apps.") and (
                        attr_name.endswith("Out") or "Response" in attr_name
                    ):
                        schemas.add(attr)

    return sorted(schemas, key=lambda c: f"{c.__module__}.{c.__name__}")


@pytest.mark.django_db
class TestSensitiveDataLeak:
    """
    Suíte de testes para prevenir vazamento acidental de credenciais e segredos.
    """

    def test_no_public_response_schemas_contain_sensitive_fields(self) -> None:
        """
        Garante que 100% dos schemas de resposta públicos não expõem campos sensíveis.
        """
        violations: list[str] = []
        tested_schemas_count = 0

        # Percurso dinâmico de schemas de resposta nos módulos apps/*/schemas.py
        app_schemas = _discover_app_response_schemas()
        for schema_cls in app_schemas:
            tested_schemas_count += 1
            leaks = _find_sensitive_fields_in_schema(schema_cls)
            for schema_name, field_name in leaks:
                msg = (
                    f"Schema de resposta '{schema_name}' "
                    f"contém o campo sensível '{field_name}'."
                )
                violations.append(msg)

        assert tested_schemas_count > 0, "Nenhum schema de resposta foi encontrado."
        assert not violations, (
            "Vazamento de dados sensíveis detectado nos schemas de resposta da API:\n"
            + "\n".join(violations)
        )

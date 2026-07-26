"""
Testes de integridade de Schemas (Ninja / Pydantic).

Garante a conformidade com a regra de negócio BR-VAL01: nenhum campo
representando valor monetário/financeiro pode utilizar o tipo float,
exigindo Decimal (ou Decimal | None) para evitar imprecisões binárias
de ponto flutuante.
"""

import importlib
import inspect
import logging
import pkgutil
import typing
from typing import Any

import pydantic

import apps


logger = logging.getLogger(__name__)


def _annotation_contains_float(annotation: Any) -> bool:
    """Verifica se uma anotação de tipo contém o tipo float primitivo."""
    if annotation is float or annotation == "float":
        return True
    origin = typing.get_origin(annotation)
    if origin is not None:
        args = typing.get_args(annotation)
        return any(_annotation_contains_float(arg) for arg in args)
    return False


def _is_monetary_field(field_name: str) -> bool:
    """
    Identifica se o nome de um campo representa um valor financeiro/monetário.

    Filtra termos financeiros e descarta exceções como porcentagens ou contagens.
    """
    name_lower = field_name.lower()

    if any(
        non_monetary in name_lower
        for non_monetary in [
            "percentage",
            "percent",
            "pct",
            "_count",
            "_days",
            "_number",
            "incomplete_tasks",
            "overdue_tasks",
        ]
    ):
        return False

    monetary_keywords = {
        "amount",
        "budget",
        "spent",
        "price",
        "cost",
        "fee",
        "balance",
        "allocated",
        "estimated",
        "actual",
    }
    return any(keyword in name_lower for keyword in monetary_keywords)


def _get_all_schema_classes() -> set[type[pydantic.BaseModel]]:
    """Descobre dinamicamente todas as classes de Schema do Ninja/Pydantic em apps."""
    schemas: set[type[pydantic.BaseModel]] = set()
    for _, modname, _ in pkgutil.walk_packages(apps.__path__, apps.__name__ + "."):
        if ".tests" in modname:
            continue
        try:
            mod = importlib.import_module(modname)
        except Exception as exc:
            logger.debug(f"Não foi possível importar {modname}: {exc}")
            continue
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            if (
                issubclass(obj, pydantic.BaseModel)
                and obj is not pydantic.BaseModel
                and obj.__module__.startswith("apps.")
                and ".tests" not in obj.__module__
            ):
                schemas.add(obj)
    return schemas


class TestSchemaIntegrity:
    """Suíte de testes para auditoria estática dos schemas da API."""

    def test_no_monetary_fields_use_float(self) -> None:
        """
        Teste CRÍTICO BR-VAL01: Nenhum campo monetário pode utilizar o tipo float.

        Inspeciona todas as classes que herdam de ninja.Schema ou pydantic.BaseModel
        nos módulos do projeto e verifica se algum campo monetário (ex: amount,
        budget, spent, price) utiliza float em vez de Decimal.
        """
        schemas = _get_all_schema_classes()
        assert len(schemas) > 0, "Nenhum schema Pydantic/Ninja foi encontrado."

        failures: list[str] = []

        for schema_cls in schemas:
            model_fields = getattr(schema_cls, "model_fields", {})
            for field_name, field_info in model_fields.items():
                if _is_monetary_field(field_name):
                    annotation = field_info.annotation
                    if _annotation_contains_float(annotation):
                        failures.append(
                            f"Schema '{schema_cls.__module__}.{schema_cls.__name__}' "
                            f"campo '{field_name}' está tipado como float "
                            f"({annotation}). Exigido Decimal (BR-VAL01)."
                        )

        assert not failures, (
            "Violacão BR-VAL01: campos monetários usando float:\n" + "\n".join(failures)
        )

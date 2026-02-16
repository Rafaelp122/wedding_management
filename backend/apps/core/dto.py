from dataclasses import dataclass, fields
from typing import Any, TypeVar


T = TypeVar("T", bound="BaseDTO")


@dataclass(frozen=True)
class BaseDTO:
    """
    Abstração base para Data Transfer Objects.
    Automatiza a criação de instâncias a partir de dicionários (validated_data).
    """

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """
        Instancia o DTO filtrando chaves que não pertencem à dataclass.
        Evita o erro 'TypeError: __init__() got an unexpected keyword argument'.
        """
        valid_field_names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid_field_names})

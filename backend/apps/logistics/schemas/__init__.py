"""Módulo de schemas para o domínio de logística."""

from apps.logistics.schemas.contract import (
    ContractFullCreateIn,
    ContractIn,
    ContractOut,
    ContractPatchIn,
    ContractStatusTransitionIn,
    ContractUploadIn,
    ContractUploadUrlIn,
    ContractUploadUrlOut,
)
from apps.logistics.schemas.item import (
    ItemIn,
    ItemOut,
    ItemPatchIn,
    ItemStatusTransitionIn,
)
from apps.logistics.schemas.supplier import (
    SupplierIn,
    SupplierOut,
    SupplierPatchIn,
)


__all__ = [
    "ContractFullCreateIn",
    "ContractIn",
    "ContractOut",
    "ContractPatchIn",
    "ContractStatusTransitionIn",
    "ContractUploadIn",
    "ContractUploadUrlIn",
    "ContractUploadUrlOut",
    "ItemIn",
    "ItemOut",
    "ItemPatchIn",
    "ItemStatusTransitionIn",
    "SupplierIn",
    "SupplierOut",
    "SupplierPatchIn",
]

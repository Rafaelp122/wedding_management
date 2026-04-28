from uuid import UUID

from django.http import HttpRequest

from apps.logistics.models import Contract, Item, Supplier


def get_supplier(request: HttpRequest, uuid: UUID) -> Supplier:
    """Injeta a instância de Supplier validada para o usuário logado."""
    return Supplier.objects.resolve(request.user, uuid)


def get_contract(request: HttpRequest, uuid: UUID) -> Contract:
    """Injeta a instância de Contract validada para o usuário logado."""
    return Contract.objects.resolve(request.user, uuid)


def get_item(request: HttpRequest, uuid: UUID) -> Item:
    """Injeta a instância de Item validada para o usuário logado."""
    return Item.objects.resolve(request.user, uuid)

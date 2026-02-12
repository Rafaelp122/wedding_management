from drf_spectacular.utils import extend_schema

from apps.core.viewsets import BaseViewSet

from .dto import ContractDTO, ItemDTO, SupplierDTO
from .models import Contract, Item, Supplier
from .serializers import ContractSerializer, ItemSerializer, SupplierSerializer
from .services import ContractService, ItemService, SupplierService


@extend_schema(tags=["Logistics - Suppliers"])
class SupplierViewSet(BaseViewSet):
    """
    Gestão de fornecedores (RF09).
    Permite o cadastro e controle de parceiros logísticos.
    """

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    service_class = SupplierService
    dto_class = SupplierDTO


@extend_schema(tags=["Logistics - Contracts"])
class ContractViewSet(BaseViewSet):
    """
    Gestão de contratos (RF10, RF13).
    Suporta upload de PDF e controle de status de assinatura.
    """

    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    service_class = ContractService
    dto_class = ContractDTO


@extend_schema(tags=["Logistics - Items"])
class ItemViewSet(BaseViewSet):
    """
    Itens de logística (RF07-RF08).
    Representa necessidades físicas vinculadas a contratos e orçamentos.
    """

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    service_class = ItemService
    dto_class = ItemDTO

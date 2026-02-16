from drf_spectacular.utils import extend_schema

from apps.core.viewsets import BaseViewSet

from .dto import ContractDTO, ItemDTO, SupplierDTO
from .models import Contract, Item, Supplier
from .serializers import ContractSerializer, ItemSerializer, SupplierSerializer
from .services import ContractService, ItemService, SupplierService


@extend_schema(tags=["Logistics - Suppliers"])
class SupplierViewSet(BaseViewSet):
    """
    Gestão de entidades fornecedoras (RF09).

    Orquestra o ciclo de vida dos fornecedores e garante o isolamento
    de dados por Planner através da infraestrutura de BaseViewSet.
    """

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    service_class = SupplierService
    dto_class = SupplierDTO


@extend_schema(tags=["Logistics - Contracts"])
class ContractViewSet(BaseViewSet):
    """
    Administração de contratos logísticos (RF10, RF13).

    Gerencia estados de assinatura, metadados financeiros e
    armazenamento de documentos digitais vinculados a fornecedores.
    """

    # Consolidação de busca via JOIN para otimizar a resolução de
    # dependências de Supplier e Wedding em operações de listagem.
    queryset = Contract.objects.select_related("supplier", "wedding").all()
    serializer_class = ContractSerializer
    service_class = ContractService
    dto_class = ContractDTO


@extend_schema(tags=["Logistics - Items"])
class ItemViewSet(BaseViewSet):
    """
    Gerenciamento de itens e insumos logísticos (RF07-RF08).

    Controla a alocação de recursos físicos e sua vinculação
    direta a contratos e categorias orçamentárias.
    """

    # Otimização de QuerySet via SQL JOIN para caminhos de relação
    # diretos e aninhados (Item -> Contract -> Supplier).
    queryset = Item.objects.select_related(
        "wedding", "budget_category", "contract", "contract__supplier"
    ).all()
    serializer_class = ItemSerializer
    service_class = ItemService
    dto_class = ItemDTO

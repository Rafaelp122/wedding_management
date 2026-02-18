from django.db import transaction

from apps.logistics.dto import ContractDTO
from apps.logistics.models import Contract, Supplier
from apps.weddings.models import Wedding


class ContractService:
    """
    Camada de serviço para gestão de contratos.
    Garante a integridade entre fornecedores, casamentos e arquivos (ADR-010).
    """

    @staticmethod
    @transaction.atomic
    def create(dto: ContractDTO) -> Contract:
        """
        Cria um contrato garantindo que o fornecedor e o casamento pertencem ao mesmo
        Planner.
        """
        # 1. Busca instâncias pai para garantir o contexto e segurança
        # (Herança de Contexto)
        supplier = Supplier.objects.get(uuid=dto.supplier_id, planner_id=dto.planner_id)
        wedding = Wedding.objects.get(uuid=dto.wedding_id, planner_id=dto.planner_id)

        data = dto.model_dump()

        # 2. Limpeza de IDs para evitar conflitos de argumentos no .create()
        data.pop("supplier_id")
        data.pop("wedding_id")
        data.pop("planner_id")

        # 3. Criação com injeção de instâncias validadas
        return Contract.objects.create(
            planner=wedding.planner, wedding=wedding, supplier=supplier, **data
        )

    @staticmethod
    @transaction.atomic
    def update(instance: Contract, dto: ContractDTO) -> Contract:
        """
        Atualiza o contrato protegendo campos imutáveis e gerenciando arquivos.
        """
        # Bloqueamos a troca de Casamento ou Dono via atualização
        exclude_fields = {"planner_id", "wedding_id", "supplier_id"}
        data = dto.model_dump(exclude=exclude_fields)

        # Se houver troca de fornecedor, validamos se ele pertence ao mesmo Planner
        if str(dto.supplier_id) != str(instance.supplier_id):
            instance.supplier = Supplier.objects.get(
                uuid=dto.supplier_id, planner_id=instance.planner_id
            )

        # Atualização dinâmica de campos
        for field, value in data.items():
            # Preserva o PDF atual se nenhum novo arquivo for enviado
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)

        instance.save()  # Dispara full_clean() conforme ADR-010
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Contract) -> None:
        """
        Executa a deleção lógica e limpa referências em itens vinculados.
        """
        # Conforme ADR-008, fazemos o cascade manual:
        # Desvinculamos o contrato dos itens de logística antes de 'deletar'
        instance.items.update(contract=None)

        instance.delete()

from django.db import transaction

from apps.logistics.dto import ContractDTO
from apps.logistics.models import Contract


class ContractService:
    @staticmethod
    @transaction.atomic
    def create(dto: ContractDTO) -> Contract:
        """Cria um contrato e garante a persistência das regras do Model.clean()."""
        contract = Contract.objects.create(
            wedding_id=dto.wedding_id,
            supplier_id=dto.supplier_id,
            total_amount=dto.total_amount,
            description=dto.description,
            status=dto.status,
            expiration_date=dto.expiration_date,
            alert_days_before=dto.alert_days_before,
            signed_date=dto.signed_date,
            pdf_file=dto.pdf_file,
        )
        return contract

    @staticmethod
    @transaction.atomic
    def update(instance: Contract, dto: ContractDTO) -> Contract:
        """Atualiza o contrato. O método save() disparará o clean() do modelo."""
        instance.supplier_id = dto.supplier_id
        instance.total_amount = dto.total_amount
        instance.description = dto.description
        instance.status = dto.status
        instance.expiration_date = dto.expiration_date
        instance.alert_days_before = dto.alert_days_before
        instance.signed_date = dto.signed_date

        if dto.pdf_file:
            instance.pdf_file = dto.pdf_file

        instance.save()  # Dispara full_clean() conforme definido no seu Model
        return instance

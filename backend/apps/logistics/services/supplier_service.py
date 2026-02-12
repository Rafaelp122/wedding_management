from django.db import transaction

from apps.logistics.dto import SupplierDTO
from apps.logistics.models import Supplier


class SupplierService:
    @staticmethod
    @transaction.atomic
    def create(dto: SupplierDTO) -> Supplier:
        return Supplier.objects.create(
            planner_id=dto.planner_id,
            name=dto.name,
            category=dto.category,
            contact_name=dto.contact_name,
            phone=dto.phone,
            email=dto.email,
            is_active=dto.is_active,
        )

    @staticmethod
    @transaction.atomic
    def update(instance: Supplier, dto: SupplierDTO) -> Supplier:
        for key, value in dto.__dict__.items():
            if key != "planner_id":  # Não mudamos o dono
                setattr(instance, key, value)
        instance.save()
        return instance

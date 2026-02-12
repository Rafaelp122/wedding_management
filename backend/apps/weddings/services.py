from django.db import transaction

from .dto import WeddingCreateDTO
from .models import Wedding


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.
    Implementa a orquestração entre DTO e Model.
    """

    @staticmethod
    @transaction.atomic
    def create(dto: WeddingCreateDTO) -> Wedding:
        """
        Cria um novo casamento a partir de um DTO.
        O uso de atomic garante que, se algo falhar, nada será salvo.
        """
        # Aqui pode disparar outras ações, como:
        # 1. Criar categorias de gastos padrão no app de Finances
        # 2. Enviar um e-mail de boas-vindas ao Planner

        wedding = Wedding.objects.create(
            planner_id=dto.planner_id,
            groom_name=dto.groom_name,
            bride_name=dto.bride_name,
            date=dto.date,
            location=dto.location,
            expected_guests=dto.expected_guests,
            status=dto.status,
        )
        return wedding

    @staticmethod
    @transaction.atomic
    def update(instance: Wedding, dto: WeddingCreateDTO) -> Wedding:
        """
        Atualiza um casamento existente.
        """
        instance.groom_name = dto.groom_name
        instance.bride_name = dto.bride_name
        instance.date = dto.date
        instance.location = dto.location
        instance.expected_guests = dto.expected_guests
        instance.status = dto.status

        # O método .save() do model executará o seu .clean() (ADR-010)
        instance.save()
        return instance

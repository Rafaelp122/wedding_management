from django.db import transaction

from .dto import WeddingDTO
from .models import Wedding


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.
    Implementa a orquestração entre DTO e Model.
    """

    @staticmethod
    @transaction.atomic
    def create(dto: WeddingDTO) -> Wedding:
        """
        Cria um novo casamento a partir de um DTO.
        O uso de atomic garante que, se algo falhar, nada será salvo.
        """
        # Aqui pode disparar outras ações, como:
        # 1. Criar categorias de gastos padrão no app de Finances
        # 2. Enviar um e-mail de boas-vindas ao Planner

        # O model_dump() retorna um dicionário pronto para o create do Django.
        # planner_id no DTO mapeia corretamente para o campo planner no model via
        # Django.
        return Wedding.objects.create(**dto.model_dump())

    @staticmethod
    @transaction.atomic
    def update(instance: Wedding, dto: WeddingDTO) -> Wedding:
        """
        Atualiza um casamento existente.
        """
        # Atualiza os campos dinamicamente, excluindo o planner_id que é imutável
        for field, value in dto.model_dump(exclude={"planner_id"}).items():
            setattr(instance, field, value)

        # O método .save() do model executará o seu .clean() (ADR-010)
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Wedding) -> None:
        """
        Executa a deleção lógica do casamento e seus dependentes.

        Como o cascade não é automático (ADR-008), este é o local para
        deletar convidados, tarefas e orçamentos vinculados antes
        de 'remover' o casamento.
        """
        # Exemplo de cascade manual:
        # instance.guest_records.all().delete()
        # instance.task_records.all().delete()

        instance.delete()

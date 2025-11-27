from django.db import models
from django.db.models import Case, Value, When

from .constants import (
    EDITABLE_STATUSES,
    STATUS_CANCELED,
    STATUS_COMPLETED,
    STATUS_WAITING_COUPLE,
    STATUS_WAITING_PLANNER,
    STATUS_WAITING_SUPPLIER,
)


class ContractQuerySet(models.QuerySet):
    """
    QuerySet customizado para o modelo Contract.
    Fornece métodos de filtragem e otimização específicos para contratos.
    """

    def for_planner(self, planner) -> "ContractQuerySet":
        """
        Filtra contratos pertencentes a um cerimonialista específico.
        
        Args:
            planner: Instância do usuário cerimonialista.
            
        Returns:
            QuerySet filtrado por planner.
        """
        return self.filter(item__wedding__planner=planner)

    def for_wedding(self, wedding) -> "ContractQuerySet":
        """
        Filtra contratos de um casamento específico.
        
        Args:
            wedding: Instância do modelo Wedding.
            
        Returns:
            QuerySet filtrado por wedding.
        """
        return self.filter(item__wedding=wedding)

    def with_related(self) -> "ContractQuerySet":
        """
        Otimiza queries incluindo relacionamentos necessários.
        Previne N+1 queries ao buscar contratos com seus relacionamentos.
        
        Returns:
            QuerySet com select_related aplicado.
        """
        return self.select_related(
            "item",
            "item__wedding",
            "item__wedding__planner"
        )

    def fully_signed(self) -> "ContractQuerySet":
        """
        Filtra apenas contratos com todas as assinaturas completas.
        
        Returns:
            QuerySet com contratos totalmente assinados.
        """
        return self.filter(
            status=STATUS_COMPLETED,
            planner_signature__isnull=False,
            supplier_signature__isnull=False,
            couple_signature__isnull=False
        )

    def with_signature_status(self) -> "ContractQuerySet":
        """
        Anota o queryset com informações sobre o status das assinaturas.
        
        Returns:
            QuerySet anotado com campos booleanos de assinaturas.
        """
        return self.annotate(
            has_planner_signature=Case(
                When(planner_signature__isnull=False, then=Value(True)),
                default=Value(False),
            ),
            has_supplier_signature=Case(
                When(supplier_signature__isnull=False, then=Value(True)),
                default=Value(False),
            ),
            has_couple_signature=Case(
                When(couple_signature__isnull=False, then=Value(True)),
                default=Value(False),
            ),
        )

    def editable(self) -> "ContractQuerySet":
        """
        Filtra contratos que ainda podem ser editados.
        Apenas contratos em DRAFT ou WAITING_PLANNER são editáveis.
        
        Returns:
            QuerySet com contratos editáveis.
        """
        return self.filter(status__in=EDITABLE_STATUSES)

    def cancelable(self) -> "ContractQuerySet":
        """
        Filtra contratos que podem ser cancelados.
        Contratos COMPLETED não podem ser cancelados.
        
        Returns:
            QuerySet com contratos canceláveis.
        """
        return self.exclude(status=STATUS_COMPLETED)

    def bulk_cancel(self) -> int:
        """
        Cancela múltiplos contratos de uma vez.
        Apenas contratos que não estão completos serão cancelados.
        
        Returns:
            Número de contratos cancelados.
        """
        return self.cancelable().update(status=STATUS_CANCELED)

    def bulk_update_description(self, description: str) -> int:
        """
        Atualiza a descrição de múltiplos contratos editáveis.
        
        Args:
            description: Nova descrição para os contratos.
            
        Returns:
            Número de contratos atualizados.
        """
        return self.editable().update(description=description)

    def get_next_signer_name(self, contract_id: int) -> dict:
        """
        Retorna informações sobre o próximo assinante de um contrato.
        Otimizado com select_related para evitar queries extras.
        
        Args:
            contract_id: ID do contrato.
            
        Returns:
            Dicionário com role e name do próximo signatário.
        """
        try:
            contract = self.select_related(
                'item__wedding'
            ).get(id=contract_id)

            if contract.status == STATUS_WAITING_PLANNER:
                return {
                    'role': 'Cerimonialista',
                    'name': 'Você (Cerimonialista)'
                }

            elif contract.status == STATUS_WAITING_SUPPLIER:
                supplier_name = contract.item.supplier or "Não vinculado"
                return {
                    'role': 'Fornecedor',
                    'name': f"Fornecedor ({supplier_name})"
                }

            elif contract.status == STATUS_WAITING_COUPLE:
                if contract.item.wedding:
                    bride = contract.item.wedding.bride_name
                    groom = contract.item.wedding.groom_name
                    return {
                        'role': 'Noivos',
                        'name': f"Noivos ({bride} e {groom})"
                    }
                return {'role': 'Noivos', 'name': 'Noivos'}

            return {'role': 'Desconhecido', 'name': 'Alguém'}

        except self.model.DoesNotExist:
            return {'role': 'Erro', 'name': 'Contrato não encontrado'}


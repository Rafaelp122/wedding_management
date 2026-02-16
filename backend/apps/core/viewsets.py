from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError

from .mixins import PlannerOwnedMixin, WeddingOwnedMixin


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="include_deleted",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Se verdadeiro, inclui registros marcados como "
                "removidos (Soft Delete).",
                default=False,
            )
        ]
    )
)
class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base para padronização de comportamentos do sistema.

    Funcionalidades:
    1. Lookup por UUID (Segurança RNF05).
    2. Multitenancy automático via herança de Mixins (ADR-009).
    3. Suporte a Soft Delete (ADR-008).
    4. Orquestração flexível via Service Layer e DTO (ADR-006).
    """

    lookup_field = "uuid"
    service_class = None
    dto_class = None

    def get_queryset(self):
        """
        Retorna o QuerySet filtrado por regras de multitenancy e visibilidade.
        """
        user = self.request.user
        queryset = super().get_queryset()
        model = queryset.model

        if issubclass(model, WeddingOwnedMixin):
            queryset = queryset.filter(wedding__planner=user)
        elif issubclass(model, PlannerOwnedMixin):
            queryset = queryset.filter(planner=user)

        include_deleted = self.request.query_params.get("include_deleted") == "true"
        if include_deleted and hasattr(model, "all_objects"):
            queryset = model.all_objects.filter(
                id__in=queryset.values_list("id", flat=True)
            )

        return queryset

    def perform_create(self, serializer):
        """
        Criação híbrida: Service.create -> Serializer.save.
        """
        # Checa se o trio Service + DTO + Método está completo
        if (
            self.service_class
            and self.dto_class
            and hasattr(self.service_class, "create")
        ):
            try:
                dto = self.dto_class.from_validated_data(
                    user_id=self.request.user.id,
                    validated_data=serializer.validated_data,
                )
                self.instance = self.service_class.create(dto)
            except DjangoValidationError as e:
                raise DRFValidationError(e.message_dict) from e
        else:
            # Fallback para o comportamento padrão do DRF
            serializer.save()

    def perform_update(self, serializer):
        """
        Atualização híbrida: Service.update -> Serializer.save.
        """
        if (
            self.service_class
            and self.dto_class
            and hasattr(self.service_class, "update")
        ):
            try:
                dto = self.dto_class.from_validated_data(
                    user_id=self.request.user.id,
                    validated_data=serializer.validated_data,
                )
                self.instance = self.service_class.update(
                    instance=self.get_object(), dto=dto
                )
            except DjangoValidationError as e:
                raise DRFValidationError(e.message_dict) from e
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """
        Exclusão híbrida: Service.delete -> Model.delete.
        """
        # Verifica se o service tem um método de delete customizado
        if self.service_class and hasattr(self.service_class, "delete"):
            self.service_class.delete(instance)
        else:
            # Fallback para o delete do model (Soft Delete padrão)
            instance.delete()

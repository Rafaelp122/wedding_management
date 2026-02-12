from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="include_deleted",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Se verdadeiro, inclui registros marcados "
                "como removidos (Soft Delete).",
                default=False,
            )
        ]
    )
)
class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base para o Wedding Management System.

    Padroniza:
    1. Lookup por UUID (ADR-007).
    2. Multitenancy automático via Planner (ADR-009).
    3. Suporte a Soft Delete (?include_deleted=true) (ADR-008).
    4. Orquestração via Service Layer e DTO (ADR-006).
    """

    lookup_field = "uuid"
    service_class = None
    dto_class = None

    def get_queryset(self):
        """Aplica filtros de segurança de Multitenancy e Soft Delete."""
        user = self.request.user
        model = self.queryset.model

        # 1. Filtro de Multitenancy (Segurança por Design)
        if hasattr(model, "wedding"):
            queryset = model.objects.filter(wedding__planner=user)
        elif hasattr(model, "planner"):
            queryset = model.objects.filter(planner=user)
        else:
            queryset = super().get_queryset()

        # 2. Filtro de Soft Delete
        include_deleted = self.request.query_params.get("include_deleted") == "true"
        if include_deleted and hasattr(model, "all_objects"):
            queryset = model.all_objects.filter(
                id__in=queryset.values_list("id", flat=True)
            )

        return queryset

    def perform_create(self, serializer):
        """Converte dados para DTO e delega ao Service."""
        if self.service_class and self.dto_class:
            try:
                dto = self.dto_class.from_validated_data(
                    user_id=self.request.user.id,
                    validated_data=serializer.validated_data,
                )
                self.instance = self.service_class.create(dto)
            except DjangoValidationError as e:
                raise DRFValidationError(e.message_dict) from e
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Delega a atualização ao Service com suporte a DTO."""
        if self.service_class and self.dto_class:
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

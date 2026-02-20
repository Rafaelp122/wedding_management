from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError


class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base híbrida e multitenant.

    1. Isolamento: Filtra automaticamente por Planner via Manager.
    2. Híbrida: Usa ServiceLayer se definida, caso contrário segue o padrão DRF.
    """

    lookup_field = "uuid"
    service_class = None

    def get_queryset(self):
        """
        Garante isolamento de dados (Multitenancy) via Manager.
        """
        if self.queryset is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} precisa de um 'queryset' definido."
            )

        # O Manager (BaseManager) resolve o isolamento para o usuário autenticado.
        user = self.request.user
        return self.queryset.model.objects.all().for_user(user)

    def perform_create(self, serializer):
        """
        Criação híbrida: Service.create ou Serializer.save.
        """
        if self.service_class and hasattr(self.service_class, "create"):
            try:
                # O Service é responsável pela persistência e retorno da instância.
                instance = self.service_class.create(
                    user=self.request.user, data=serializer.validated_data
                )
                serializer.instance = instance
            except DjangoValidationError as e:
                raise DRFValidationError(e.message_dict) from e
        else:
            serializer.save()

    def perform_update(self, serializer):
        """
        Atualização híbrida: Service.update ou Serializer.save.
        """
        if self.service_class and hasattr(self.service_class, "update"):
            try:
                instance = self.service_class.update(
                    instance=self.get_object(),
                    user=self.request.user,
                    data=serializer.validated_data,
                )
                serializer.instance = instance
            except DjangoValidationError as e:
                raise DRFValidationError(e.message_dict) from e
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """
        Deleção híbrida: Service.delete ou fallback para Hard Delete.
        """
        if self.service_class and hasattr(self.service_class, "delete"):
            self.service_class.delete(user=self.request.user, instance=instance)
        else:
            instance.delete()

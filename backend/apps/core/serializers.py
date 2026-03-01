from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Serializer base para todos os models do sistema.
    """

    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        fields = ["uuid", "created_at", "updated_at"]
        read_only_fields = ["uuid", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pega o request do contexto do serializer
        request = self.context.get("request")

        # Se houver request e usuário instanciado
        if request and hasattr(request, "user"):
            user = request.user

            # Percorre todos os campos deste serializer
            for field_name, field_obj in self.fields.items():
                # Se for um campo de relacionamento (tem queryset)
                if hasattr(field_obj, "queryset") and field_obj.queryset is not None:
                    # Aplica o nosso filtro de multitenancy automaticamente!
                    if hasattr(field_obj.queryset, "for_user"):
                        field_obj.queryset = field_obj.queryset.for_user(user)

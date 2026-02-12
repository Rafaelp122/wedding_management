from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Serializer base para todos os models do sistema.

    Seguindo o ADR-007:
    - Expõe o 'uuid' como identificador público.
    - Oculta o 'id' sequencial (BigInt) por segurança.
    - Inclui timestamps automáticos como leitura.
    """

    # Explicitamos o uuid para garantir que ele seja sempre read_only
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        # Campos comuns a todos os modelos que herdam de BaseModel
        fields = ["uuid", "created_at", "updated_at"]
        read_only_fields = ["uuid", "created_at", "updated_at"]

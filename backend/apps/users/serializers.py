# apps/users/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserDataSerializer(serializers.Serializer):
    """Estrutura dos dados do usuário retornados no login."""

    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    # DECLARAÇÃO EXPLÍCITA PARA O SWAGGER ENXERGAR:
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserDataSerializer(read_only=True)

    def validate(self, attrs):
        # O super().validate(attrs) gera os tokens no dicionário 'data'
        data = super().validate(attrs)

        # Injeta os dados do usuário
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }

        return data

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer JWT customizado para usar email ao invés de username.
    """

    username_field = "email"

    def validate(self, attrs):
        # O campo vem como 'email' mas o SimpleJWT espera 'username' internamente
        # Então fazemos o mapeamento aqui
        data = super().validate(attrs)

        # Adiciona informações extras ao token se necessário
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }

        return data

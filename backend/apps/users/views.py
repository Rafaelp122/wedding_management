from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.views import TokenViewBase

from apps.users.serializers import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenViewBase):
    """View JWT customizada para usar email."""

    # Bloqueia a entrada de lixo (apenas JSON)
    parser_classes = [JSONParser]
    serializer_class = EmailTokenObtainPairSerializer

    @extend_schema(
        tags=["auth"],
        summary="Obter Par de Tokens",
        description="Autentica o utilizador via email e devolve os tokens Access e "
        "Refresh.",
        responses={
            200: OpenApiResponse(description="Login com sucesso. Tokens gerados."),
            400: OpenApiResponse(
                description="Erro de validação. Estrutura JSON incorreta."
            ),
            401: OpenApiResponse(description="Não autorizado. Credenciais inválidas."),
        },
    )
    def post(self, request, *args, **kwargs):
        # Sobrescrevemos o método apenas para ancorar o decorator do Swagger
        return super().post(request, *args, **kwargs)

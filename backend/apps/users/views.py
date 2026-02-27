# apps/users/views.py
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.views import TokenViewBase

from apps.users.serializers import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenViewBase):
    """
    Gerenciamento de autenticação via JWT com e-mail.
    """

    parser_classes = [JSONParser]
    serializer_class = EmailTokenObtainPairSerializer

    @extend_schema(
        tags=["auth"],
        summary="Obter Par de Tokens",
        description="Recebe as credenciais (e-mail/senha) e retorna um par de tokens "
        "JWT (Access e Refresh).",
        responses={
            # Ao passar o serializer aqui, o Swagger gera o schema
            # 'AuthTokenCreate200Response' com os campos 'access' e 'refresh'.
            # Sem isso, o Orval assume 'void'.
            200: EmailTokenObtainPairSerializer,
            400: OpenApiResponse(
                description="Requisição inválida. Verifique o formato do JSON."
            ),
            401: OpenApiResponse(
                description="Credenciais inválidas ou conta desativada."
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        # Sobrescrevemos o método apenas para ancorar o decorator do Swagger
        return super().post(request, *args, **kwargs)

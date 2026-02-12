from rest_framework_simplejwt.views import TokenViewBase

from apps.users.serializers import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenViewBase):
    """View JWT customizada para usar email."""

    serializer_class = EmailTokenObtainPairSerializer

import pytest
from django.urls import reverse
from rest_framework import status

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingViewSet:
    def test_list_weddings_isolation(self, api_client, user):
        """
        Garante que o Planner só veja os SEUS casamentos na listagem.
        """
        # Setup: Casamento do usuário logado e de outro planner
        WeddingFactory(planner=user, bride_name="Noiva do User")
        WeddingFactory(bride_name="Noiva Alheia")  # Planner diferente via factory

        url = reverse("wedding-list")  # Verifique o basename no seu urls.py
        api_client.force_authenticate(user=user)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["bride_name"] == "Noiva do User"

    def test_retrieve_wedding_forbidden_for_other_planner(self, api_client, user):
        """
        Garante que acessar o detalhe de um casamento de outro planner retorne 404.
        Retornamos 404 em vez de 403 para não confirmar a existência do ID (Segurança).
        """
        other_wedding = WeddingFactory(bride_name="Noiva Secreta")

        url = reverse("wedding-detail", kwargs={"uuid": other_wedding.uuid})
        api_client.force_authenticate(user=user)

        response = api_client.get(url)

        # O Manager .for_user(user) deve fazer o DRF lançar 404
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_wedding_via_api_success(self, api_client, user):
        """
        Garante que o POST na API aciona o WeddingService e cria o ecossistema.
        """
        url = reverse("wedding-list")
        payload = {
            "groom_name": "Rafael",
            "bride_name": "Noiva de Teste",
            "date": "2026-12-31",
            "location": "Espaço Alvorada",
            "expected_guests": 150,
            "total_estimated": "50000.00",
        }

        api_client.force_authenticate(user=user)
        response = api_client.post(url, data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        # Verifica se o Service foi chamado (pela presença do UUID e Budget)
        assert "uuid" in response.data
        assert Wedding.objects.filter(planner=user).count() == 1

    def test_unauthenticated_access_denied(self, api_client):
        """
        Garante que ninguém acessa nada sem estar logado.
        """
        url = reverse("wedding-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

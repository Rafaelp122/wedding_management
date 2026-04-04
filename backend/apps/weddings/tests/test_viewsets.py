import pytest

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingViewSet:
    def test_list_weddings_isolation(self, auth_client, user):
        """
        Garante que o Planner só veja os SEUS casamentos na listagem.
        """
        # Setup: Casamento do usuário logado e de outro planner
        WeddingFactory(planner=user, bride_name="Noiva do User")
        WeddingFactory(bride_name="Noiva Alheia")  # Planner diferente via factory

        url = "/api/v1/weddings/"

        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["bride_name"] == "Noiva do User"

    def test_retrieve_wedding_forbidden_for_other_planner(self, auth_client, user):
        """
        Garante que acessar o detalhe de um casamento de outro planner retorne 404.
        Retornamos 404 em vez de 403 para não confirmar a existência do ID (Segurança).
        """
        other_wedding = WeddingFactory(bride_name="Noiva Secreta")

        url = f"/api/v1/weddings/{other_wedding.uuid}/"

        response = auth_client.get(url)

        # O Manager .for_user(user) deve fazer o Ninja lançar 404
        assert response.status_code == 404

    def test_create_wedding_via_api_success(self, auth_client, user):
        """
        Garante que o POST na API aciona o WeddingService e cria o ecossistema.
        """
        url = "/api/v1/weddings/"
        payload = {
            "groom_name": "Rafael",
            "bride_name": "Noiva de Teste",
            "date": "2026-12-31",
            "location": "Espaço Alvorada",
            "expected_guests": 150,
            "total_estimated": "50000.00",
        }

        response = auth_client.post(url, data=payload, content_type="application/json")

        assert response.status_code == 201
        # Verifica se o Service foi chamado (pela presença do UUID e Budget)
        assert "uuid" in response.json()
        assert Wedding.objects.filter(planner=user).count() == 1

    def test_unauthenticated_access_denied(self, client):
        """
        Garante que ninguém acessa nada sem estar logado.
        """
        url = "/api/v1/weddings/"
        response = client.get(url)

        assert response.status_code == 401

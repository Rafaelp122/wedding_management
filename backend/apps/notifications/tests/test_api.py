from uuid import uuid4

import pytest

from apps.notifications.tests.factories import NotificationFactory
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestNotificationsAPI:
    """Testes de integração para a API de Notificações In-App."""

    def test_list_notifications_unauthorized(self, client):
        response = client.get("/api/v1/notifications/")
        assert response.status_code == 401

    def test_list_notifications_success(self, auth_client, user):
        target_uuid = uuid4()
        wedding_uuid = uuid4()
        n1 = NotificationFactory(
            user=user,
            is_read=False,
            target_type="installment",
            target_id=target_uuid,
            wedding_id=wedding_uuid,
        )
        n2 = NotificationFactory(user=user, is_read=True)

        other_user = UserFactory()
        NotificationFactory(user=other_user)

        response = auth_client.get("/api/v1/notifications/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        uuids = {item["uuid"] for item in data}
        assert str(n1.uuid) in uuids
        assert str(n2.uuid) in uuids

        n1_data = next(item for item in data if item["uuid"] == str(n1.uuid))
        assert n1_data["target_type"] == "installment"
        assert n1_data["target_id"] == str(target_uuid)
        assert n1_data["wedding_id"] == str(wedding_uuid)

    def test_list_notifications_filter_by_is_read(self, auth_client, user):
        n1 = NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        response = auth_client.get("/api/v1/notifications/?is_read=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["uuid"] == str(n1.uuid)

    def test_get_unread_count_success(self, auth_client, user):
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        response = auth_client.get("/api/v1/notifications/unread-count/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    def test_mark_as_read_success(self, auth_client, user):
        notification = NotificationFactory(user=user, is_read=False)

        response = auth_client.patch(f"/api/v1/notifications/{notification.uuid}/read/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_read"] is True
        assert data["read_at"] is not None

    def test_mark_as_read_not_found(self, auth_client):
        response = auth_client.patch(f"/api/v1/notifications/{uuid4()}/read/")
        assert response.status_code == 404

    def test_mark_as_read_other_user_notification(self, auth_client, user):
        other_user = UserFactory()
        other_note = NotificationFactory(user=other_user)

        response = auth_client.patch(f"/api/v1/notifications/{other_note.uuid}/read/")
        assert response.status_code == 404

    def test_mark_all_as_read_success(self, auth_client, user):
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        response = auth_client.post("/api/v1/notifications/read-all/")
        assert response.status_code == 200
        data = response.json()
        assert data["marked_count"] == 2

        count_response = auth_client.get("/api/v1/notifications/unread-count/")
        assert count_response.json()["count"] == 0

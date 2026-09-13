"""Testes unitários para os schemas Pydantic/Ninja do domínio de notificações."""

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from apps.notifications.schemas import (
    BulkNotificationIdsIn,
    BulkOperationOut,
    MarkAllReadOut,
    NotificationOut,
    UnreadCountOut,
)


class Dummy:
    """Objeto simples para simular instâncias de modelos em testes unitários puros."""

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


class TestNotificationSchemas:
    """Testes de validação para schemas de Notificação."""

    def test_bulk_notification_ids_in_valid(self) -> None:
        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        schema = BulkNotificationIdsIn(notification_ids=[id1, id2])
        assert schema.notification_ids == [id1, id2]

    def test_bulk_notification_ids_in_rejects_empty_list(self) -> None:
        with pytest.raises(ValidationError):
            BulkNotificationIdsIn(notification_ids=[])

    def test_bulk_notification_ids_in_rejects_invalid_uuid(self) -> None:
        with pytest.raises(ValidationError):
            BulkNotificationIdsIn(notification_ids=["not-a-valid-uuid"])  # type: ignore[list-item]

    def test_bulk_operation_out(self) -> None:
        schema = BulkOperationOut(affected_count=5)
        assert schema.affected_count == 5

    def test_unread_count_out(self) -> None:
        schema = UnreadCountOut(count=12)
        assert schema.count == 12

    def test_mark_all_read_out(self) -> None:
        schema = MarkAllReadOut(marked_count=8)
        assert schema.marked_count == 8

    def test_notification_out_serialization_pure(self) -> None:
        notif_uuid = uuid.uuid4()
        target_uuid = uuid.uuid4()
        wedding_uuid = uuid.uuid4()
        now = datetime.now(UTC)

        mock_notif = Dummy(
            uuid=notif_uuid,
            title="Lembrete de Pagamento",
            message="Parcela 1 vence amanhã",
            type="PAYMENT_REMINDER",
            target_type="EXPENSE",
            target_id=target_uuid,
            wedding_id=wedding_uuid,
            wedding_name="Casamento Ana & Pedro",
            is_read=False,
            link="/finances/expenses",
            read_at=None,
            created_at=now,
        )

        out = NotificationOut.from_orm(mock_notif)
        assert out.uuid == notif_uuid
        assert out.title == "Lembrete de Pagamento"
        assert out.message == "Parcela 1 vence amanhã"
        assert out.type == "PAYMENT_REMINDER"
        assert out.target_type == "EXPENSE"
        assert out.target_id == target_uuid
        assert out.wedding_id == wedding_uuid
        assert out.wedding_name == "Casamento Ana & Pedro"
        assert out.is_read is False
        assert out.link == "/finances/expenses"
        assert out.read_at is None
        assert out.created_at == now

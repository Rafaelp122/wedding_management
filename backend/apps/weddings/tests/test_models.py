from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestWeddingModelMetadata:
    """
    Testes de representação e metadados do modelo Wedding.
    """

    def test_wedding_str_representation(self):
        """RF: O método __str__ deve retornar 'Groom & Bride'."""
        wedding = Wedding(groom_name="Diogo", bride_name="Laura")
        assert str(wedding) == "Diogo & Laura"

    def test_wedding_ordering_by_date_descending(self, user):
        """RF: A ordenação padrão deve ser pela data mais futura primeiro (-date)."""
        today = date.today()
        w_future = WeddingFactory(planner=user, date=today + timedelta(days=60))
        w_mid = WeddingFactory(planner=user, date=today + timedelta(days=30))
        w_soon = WeddingFactory(planner=user, date=today + timedelta(days=5))

        queryset = list(Wedding.objects.all())

        assert queryset == [w_future, w_mid, w_soon]


@pytest.mark.django_db
@pytest.mark.unit
class TestWeddingModelIntegrity:
    """
    Testes de limites físicos e integridade de dados do Model.
    """

    def test_bride_name_max_length(self, user):
        """Garante que nomes com mais de 100 caracteres falham na validação."""
        long_name = "A" * 101
        wedding = WeddingFactory.build(planner=user, bride_name=long_name)

        with pytest.raises(ValidationError) as exc:
            wedding.full_clean()
        assert "bride_name" in exc.value.message_dict

    def test_groom_name_max_length(self, user):
        """Garante que nomes com mais de 100 caracteres falham na validação."""
        long_name = "B" * 101
        wedding = WeddingFactory.build(planner=user, groom_name=long_name)

        with pytest.raises(ValidationError) as exc:
            wedding.full_clean()
        assert "groom_name" in exc.value.message_dict

    def test_expected_guests_cannot_be_negative(self, user):
        """Garante que o campo PositiveIntegerField rejeita negativos."""
        wedding = WeddingFactory.build(planner=user, expected_guests=-1)

        with pytest.raises(ValidationError):
            wedding.full_clean()


@pytest.mark.django_db
@pytest.mark.unit
class TestWeddingDateValidator:
    """
    Testes específicos para o validador de data.
    """

    def test_wedding_date_future_passes(self, user):
        """Garante que data no futuro passa."""
        future_date = timezone.now().date() + timedelta(days=30)
        wedding = WeddingFactory.build(planner=user, date=future_date)
        wedding.full_clean()

    def test_wedding_date_past_fails(self, user):
        """Garante que datas passadas disparam ValidationError."""
        yesterday = timezone.now().date() - timedelta(days=1)
        wedding = WeddingFactory.build(planner=user, date=yesterday)

        with pytest.raises(ValidationError) as exc:
            wedding.full_clean()
        assert "date" in exc.value.message_dict


@pytest.mark.django_db
@pytest.mark.unit
class TestWeddingBusinessRules:
    """
    Testes para as regras de negócio puramente locais do Modelo.
    """

    def test_status_completed_invalid_future_date(self, user):
        """Garante que NÃO se pode concluir um casamento que ainda não aconteceu."""
        future_date = timezone.now().date() + timedelta(days=365)
        wedding = WeddingFactory.build(
            planner=user, date=future_date, status=Wedding.StatusChoices.COMPLETED
        )

        with pytest.raises(ValidationError) as exc:
            wedding.clean()
        assert "Não pode marcar como CONCLUÍDO antes da data do casamento" in str(
            exc.value
        )

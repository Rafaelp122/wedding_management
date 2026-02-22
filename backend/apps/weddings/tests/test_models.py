from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingModelMetadata:
    """
    Testes de representação e metadados do modelo Wedding.
    """

    def test_wedding_str_representation(self):
        """
        RF: O método __str__ deve retornar 'Groom & Bride'.
        """
        # 1. Setup com nomes fixos
        wedding = WeddingFactory(groom_name="Rafael", bride_name="Beatriz")

        # 2. Asserção do método mágico __str__
        assert str(wedding) == "Rafael & Beatriz"

    def test_wedding_ordering_by_date_descending(self):
        """
        RF: A ordenação padrão deve ser pela data mais futura primeiro (-date).
        """
        # 1. Setup: Criar casamentos em datas diferentes
        today = date.today()

        # Casamento mais distante (deve ser o 1º da lista)
        w_future = WeddingFactory(date=today + timedelta(days=60))

        # Casamento intermediário (deve ser o 2º)
        w_mid = WeddingFactory(date=today + timedelta(days=30))

        # Casamento mais próximo (deve ser o 3º)
        w_soon = WeddingFactory(date=today + timedelta(days=5))

        # 2. Execução: Buscar todos
        # Como definimos ordering = ["-date"] no Meta, o Django já deve sortear
        queryset = list(Wedding.objects.all())

        # 3. Asserção da ordem lógica
        assert queryset == [w_future, w_mid, w_soon]

        # Verificação matemática da ordem: date_i >= date_{i+1}
        for i in range(len(queryset) - 1):
            assert queryset[i].date >= queryset[i + 1].date


@pytest.mark.django_db
class TestWeddingDateValidator:
    """
    Testes específicos para o validador de data.
    Usamos .build() + .full_clean() para isolar o validador do banco de dados.
    """

    def test_wedding_date_future_passes(self, user):
        """Garante que data no futuro passa."""
        future_date = timezone.now().date() + timedelta(days=30)
        # Passamos o planner=user para evitar o erro de 'campo nulo'
        wedding = WeddingFactory.build(planner=user, date=future_date)
        wedding.full_clean()  # Se não levantar erro, passou!

    def test_wedding_date_today_passes(self, user):
        """Garante que data de hoje passa."""
        today = timezone.now().date()
        wedding = WeddingFactory.build(planner=user, date=today)
        wedding.full_clean()

    def test_wedding_date_past_fails(self, user):
        """
        Garante que datas passadas disparam ValidationError.
        Este é o teste que estava falhando.
        """
        yesterday = timezone.now().date() - timedelta(days=1)
        wedding = WeddingFactory.build(planner=user, date=yesterday)

        # Agora chamamos o full_clean explicitamente dentro do raises
        with pytest.raises(ValidationError) as excinfo:
            wedding.full_clean()

        # Verificamos se o erro está especificamente no campo 'date'
        assert "date" in excinfo.value.message_dict
        assert "A data do casamento não pode ser no passado." in str(excinfo.value)


@pytest.mark.django_db
class TestWeddingBusinessRules:
    """
    Testes para as regras de negócio implementadas no método clean().
    Focamos apenas na lógica do status vs data.
    """

    def test_status_completed_valid_past_date(self, user):
        """
        Garante que um casamento que já aconteceu pode ser marcado como CONCLUÍDO.
        """
        # Ontem
        past_date = timezone.now().date() - timedelta(days=1)

        # Usamos .build(planner=user) para que o objeto tenha um planner
        # caso a lógica do clean() ou do Mixin venha a precisar dele.
        wedding = WeddingFactory.build(
            planner=user, date=past_date, status=Wedding.StatusChoices.COMPLETED
        )

        # Não deve lançar erro
        wedding.clean()

    def test_status_completed_invalid_future_date(self, user):
        """
        Garante que NÃO se pode concluir um casamento que ainda não aconteceu (Precoce).
        """
        # Daqui a um ano
        future_date = timezone.now().date() + timedelta(days=365)
        wedding = WeddingFactory.build(
            planner=user, date=future_date, status=Wedding.StatusChoices.COMPLETED
        )

        with pytest.raises(ValidationError) as excinfo:
            wedding.clean()

        assert "Não pode marcar como CONCLUÍDO antes da data do casamento" in str(
            excinfo.value
        )

    def test_other_statuses_work_with_future_dates(self, user):
        """
        Garante que as travas do status COMPLETED não afetam outros status.
        """
        future_date = timezone.now().date() + timedelta(days=30)

        # Testando IN_PROGRESS
        wedding_progress = WeddingFactory.build(
            planner=user, date=future_date, status=Wedding.StatusChoices.IN_PROGRESS
        )
        wedding_progress.clean()  # Deve passar

        # Testando CANCELED
        wedding_canceled = WeddingFactory.build(
            planner=user, date=future_date, status=Wedding.StatusChoices.CANCELED
        )
        wedding_canceled.clean()  # Deve passar

from datetime import date

import pytest
from django.test import TestCase

from apps.users.models import User
from apps.weddings.models import Wedding


@pytest.mark.integration
class WeddingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="planner", email="p@test.com", password="123"
        )

    def test_wedding_creation_and_str(self):
        """
        Testa se o __str__ retorna 'Groom & Bride' e se defaults funcionam.
        """
        wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Romeo",
            bride_name="Juliet",
            date=date(2025, 5, 20),
            location="Verona",
            budget=50000,
        )

        # Verifica __str__
        self.assertEqual(str(wedding), "Romeo & Juliet")

        # Verifica default do status
        self.assertEqual(wedding.status, "IN_PROGRESS")

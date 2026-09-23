"""
Testes unitários para o LockoutService.
"""

from collections.abc import Generator

import pytest
from django.core.cache import cache

from apps.users.services.lockout_service import LockoutService


@pytest.mark.django_db
class TestLockoutService:
    @pytest.fixture(autouse=True)
    def clear_cache(self) -> Generator[None, None, None]:
        cache.clear()
        yield
        cache.clear()

    def test_record_failure_increments_attempts(self) -> None:
        email = "user@example.com"
        assert not LockoutService.is_locked(email)

        attempts, is_locked = LockoutService.record_failure(email)
        assert attempts == 1
        assert not is_locked
        assert not LockoutService.is_locked(email)

        attempts, is_locked = LockoutService.record_failure(email)
        assert attempts == 2
        assert not is_locked
        assert not LockoutService.is_locked(email)

    def test_lockout_triggered_after_max_attempts(self) -> None:
        email = "victim@example.com"
        for _ in range(4):
            LockoutService.record_failure(email)
            assert not LockoutService.is_locked(email)

        # 5ª tentativa (limite)
        attempts, is_locked = LockoutService.record_failure(email)
        assert attempts == 5
        assert is_locked is True
        assert LockoutService.is_locked(email)
        assert LockoutService.get_remaining_lockout_seconds(email) > 0

    def test_reset_failures_clears_lockout_and_counter(self) -> None:
        email = "reset@example.com"
        for _ in range(5):
            LockoutService.record_failure(email)

        assert LockoutService.is_locked(email)

        LockoutService.reset_failures(email)
        assert not LockoutService.is_locked(email)
        assert LockoutService.get_remaining_lockout_seconds(email) == 0

    def test_email_normalization_case_and_whitespace(self) -> None:
        email_raw = "  UsEr.TeSt@Example.COM "
        email_clean = "user.test@example.com"

        LockoutService.record_failure(email_raw)
        attempts, _ = LockoutService.record_failure(email_clean)
        assert attempts == 2

        for _ in range(3):
            LockoutService.record_failure(email_raw)

        assert LockoutService.is_locked(email_clean)
        assert LockoutService.is_locked(email_raw)

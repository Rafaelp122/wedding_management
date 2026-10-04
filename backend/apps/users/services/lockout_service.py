"""Serviço de bloqueio temporário de conta (Account Lockout).

Gerencia contadores de falhas consecutivas de autenticação e bloqueio temporário
de contas utilizando o cache configurado (Redis em produção ou LocMem em testes),
mitigando ataques de força bruta, credential stuffing e password spraying.
"""

from __future__ import annotations

import logging
import time
from typing import Any, cast

from django.conf import settings
from django.core.cache import caches


logger = logging.getLogger(__name__)


class LockoutService:
    """
    Serviço de controle de tentativas de autenticação e bloqueio temporário de contas.

    Regra de Negócio:
        BR-U06 (docs/architecture/domains/users-domain.md)
    """

    CACHE_ALIAS = "default"
    FAILURE_KEY_PREFIX = "auth_lockout_attempts:"
    BLOCKED_KEY_PREFIX = "auth_lockout_blocked:"

    @classmethod
    def _get_cache(cls) -> Any:
        return caches[cls.CACHE_ALIAS]

    @classmethod
    def _normalize_key(cls, email: str) -> str:
        return email.strip().lower()

    @classmethod
    def is_locked(cls, email: str) -> bool:
        """
        Verifica se a conta associada ao e-mail está temporariamente bloqueada.

        Returns:
            True se a conta estiver temporariamente bloqueada, False caso contrário.
        """
        cache = cls._get_cache()
        key = f"{cls.BLOCKED_KEY_PREFIX}{cls._normalize_key(email)}"
        return bool(cache.get(key))

    @classmethod
    def record_failure(cls, email: str) -> tuple[int, bool]:
        """
        Registra tentativa falha de autenticação e aplica bloqueio se o limite for atingido.

        Efeitos Colaterais:
            - Incrementa contador de tentativas no cache.
            - Registra bloqueio temporário caso atinja o limite máximo de tentativas.

        Returns:
            Tupla contendo o total de tentativas acumuladas e se a conta está bloqueada no momento.
        """
        cache = cls._get_cache()
        norm_email = cls._normalize_key(email)
        attempts_key = f"{cls.FAILURE_KEY_PREFIX}{norm_email}"
        blocked_key = f"{cls.BLOCKED_KEY_PREFIX}{norm_email}"

        max_attempts = getattr(settings, "AUTH_LOCKOUT_MAX_ATTEMPTS", 5)
        lockout_duration = getattr(settings, "AUTH_LOCKOUT_DURATION_SECONDS", 900)

        # Incrementa contador com janela de observação igual à duração do bloqueio
        try:
            attempts = cache.incr(attempts_key)
        except ValueError:
            # Chave não existia no cache
            cache.set(attempts_key, 1, timeout=lockout_duration)
            attempts = 1

        if attempts >= max_attempts:
            unlock_timestamp = time.time() + lockout_duration
            cache.set(blocked_key, unlock_timestamp, timeout=lockout_duration)
            logger.warning(
                f"Conta {norm_email} temporariamente bloqueada por {lockout_duration}s "
                f"após {attempts} falhas consecutivas de login."
            )
            return attempts, True

        return attempts, False

    @classmethod
    def reset_failures(cls, email: str) -> None:
        """
        Limpa o histórico de falhas e qualquer bloqueio ativo para a conta.

        Efeitos Colaterais:
            - Remove as chaves de tentativas e de bloqueio do cache.
        """
        cache = cls._get_cache()
        norm_email = cls._normalize_key(email)
        cache.delete_many(
            [
                f"{cls.FAILURE_KEY_PREFIX}{norm_email}",
                f"{cls.BLOCKED_KEY_PREFIX}{norm_email}",
            ]
        )

    @classmethod
    def get_remaining_lockout_seconds(cls, email: str) -> int:
        """
        Calcula o tempo restante de bloqueio em segundos para a conta informada.

        Returns:
            Segundos restantes de bloqueio ou 0 se a conta não estiver bloqueada.
        """
        cache = cls._get_cache()
        blocked_key = f"{cls.BLOCKED_KEY_PREFIX}{cls._normalize_key(email)}"
        unlock_timestamp = cast(float | None, cache.get(blocked_key))
        if not unlock_timestamp:
            return 0
        remaining = int(unlock_timestamp - time.time())
        return max(0, remaining)

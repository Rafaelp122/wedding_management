import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

import sentry_sdk


logger = logging.getLogger(__name__)


class CronRegistry:
    """
    Registro extensível para tarefas agendadas em lote (Daily Batch Cron).
    Permite que qualquer app/domínio registre funções de manutenção sem acoplar a API.
    """

    def __init__(self) -> None:
        self._registry: dict[str, dict[str, Any]] = {}

    def register(
        self, name: str, description: str = ""
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator para registrar uma função de lote diário.
        Uso:
            @cron_registry.register("mark_overdue_installments", description="...")
            def my_cron_func(): ...
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._registry[name] = {
                "func": func,
                "description": description,
            }
            logger.debug("Cron task '%s' registrada com sucesso.", name)
            return func

        return decorator

    def run_batch(self) -> list[dict[str, Any]]:
        """
        Executa todas as tarefas registradas no lote diário em sequência.
        Captura exceções no Sentry para monitoramento e retorna resultados detalhados.
        """
        results: list[dict[str, Any]] = []

        logger.info(
            "Executando lote diário de tarefas (%d tarefas registradas)...",
            len(self._registry),
        )

        for name, meta in self._registry.items():
            func = meta["func"]
            executed_at = datetime.now().isoformat()
            try:
                msg = func()
                message_str = str(msg) if msg is not None else "Executado com sucesso."
                results.append(
                    {
                        "task": name,
                        "status": "success",
                        "message": message_str,
                        "executed_at": executed_at,
                    }
                )
                logger.info("Tarefa de cron '%s' concluída: %s", name, message_str)
            except Exception as exc:
                sentry_sdk.capture_exception(exc)
                logger.exception("Falha ao executar tarefa de cron '%s'", name)
                results.append(
                    {
                        "task": name,
                        "status": "error",
                        "message": str(exc),
                        "executed_at": executed_at,
                    }
                )

        return results


# Instância global do registro de tarefas cron
cron_registry = CronRegistry()

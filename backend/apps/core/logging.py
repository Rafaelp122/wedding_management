import logging
import threading


# Armazenamento isolado por thread. Essencial para não misturar IDs
# num ambiente com dezenas de requisições concorrentes.
_thread_locals = threading.local()


def set_request_id(request_id: str) -> None:
    _thread_locals.request_id = request_id


def get_request_id() -> str | None:
    return getattr(_thread_locals, "request_id", None)


class RequestIDFilter(logging.Filter):
    """
    Injeta a variável 'request_id' no record do logger.
    Se o log for gerado fora de uma requisição HTTP (ex: CRON ou Shell),
    assume o valor 'system'.
    """

    def filter(self, record):
        record.request_id = getattr(_thread_locals, "request_id", "system")
        return True

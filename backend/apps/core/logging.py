import logging
import threading


# Armazenamento isolado por thread. Essencial para não misturar IDs
# num ambiente com dezenas de requisições concorrentes.
_thread_locals = threading.local()


class RequestIDFilter(logging.Filter):
    """
    Injeta a variável 'request_id' no record do logger.
    Se o log for gerado fora de uma requisição HTTP (ex: CRON ou Shell),
    assume o valor 'system'.
    """

    def filter(self, record):
        record.request_id = getattr(_thread_locals, "request_id", "system")
        return True

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

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(_thread_locals, "request_id", "system")
        return True


def mask_email(email: str) -> str:
    """Mascara e-mail para evitar vazamento de PII em logs de auditoria."""
    if not email or "@" not in email:
        return "***"
    name, domain = email.split("@", 1)
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + "*" * (len(name) - 2) + name[-1]
    return f"{masked_name}@{domain}"

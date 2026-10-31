"""
WSGI config for wedding_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import gc
import os
import threading

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# Otimização de Boot & GC: Desabilita temporariamente o Garbage Collector durante
# a inicialização do Django para evitar varreduras cíclicas em milhares de objetos
# alocados no startup, e congela os objetos permanentes via gc.freeze() (Python 3.7+).
gc.disable()
try:
    application = get_wsgi_application()
finally:
    gc.enable()
    gc.freeze()


# Pré-aquecimento assíncrono de conexão: Permite que o servidor web
# abra a porta imediatamente sem bloquear a inicialização principal do container.
def _async_prewarm_db() -> None:
    try:
        from django.db import connection

        connection.ensure_connection()
        connection.close()
    except Exception:
        import logging

        logging.getLogger("config.wsgi").debug(
            "Banco de dados não conectado no aquecimento em segundo plano (ignorado em build/offline)."
        )


threading.Thread(target=_async_prewarm_db, daemon=True, name="db-prewarm").start()

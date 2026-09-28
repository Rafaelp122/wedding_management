"""
WSGI config for wedding_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import gc
import os

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

# Pré-aquecimento de conexão e DNS/TLS: Garante que o driver psycopg,
# contextos SSL e sockets estejam aquecidos durante o boot, eliminando a
# latência de handshake na primeira requisição do usuário.
try:
    from django.db import connection

    connection.ensure_connection()
except Exception:
    import logging

    logging.getLogger("config.wsgi").debug(
        "Banco de dados não conectado durante o boot (ignorado em etapas de build ou offline)."
    )

"""Garante que relatório pesado não contamina o boot da API."""

import subprocess
import sys


def test_reporting_services_nao_importa_reportlab_nem_openpyxl_no_boot() -> None:
    codigo = (
        "import os, sys, django;"
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test');"
        "django.setup();"
        "import apps.reporting.services as svc;"
        "pesados = [m for m in sys.modules if m.split('.')[0] in "
        "('reportlab', 'openpyxl')];"
        "print(','.join(pesados))"
    )
    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-c", codigo],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "", f"módulos pesados no boot: {proc.stdout.strip()}"

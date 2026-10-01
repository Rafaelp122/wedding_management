"""Garante que storage e OIDC não puxam SDKs pesados no boot."""

import subprocess
import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[3]


@pytest.mark.unit
def test_storage_nao_importa_boto3_no_boot() -> None:
    codigo = (
        "import os, sys, django;"
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test');"
        "django.setup();"
        "import apps.core.services.storage.cloudflare_r2 as m;"
        "pesados = [x for x in sys.modules if x.split('.')[0] in ('boto3', 'botocore')];"
        "print(','.join(pesados))"
    )
    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-c", codigo],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "", f"boto3 no boot: {proc.stdout.strip()}"


@pytest.mark.unit
def test_oidc_nao_importa_google_auth_no_boot() -> None:
    codigo = (
        "import os, sys, django;"
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test');"
        "django.setup();"
        "import apps.core.services.oidc.gcp as m;"
        "import apps.core.services.social_auth.google_provider as p;"
        "pesados = [x for x in sys.modules if x.split('.')[0] == 'google'];"
        "print(','.join(pesados))"
    )
    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-c", codigo],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "", f"google-auth no boot: {proc.stdout.strip()}"

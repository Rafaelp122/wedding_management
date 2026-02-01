#!/usr/bin/env python3
"""
Script para gerar uma SECRET_KEY segura para Django.
Uso: python generate_secret_key.py
"""

import secrets
import string


def generate_secret_key(length=50):
    """Gera uma chave aleatória segura."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(secrets.choice(chars) for _ in range(length))


if __name__ == "__main__":
    try:
        from django.core.management.utils import get_random_secret_key

        secret_key = get_random_secret_key()
    except ImportError:
        secret_key = generate_secret_key()

    print("\n" + "=" * 70)
    print("DJANGO SECRET_KEY GERADA COM SUCESSO!")
    print("=" * 70)
    print(f"\nSECRET_KEY={secret_key}\n")
    print("Copie a linha acima e cole no seu arquivo .env")
    print("=" * 70 + "\n")
    print("=" * 70 + "\n")

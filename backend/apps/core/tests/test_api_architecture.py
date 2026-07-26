"""
Testes de arquitetura da API Ninja.

Inspeciona a instância global da API (config.api.api) para validar a aderência
às diretrizes arquiteturais do projeto:
- 100% das rotas cadastradas possuem operation_id explícito e não vazio.
- Rotas protegidas (que exigem autenticação JWT) retornam HTTP 401 quando
  acessadas sem token.
"""

import re
from typing import Any

import pytest
from django.test import Client

from config.api import api


@pytest.mark.django_db
class TestApiArchitecture:
    """
    Testes de integridade arquitetural para a API Ninja.
    """

    def test_all_routes_have_operation_id(self) -> None:
        """
        Garante que todas as rotas/operações registradas na API possuem operation_id.

        Nenhuma rota cadastrada pode ficar sem um operation_id definido,
        pois ele é essencial para a geração de código cliente via Orval.
        """
        all_operations: list[tuple[str, list[str], Any]] = []
        missing_operation_ids: list[tuple[str, list[str]]] = []

        for prefix, router in api._routers:
            for path, path_op in router.path_operations.items():
                full_path = f"{prefix}{path}"
                for op in path_op.operations:
                    all_operations.append((full_path, op.methods, op.operation_id))
                    if not op.operation_id or not str(op.operation_id).strip():
                        missing_operation_ids.append((full_path, op.methods))

        assert len(all_operations) > 0, (
            "Nenhuma operação registrada na instância da API Ninja."
        )
        assert not missing_operation_ids, (
            f"As seguintes rotas não possuem operation_id definido: "
            f"{missing_operation_ids}"
        )

    def test_protected_routes_return_401_without_token(self, client: Client) -> None:
        """
        Garante que requisições não autenticadas para rotas protegidas
        retornam HTTP 401.

        Filtra as rotas públicas (/health e /auth/*) e dispara requisições HTTP
        simuladas para todas as demais rotas para assegurar a blindagem de segurança.
        """
        unauthorized_failures: list[str] = []
        tested_count = 0

        for prefix, router in api._routers:
            for path, path_op in router.path_operations.items():
                full_route = (prefix + path).replace("//", "/")
                # Ignora rotas públicas de infraestrutura e autenticação
                if full_route.startswith("/health") or full_route.startswith("/auth/"):
                    continue

                # Substitui parâmetros de rota por valor fictício
                normalized_path = re.sub(
                    r"\{[a-zA-Z0-9_:]+\}",
                    "00000000-0000-0000-0000-000000000000",
                    full_route,
                )
                url = f"/api/v1{normalized_path}"

                for op in path_op.operations:
                    for method in op.methods:
                        tested_count += 1
                        http_method = method.lower()
                        method_func = getattr(client, http_method, None)
                        if not method_func:
                            continue

                        response = method_func(url)
                        if response.status_code != 401:
                            unauthorized_failures.append(
                                f"[{method}] {url} -> status {response.status_code}"
                                " (esperado 401)"
                            )

        assert tested_count > 0, (
            "Nenhuma rota protegida foi encontrada para validação de 401."
        )
        assert not unauthorized_failures, (
            "Rotas protegidas permitiram acesso sem token ou não retornaram 401:\n"
            + "\n".join(unauthorized_failures)
        )

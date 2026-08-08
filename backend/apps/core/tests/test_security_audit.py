"""
Teste de auditoria estática de segurança e arquitetura via AST.

Analisa a camada de serviços (apps/*/services/*.py ou services.py) para garantir:
1. Nenhum serviço importa ou invoca django.shortcuts.get_object_or_404
   (deve obrigatoriamente utilizar get_object_or_404_for_tenant).
2. Todas as funções e métodos de serviço públicos de domínio declaram
   o parâmetro 'company' para sustentação da blindagem multi-tenant.
"""

import ast
from pathlib import Path

import pytest

from apps.core.tests.utils import find_service_files


def _check_node_for_get_object_or_404(node: ast.AST, filename: str) -> list[str]:
    """
    Verifica se um nó AST representa importação ou uso de get_object_or_404.

    Args:
        node: Nó da árvore sintática abstrata.
        filename: Nome do arquivo analisado.

    Returns:
        Lista com mensagens de erro caso encontre violações no nó.
    """
    violations: list[str] = []

    if isinstance(node, ast.ImportFrom) and node.module == "django.shortcuts":
        for alias in node.names:
            if alias.name == "get_object_or_404":
                violations.append(
                    f"{filename}:{node.lineno} importa "
                    "'django.shortcuts.get_object_or_404'"
                )

    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == "get_object_or_404":
            violations.append(f"{filename}:{node.lineno} chama 'get_object_or_404()'")
        elif isinstance(func, ast.Attribute) and func.attr == "get_object_or_404":
            violations.append(f"{filename}:{node.lineno} chama '.get_object_or_404()'")

    return violations


@pytest.mark.unit
class TestSecurityAudit:
    """
    Auditoria estática por análise de AST dos arquivos da camada de serviços.
    """

    @property
    def service_files(self) -> list[Path]:
        """
        Retorna a lista de caminhos para todos os arquivos de serviço do projeto.
        """
        return find_service_files()

    def test_services_do_not_use_django_get_object_or_404(self) -> None:
        """
        Garante que nenhum serviço utiliza django.shortcuts.get_object_or_404.

        Serviços de domínio devem obrigatoriamente utilizar get_object_or_404_for_tenant
        para evitar vazamento de dados entre empresas.
        """
        violations: list[str] = []

        for filepath in self.service_files:
            try:
                tree = ast.parse(
                    filepath.read_text(encoding="utf-8"), filename=str(filepath)
                )
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                violations.extend(
                    _check_node_for_get_object_or_404(node, filepath.name)
                )

        assert not violations, (
            "Serviços utilizando django.shortcuts.get_object_or_404 encontrados. "
            "Use get_object_or_404_for_tenant para isolamento por tenant:\n"
            + "\n".join(violations)
        )

    def test_public_service_functions_declare_company_parameter(self) -> None:
        """
        Garante que funções públicas de serviços declaram o parâmetro 'company'.

        Isenções permitidas apenas para serviços globais/infraestrutura que não possuem
        escopo de tenant (ex: autenticação inicial, registro de empresa, social auth).
        """
        exempt_relative_files = {
            "apps/users/services/registration_service.py",
            "apps/users/services/token_service.py",
            "apps/users/services/google_auth_service.py",
            "apps/tenants/services/tenant_service.py",
            "apps/core/services/storage/base.py",
            "apps/core/services/storage/cloudflare_r2.py",
            "apps/core/services/storage/factory.py",
            "apps/core/services/social_auth/base.py",
            "apps/core/services/social_auth/google_provider.py",
            "apps/core/services/oidc/base.py",
            "apps/core/services/oidc/gcp.py",
            "apps/core/services/oidc/mock.py",
            "apps/core/services/oidc/factory.py",
            "apps/scheduler/services/templates.py",
        }

        exempt_function_names = {
            "set_storage_service",
            "get_storage_client",
        }

        missing_company: list[str] = []

        for filepath in self.service_files:
            posix_path = filepath.as_posix()
            if any(posix_path.endswith(exempt) for exempt in exempt_relative_files):
                continue

            try:
                tree = ast.parse(
                    filepath.read_text(encoding="utf-8"), filename=str(filepath)
                )
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("_") or node.name in exempt_function_names:
                        continue

                    arg_names = [arg.arg for arg in node.args.args] + [
                        arg.arg for arg in node.args.kwonlyargs
                    ]

                    if "company" not in arg_names:
                        missing_company.append(
                            f"{filepath.name}:{node.lineno} -> "
                            f"{node.name}({', '.join(arg_names)})"
                        )

        assert not missing_company, (
            "Funções públicas de serviços encontradas sem o parâmetro 'company':\n"
            + "\n".join(missing_company)
        )

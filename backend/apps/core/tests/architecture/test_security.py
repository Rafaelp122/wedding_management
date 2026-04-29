import ast
import os
from pathlib import Path
from typing import List

import pytest


def _get_controller_files() -> List[Path]:
    """Descobre todos os arquivos de controlador seguindo a convenção apps/*/api/*.py"""
    base_path = Path(__file__).parent.parent.parent.parent
    return list(base_path.glob("**/api/*.py"))


def _audit_file_security(file_path: Path):
    """Analisa um arquivo Python e garante a segurança em todos os métodos de classe."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        # Procuramos por classes (nossos controladores)
        if isinstance(node, ast.ClassDef):
            # Ignora AuthController pois não lida com recursos por UUID de tenant
            if node.name == "AuthController":
                continue

            for item in node.body:
                # Procuramos por métodos (nossos endpoints)
                if not isinstance(item, ast.FunctionDef):
                    continue

                # Identifica parâmetros que são UUIDs (pela convenção de sufixo _uuid)
                uuid_params = [
                    a.arg for a in item.args.args if a.arg.endswith("_uuid")
                ]
                if not uuid_params:
                    continue

                # Extrai todas as chamadas dentro do método
                all_calls = []
                for n in ast.walk(item):
                    if isinstance(n, ast.Call):
                        if isinstance(n.func, ast.Name):
                            all_calls.append(n.func.id)
                        elif isinstance(n.func, ast.Attribute):
                            all_calls.append(n.func.attr)

                for uuid_param in uuid_params:
                    # Convenção: event_uuid deve chamar get_event() ou .resolve()
                    resource_name = uuid_param.replace("_uuid", "")
                    expected_getter = f"get_{resource_name}"

                    # Mapeamentos especiais
                    special_mappings = {"category": "get_budget_category"}
                    if resource_name in special_mappings:
                        expected_getter = special_mappings[resource_name]

                    # Proteção: Deve chamar o getter gerado ou o método .resolve() do Manager
                    has_protection = (
                        expected_getter in all_calls or "resolve" in all_calls
                    )

                    assert has_protection, (
                        f"VULNERABILIDADE IDOR: No arquivo {file_path.name}, o método "
                        f"{node.name}.{item.name}() recebe '{uuid_param}' "
                        f"mas não chama {expected_getter}() ou .resolve()."
                    )


@pytest.mark.parametrize("controller_file", _get_controller_files())
def test_all_controllers_enforce_resource_security(controller_file):
    """
    AUDITORIA DE SEGURANÇA AUTOMATIZADA:
    Varre todos os arquivos da pasta 'api' de todos os apps e garante
    que ninguém esqueceu de validar a posse de um recurso UUID.
    """
    _audit_file_security(controller_file)

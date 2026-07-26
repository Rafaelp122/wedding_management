"""
Auditoria estática de transações atômicas nas camadas de serviço (services).

Valida se todas as funções públicas ou métodos de serviço que realizam
múltiplas operações de escrita no ORM (save, create, delete, update, etc.)
estão devidamente protegidos com a anotação @transaction.atomic ou um bloco
com context manager 'with transaction.atomic():'.
"""

import ast
from pathlib import Path

import pytest


# Métodos do Django ORM que executam escritas/alterações no banco de dados
WRITE_METHODS: set[str] = {
    "save",
    "create",
    "bulk_create",
    "bulk_update",
    "update",
    "delete",
    "get_or_create",
    "update_or_create",
}


def _is_atomic_expr(expr: ast.expr) -> bool:
    """
    Verifica se uma expressão AST corresponde ao uso de atomic
    (ex: transaction.atomic, atomic, ou chamada transaction.atomic(...)).
    """
    if isinstance(expr, ast.Attribute) and expr.attr == "atomic":
        return True
    if isinstance(expr, ast.Name) and expr.id == "atomic":
        return True
    if isinstance(expr, ast.Call):
        return _is_atomic_expr(expr.func)
    return False


def _has_atomic_decorator(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Verifica se a função possui o decorador @transaction.atomic ou @atomic.
    """
    for decorator in func_node.decorator_list:
        if _is_atomic_expr(decorator):
            return True
    return False


def _has_atomic_with_block(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Verifica se a função possui bloco 'with transaction.atomic():'.
    """
    for node in ast.walk(func_node):
        if isinstance(node, ast.With):
            for item in node.items:
                if _is_atomic_expr(item.context_expr):
                    return True
    return False


def _count_orm_writes(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """
    Conta o número de chamadas diretas a métodos de escrita do ORM.
    """
    write_count = 0
    for node in ast.walk(func_node):
        # Ignora nós internos de funções aninhadas para não duplicar contagem
        if node is not func_node and isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in WRITE_METHODS:
                write_count += 1
    return write_count


def _find_service_files() -> list[Path]:
    """
    Localiza todos os arquivos de serviço sob apps/*/services.py
    ou apps/*/services/*.py. Exclui arquivos de teste.
    """
    apps_dir = Path(__file__).resolve().parent.parent.parent
    service_files: list[Path] = []

    for path in apps_dir.glob("**/*.py"):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue

        if path.name == "services.py" or "services" in path.parts:
            service_files.append(path)

    return sorted(service_files)


@pytest.mark.django_db
class TestAtomicServiceAudit:
    """
    Suíte de auditoria de atomicidade em funções de serviço.
    """

    def test_services_with_multiple_writes_are_atomic(self) -> None:
        """
        Garante que funções com 2+ escritas possuem transação atômica.
        """
        service_files = _find_service_files()
        assert service_files, "Nenhum arquivo de serviço encontrado para auditoria."

        violations: list[str] = []

        for file_path in service_files:
            source = file_path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError as exc:
                violations.append(f"Erro de sintaxe em {file_path}: {exc}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    write_count = _count_orm_writes(node)
                    if write_count >= 2:
                        is_atomic = _has_atomic_decorator(
                            node
                        ) or _has_atomic_with_block(node)
                        if not is_atomic:
                            root = Path(__file__).resolve().parent.parent.parent.parent
                            rel_path = file_path.relative_to(root)
                            msg = (
                                f"Função '{node.name}' em {rel_path}:{node.lineno} "
                                f"realiza {write_count} escritas sem atomic."
                            )
                            violations.append(msg)

        assert not violations, (
            "Funções de serviço com múltiplas escritas sem atomicidade:\n"
            + "\n".join(violations)
        )

    def test_atomic_auditor_helper_detects_non_atomic_function(self) -> None:
        """
        Teste unitário do próprio auditador AST.
        """
        dummy_code = """
def non_atomic_service(obj1, obj2):
    obj1.save()
    obj2.delete()
"""
        tree = ast.parse(dummy_code)
        func_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
        assert _count_orm_writes(func_node) == 2
        assert not _has_atomic_decorator(func_node)
        assert not _has_atomic_with_block(func_node)

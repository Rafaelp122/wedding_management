"""
Auditoria estática via AST dos contratos de interfaces públicas (ADR-031).

Garante a conformidade arquitetural das fachadas públicas (interfaces.py):
1. Todas as funções públicas no topo do arquivo declaram o parâmetro
   'company' ou 'company_id', sustentando o multi-tenancy (ADR-016 e ADR-019).
2. O arquivo de interface não importa módulos da camada de apresentação
   (api ou views).
3. O arquivo de interface não importa models de outros Bounded Contexts em tempo
   de execução (apenas seus próprios models internos ou interfaces/schemas alheios).
"""

import ast
from pathlib import Path

import pytest

from apps.core.tests.utils import find_interface_files


def _is_type_checking_guard(node: ast.AST) -> bool:
    """
    Verifica se um nó AST condicional representa 'if TYPE_CHECKING:'.

    Args:
        node: Nó da árvore sintática abstrata.

    Returns:
        True se for um bloco condicional de TYPE_CHECKING, False caso contrário.
    """
    if not isinstance(node, ast.If):
        return False
    test = node.test
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    if isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
        return True
    return False


def _collect_import_nodes(
    tree: ast.AST,
    include_type_checking: bool = False,
) -> list[ast.Import | ast.ImportFrom]:
    """
    Coleta todas as declarações de importação da AST.

    Args:
        tree: Raiz da árvore sintática abstrata.
        include_type_checking: Se True, inclui instruções em 'if TYPE_CHECKING:'.
            Se False, coleta apenas importações executadas em tempo de execução.

    Returns:
        Lista de nós ast.Import e ast.ImportFrom encontrados.
    """
    imports: list[ast.Import | ast.ImportFrom] = []

    def visit(node: ast.AST) -> None:
        if not include_type_checking and _is_type_checking_guard(node):
            if isinstance(node, ast.If):
                for orelse_node in node.orelse:
                    visit(orelse_node)
            return

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)

        for child_node in ast.iter_child_nodes(node):
            visit(child_node)

    visit(tree)
    return imports


def check_top_level_functions_for_tenant_param(
    tree: ast.AST,
    filename: str,
) -> list[str]:
    """
    Valida se as funções públicas de topo declaram 'company' ou 'company_id'.

    Args:
        tree: Raiz da AST do arquivo analisado.
        filename: Identificador do arquivo para exibição de erros.

    Returns:
        Lista de mensagens descrevendo funções que violam a regra.
    """
    violations: list[str] = []
    body_nodes = tree.body if isinstance(tree, ast.Module) else []

    for node in body_nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue

            param_names = {
                arg.arg
                for arg in (
                    node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                )
            }

            if "company" not in param_names and "company_id" not in param_names:
                params_str = ", ".join(param_names) if param_names else "vazio"
                violations.append(
                    f"{filename}:{node.lineno} -> Função pública '{node.name}' "
                    f"com args ({params_str}) não declara 'company' ou 'company_id'."
                )

    return violations


def check_presentation_layer_imports(
    node: ast.Import | ast.ImportFrom,
    filename: str,
) -> list[str]:
    """
    Verifica se uma instrução de importação referencia módulos 'api' ou 'views'.

    Args:
        node: Nó de importação AST.
        filename: Identificador do arquivo para exibição de erros.

    Returns:
        Lista de mensagens de violação caso importe a camada de apresentação.
    """
    violations: list[str] = []

    if isinstance(node, ast.Import):
        for alias in node.names:
            parts = alias.name.split(".")
            if "api" in parts or "views" in parts:
                violations.append(
                    f"{filename}:{node.lineno} importa da camada de apresentação: "
                    f"'{alias.name}'."
                )

    elif isinstance(node, ast.ImportFrom):
        if node.module:
            parts = node.module.split(".")
            if "api" in parts or "views" in parts:
                violations.append(
                    f"{filename}:{node.lineno} importa da camada de apresentação: "
                    f"'{node.module}'."
                )
        for alias in node.names:
            if alias.name in ("api", "views"):
                full_name = f"{node.module}.{alias.name}" if node.module else alias.name
                violations.append(
                    f"{filename}:{node.lineno} importa módulo de apresentação: "
                    f"'{full_name}'."
                )

    return violations


def _check_ast_import_for_other_domain_models(
    node: ast.Import,
    current_domain: str,
    filename: str,
) -> list[str]:
    """Valida instruções 'import ...' contra models de outros domínios."""
    violations: list[str] = []
    for alias in node.names:
        parts = alias.name.split(".")
        if len(parts) >= 3 and parts[0] == "apps" and parts[2] == "models":
            if parts[1] != current_domain:
                violations.append(
                    f"{filename}:{node.lineno} importa models de outro domínio: "
                    f"'{alias.name}' (domínio atual: '{current_domain}')."
                )
    return violations


def _check_ast_import_from_for_other_domain_models(
    node: ast.ImportFrom,
    current_domain: str,
    filename: str,
) -> list[str]:
    """Valida instruções 'from ... import ...' contra models de outros domínios."""
    violations: list[str] = []

    # Importação absoluta (ex: from apps.finances.models import Expense)
    if node.level == 0 and node.module:
        parts = node.module.split(".")
        if len(parts) >= 3 and parts[0] == "apps" and parts[2] == "models":
            if parts[1] != current_domain:
                violations.append(
                    f"{filename}:{node.lineno} importa models de outro domínio: "
                    f"'{node.module}' (domínio atual: '{current_domain}')."
                )
        elif len(parts) == 2 and parts[0] == "apps" and parts[1] != current_domain:
            for alias in node.names:
                if alias.name == "models":
                    violations.append(
                        f"{filename}:{node.lineno} importa submódulo models alheio: "
                        f"'{node.module}.{alias.name}' "
                        f"(domínio atual: '{current_domain}')."
                    )
    # Importação relativa cruzada (ex: from ..finances.models import Expense)
    elif node.level == 2 and node.module:
        parts = node.module.split(".")
        if len(parts) >= 2 and parts[1] == "models" and parts[0] != current_domain:
            violations.append(
                f"{filename}:{node.lineno} importa models relativos de outro domínio: "
                f"'{node.module}' (domínio atual: '{current_domain}')."
            )

    return violations


def check_other_domain_models_imports(
    node: ast.Import | ast.ImportFrom,
    current_domain: str,
    filename: str,
) -> list[str]:
    """
    Verifica se uma instrução importa models de outros Bounded Contexts.

    Interfaces só podem importar seus próprios models internos
    (ex: apps.<current_domain>.models ou .models) ou interfaces/schemas
    de outros domínios.

    Args:
        node: Nó de importação AST.
        current_domain: Nome do Bounded Context do arquivo inspecionado.
        filename: Identificador do arquivo para exibição de erros.

    Returns:
        Lista de mensagens de violação caso importe models de outro domínio.
    """
    if isinstance(node, ast.Import):
        return _check_ast_import_for_other_domain_models(node, current_domain, filename)
    if isinstance(node, ast.ImportFrom):
        return _check_ast_import_from_for_other_domain_models(
            node, current_domain, filename
        )
    return []


@pytest.mark.unit
class TestInterfacesAudit:
    """
    Auditoria estática de arquitetura para arquivos de interface (ADR-031).
    """

    @property
    def interface_files(self) -> list[Path]:
        """Retorna todos os caminhos para arquivos interfaces.py descobertos."""
        return find_interface_files()

    def test_interfaces_discovered_in_all_core_domains(self) -> None:
        """
        Garante que todas as interfaces públicas esperadas estão presentes.
        """
        discovered_domains = {f.parent.name for f in self.interface_files}
        expected_domains = {
            "finances",
            "logistics",
            "notifications",
            "scheduler",
            "weddings",
        }
        missing = expected_domains - discovered_domains
        assert not missing, (
            f"Interfaces públicas não encontradas para os domínios: {missing}"
        )

    def test_public_functions_declare_tenant_parameter(self) -> None:
        """
        Garante que funções públicas de topo declaram 'company' ou 'company_id'.

        Sustenta o isolamento de dados multi-tenant definido nas ADRs 016 e 019.
        """
        violations: list[str] = []

        for filepath in self.interface_files:
            try:
                tree = ast.parse(
                    filepath.read_text(encoding="utf-8"),
                    filename=str(filepath),
                )
            except SyntaxError:
                continue

            violations.extend(
                check_top_level_functions_for_tenant_param(
                    tree,
                    filepath.name,
                )
            )

        assert not violations, (
            "Funções públicas em interfaces.py sem parâmetro de tenant "
            "(deve declarar 'company' ou 'company_id'):\n" + "\n".join(violations)
        )

    def test_interfaces_do_not_import_presentation_layer(self) -> None:
        """
        Garante que interfaces.py não importam nada de 'api' ou 'views'.

        Fachadas de domínio não devem possuir acoplamento com a camada HTTP/Web.
        """
        violations: list[str] = []

        for filepath in self.interface_files:
            try:
                tree = ast.parse(
                    filepath.read_text(encoding="utf-8"),
                    filename=str(filepath),
                )
            except SyntaxError:
                continue

            for node in _collect_import_nodes(tree, include_type_checking=True):
                violations.extend(check_presentation_layer_imports(node, filepath.name))

        assert not violations, (
            "Importações da camada de apresentação encontradas em interfaces.py:\n"
            + "\n".join(violations)
        )

    def test_interfaces_do_not_import_other_domain_models_at_runtime(self) -> None:
        """
        Garante que interfaces.py não importam models de outros domínios em runtime.

        Interfaces só podem importar seus próprios models internos ou
        interfaces/schemas de outros domínios (ADR-031).
        """
        violations: list[str] = []

        for filepath in self.interface_files:
            current_domain = filepath.parent.name
            try:
                tree = ast.parse(
                    filepath.read_text(encoding="utf-8"),
                    filename=str(filepath),
                )
            except SyntaxError:
                continue

            for node in _collect_import_nodes(tree, include_type_checking=False):
                violations.extend(
                    check_other_domain_models_imports(
                        node,
                        current_domain,
                        filepath.name,
                    )
                )

        assert not violations, (
            "Importações em tempo de execução de models alheios em interfaces.py:\n"
            + "\n".join(violations)
        )

    def test_auditor_detects_missing_company_parameter(self) -> None:
        """Valida detecção de função pública sem 'company' ou 'company_id'."""
        code = """
def public_action(payload: dict) -> None:
    pass

def _private_action(foo: str) -> None:
    pass

def valid_action(*, company: Company, payload: dict) -> None:
    pass

def valid_async_action(company_id: int) -> None:
    pass
"""
        tree = ast.parse(code)
        violations = check_top_level_functions_for_tenant_param(tree, "dummy.py")
        assert len(violations) == 1
        assert "public_action" in violations[0]
        assert "não declara 'company' ou 'company_id'" in violations[0]

    def test_auditor_detects_forbidden_presentation_imports(self) -> None:
        """Valida detecção de imports de módulos api e views."""
        code = """
from apps.finances.api import router
from apps.weddings.views import index
from .api import something
import apps.logistics.views
"""
        tree = ast.parse(code)
        violations: list[str] = []
        for node in _collect_import_nodes(tree, include_type_checking=True):
            violations.extend(check_presentation_layer_imports(node, "dummy.py"))

        assert len(violations) == 4

    def test_auditor_detects_other_domain_models_import(self) -> None:
        """Valida que importação de models alheios gera violação e próprios não."""
        code = """
from apps.finances.models import Expense
from apps.scheduler.models import Event
from apps.finances.schemas import ExpenseIn
from apps.finances.interfaces import create_expense_from_contract
"""
        tree = ast.parse(code)
        violations: list[str] = []
        for node in _collect_import_nodes(tree, include_type_checking=False):
            violations.extend(
                check_other_domain_models_imports(
                    node,
                    current_domain="scheduler",
                    filename="dummy.py",
                )
            )

        assert len(violations) == 1
        assert "apps.finances.models" in violations[0]

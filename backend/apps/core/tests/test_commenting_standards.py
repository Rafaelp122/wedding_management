"""
Validação de padrões de documentação e auditoria de termos proibidos.

Garante que todas as funções públicas da camada de serviço (services)
possuem docstrings em formato Google Style não-vazias e que nenhum arquivo
da aplicação contém referências/termos de IA proibidos conforme as regras
do projeto.
"""

import ast
from pathlib import Path

import pytest

from apps.core.tests.utils import find_service_files


FORBIDDEN_AI_TERMS: list[str] = [
    "bolt",
    "jules",
    "copilot",
    "chatgpt",
    "codeium",
    "ai generated",
]


def _find_all_python_files() -> list[Path]:
    """
    Retorna todos os arquivos Python da aplicação apps/.
    """
    apps_dir = Path(__file__).resolve().parent.parent.parent
    python_files: list[Path] = []

    for path in apps_dir.glob("**/*.py"):
        if "__pycache__" in path.parts or ".venv" in path.parts:
            continue
        python_files.append(path)

    return sorted(python_files)


def _get_func_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Extrai nomes dos argumentos posicionais e nomeados de uma função."""
    func_args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")] + [
        a.arg for a in node.args.kwonlyargs
    ]
    if node.args.vararg:
        func_args.append(node.args.vararg.arg)
    if node.args.kwarg:
        func_args.append(node.args.kwarg.arg)
    return func_args


def _has_non_none_return(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Verifica se a função possui anotação de retorno diferente de None."""
    if not node.returns:
        return False
    if isinstance(node.returns, ast.Constant) and node.returns.value is None:
        return False
    if isinstance(node.returns, ast.Name) and node.returns.id == "None":
        return False
    return True


def _validate_google_style_docstring(
    node: ast.FunctionDef | ast.AsyncFunctionDef, docstring: str | None
) -> list[str]:
    """
    Valida se a docstring de uma função pública possui formato Google Style.

    Args:
        node: Nó da função na árvore AST.
        docstring: Texto da docstring extraída.

    Returns:
        Lista com as violações encontradas.
    """
    errors: list[str] = []
    if not docstring or not docstring.strip():
        errors.append("não possui docstring ou possui docstring vazia.")
        return errors

    func_args = _get_func_args(node)
    if func_args:
        has_args_section = any(
            sec in docstring
            for sec in ("Args:", "Parameters:", "Parâmetros:", "Argumentos:")
        ) or any(arg in docstring for arg in func_args)
        if not has_args_section:
            args_str = ", ".join(func_args)
            errors.append(
                f"parâmetros ({args_str}) sem seção 'Args:' "
                "ou descrição no formato Google Style."
            )

    if _has_non_none_return(node):
        has_returns_section = any(
            sec in docstring
            for sec in ("Returns:", "Retorna:", "Return:", "Retorno:", "Retorna")
        )
        if not has_returns_section:
            errors.append(
                "declara retorno mas não contém "
                "seção 'Returns:' ou descrição do retorno."
            )

    return errors


@pytest.mark.unit
class TestCommentingStandards:
    """
    Suíte de testes para padrões de comentários e auditoria de código limpo.
    """

    def test_all_public_service_functions_have_docstrings(self) -> None:
        """
        Garante que 100% das funções e métodos públicos em arquivos de serviço
        possuem docstrings em formato Google Style não-vazias.
        """
        service_files = find_service_files()
        assert service_files, "Nenhum arquivo de serviço encontrado para validação."

        missing_docstrings: list[str] = []
        root_dir = Path(__file__).resolve().parent.parent.parent.parent

        for file_path in service_files:
            source = file_path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("_"):
                        continue

                    docstring = ast.get_docstring(node)
                    doc_errors = _validate_google_style_docstring(node, docstring)
                    if doc_errors:
                        rel_path = file_path.relative_to(root_dir)
                        for err in doc_errors:
                            msg = (
                                f"Função pública '{node.name}' "
                                f"em {rel_path}:{node.lineno} {err}"
                            )
                            missing_docstrings.append(msg)

        assert not missing_docstrings, (
            "Violações de docstring em formato Google Style em funções de serviço:\n"
            + "\n".join(missing_docstrings)
        )

    def test_no_forbidden_ai_terms_in_codebase(self) -> None:
        """
        Garante que nenhum arquivo Python em apps/ contém marcas ou menções
        a ferramentas de geração de IA proibidas.
        """
        python_files = _find_all_python_files()
        assert len(python_files) > 0, "Nenhum arquivo Python encontrado em apps/."

        found_terms: list[str] = []
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        current_file = Path(__file__).resolve()

        for file_path in python_files:
            if file_path.resolve() == current_file:
                continue

            lines = file_path.read_text(encoding="utf-8").splitlines()
            rel_path = file_path.relative_to(root_dir)

            for line_idx, line in enumerate(lines, start=1):
                line_lower = line.lower()
                for term in FORBIDDEN_AI_TERMS:
                    if term in line_lower:
                        msg = (
                            f"Termo proibido '{term}' em {rel_path}:{line_idx}: "
                            f"'{line.strip()}'"
                        )
                        found_terms.append(msg)

        assert not found_terms, (
            "Termos de IA proibidos foram encontrados no código fonte:\n"
            + "\n".join(found_terms)
        )

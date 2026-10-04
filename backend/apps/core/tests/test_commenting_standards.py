"""
Validação de padrões de documentação e auditoria de termos proibidos.

Garante que todas as funções públicas da camada de serviço (services)
possuem docstrings em formato Google Style não-vazias e que nenhum arquivo
da aplicação contém referências/termos de IA proibidos conforme as regras
do projeto.
"""

import ast
import re
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

FORBIDDEN_AI_PATTERNS: list[re.Pattern[str]] = [
    re.compile(rf"\b{re.escape(t)}\b", re.IGNORECASE) for t in FORBIDDEN_AI_TERMS
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


TYPE_IN_ARGS_PATTERN = re.compile(r"^\s*([a-zA-Z_]\w*)\s*\(([^)]+)\)\s*:", re.MULTILINE)
REDUNDANT_RETURN_TYPE_PATTERN = re.compile(
    r"^\s*Returns:\s*\n\s*([A-Za-z0-9_]+(?:\[[^\]]+\])?)\s*:\s*(.*)",
    re.MULTILINE,
)
ARG_IN_ARGS_PATTERN = re.compile(
    r"^\s{4,8}([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*:", re.MULTILINE
)


def _check_anti_type_drift(docstring: str) -> list[str]:
    """Verifica se há tipos redundantes declarados em Args ou Returns."""
    errors: list[str] = []
    arg_type_match = TYPE_IN_ARGS_PATTERN.search(docstring)
    if arg_type_match:
        errors.append(
            f"parâmetro '{arg_type_match.group(1)}' declara tipo redundante "
            f"'({arg_type_match.group(2)})' na docstring. Tipos pertencem exclusivamente "
            "à assinatura da função."
        )

    ret_type_match = REDUNDANT_RETURN_TYPE_PATTERN.search(docstring)
    if ret_type_match:
        errors.append(
            f"seção 'Returns:' declara tipo redundante '{ret_type_match.group(1)}:'. "
            "Tipos pertencem exclusivamente à assinatura. Descreva apenas o estado "
            "ou significado do retorno."
        )
    return errors


def _check_ghost_params(
    node: ast.FunctionDef | ast.AsyncFunctionDef, docstring: str
) -> list[str]:
    """Verifica se a seção Args faz referência a parâmetros inexistentes."""
    errors: list[str] = []
    if "Args:" not in docstring:
        return errors

    args_block = docstring.split("Args:")[1]
    for section in ("Returns:", "Raises:", "Regra de Negócio:", "Efeitos Colaterais:"):
        if section in args_block:
            args_block = args_block.split(section)[0]

    func_args = _get_func_args(node)
    for da in ARG_IN_ARGS_PATTERN.findall(args_block):
        if da not in func_args:
            errors.append(
                f"seção 'Args:' referencia parâmetro fantasma '{da}' "
                "que não existe na assinatura da função."
            )
    return errors


def _check_raises_and_returns(
    node: ast.FunctionDef | ast.AsyncFunctionDef, docstring: str
) -> list[str]:
    """Verifica a presença das seções Raises e Returns quando aplicável."""
    errors: list[str] = []
    has_raise = any(isinstance(n, ast.Raise) for n in ast.walk(node))
    if has_raise:
        has_raises_section = any(
            sec in docstring for sec in ("Raises:", "Lança:", "Raise:")
        )
        if not has_raises_section:
            errors.append(
                "função contém instrução 'raise' mas não possui seção 'Raises:' na docstring."
            )

    if _has_non_none_return(node):
        has_returns_section = any(
            sec in docstring for sec in ("Returns:", "Retorna:", "Return:", "Retorno:")
        )
        if not has_returns_section:
            errors.append(
                "declara retorno mas não contém "
                "seção 'Returns:' ou descrição do retorno."
            )
    return errors


def _validate_google_style_docstring(
    node: ast.FunctionDef | ast.AsyncFunctionDef, docstring: str | None
) -> list[str]:
    """
    Valida se a docstring de uma função pública possui formato Google Style Pragmático.

    Args:
        node: Nó da função na árvore AST.
        docstring: Texto da docstring extraída.

    Returns:
        Lista com as violações encontradas.
    """
    if not docstring or not docstring.strip():
        return ["não possui docstring ou possui docstring vazia."]

    errors: list[str] = []
    errors.extend(_check_anti_type_drift(docstring))
    errors.extend(_check_ghost_params(node, docstring))
    errors.extend(_check_raises_and_returns(node, docstring))
    return errors


@pytest.mark.unit
class TestCommentingStandards:
    """
    Suíte de testes para padrões de comentários e auditoria de código limpo.
    """

    def test_validate_google_style_docstring_unit_cases(self) -> None:
        """Valida que o validador AST detecta tipos, parâmetros fantasmas e falta de raises."""
        # 1. Sucesso pragmático (sem tipos, sem ghost, com raises e returns)
        code_valid = '''
def process_payment(company: Company, amount: int) -> bool:
    """Processa pagamento com validação de saldo.

    Args:
        amount: Valor nominal maior que zero.

    Returns:
        True se aprovado com sucesso.

    Raises:
        BusinessRuleViolation: Se saldo for insuficiente.
    """
    if amount <= 0:
        raise BusinessRuleViolation("inválido")
    return True
'''
        node = ast.parse(code_valid).body[0]
        assert isinstance(node, ast.FunctionDef)
        errors = _validate_google_style_docstring(node, ast.get_docstring(node))
        assert errors == []

        # 2. Rejeição de tipos em Args
        code_type_in_args = '''
def process(company: Company) -> bool:
    """Processa.
    Args:
        company (Company): O tenant.
    Returns:
        True se ok.
    """
    return True
'''
        node = ast.parse(code_type_in_args).body[0]
        assert isinstance(node, ast.FunctionDef)
        errors = _validate_google_style_docstring(node, ast.get_docstring(node))
        assert any("declara tipo redundante '(Company)'" in e for e in errors)

        # 3. Rejeição de tipo redundante em Returns
        code_ret_type = '''
def process() -> bool:
    """Processa.
    Returns:
        bool: Retorna sucesso.
    """
    return True
'''
        node = ast.parse(code_ret_type).body[0]
        assert isinstance(node, ast.FunctionDef)
        errors = _validate_google_style_docstring(node, ast.get_docstring(node))
        assert any("declara tipo redundante 'bool:'" in e for e in errors)

        # 4. Rejeição de parâmetro fantasma
        code_ghost = '''
def process(valid_arg: int) -> bool:
    """Processa.
    Args:
        ghost_arg: Parâmetro que não existe mais.
    Returns:
        True se ok.
    """
    return True
'''
        node = ast.parse(code_ghost).body[0]
        assert isinstance(node, ast.FunctionDef)
        errors = _validate_google_style_docstring(node, ast.get_docstring(node))
        assert any("referencia parâmetro fantasma 'ghost_arg'" in e for e in errors)

        # 5. Exigência de Raises quando houver raise
        code_missing_raises = '''
def process() -> bool:
    """Processa sem Raises documentado.
    Returns:
        True se ok.
    """
    raise ValueError("erro")
'''
        node = ast.parse(code_missing_raises).body[0]
        assert isinstance(node, ast.FunctionDef)
        errors = _validate_google_style_docstring(node, ast.get_docstring(node))
        assert any(
            "contém instrução 'raise' mas não possui seção 'Raises:'" in e
            for e in errors
        )

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
                for term, pattern in zip(
                    FORBIDDEN_AI_TERMS, FORBIDDEN_AI_PATTERNS, strict=True
                ):
                    if pattern.search(line):
                        msg = (
                            f"Termo proibido '{term}' em {rel_path}:{line_idx}: "
                            f"'{line.strip()}'"
                        )
                        found_terms.append(msg)

        assert not found_terms, (
            "Termos de IA proibidos foram encontrados no código fonte:\n"
            + "\n".join(found_terms)
        )

"""
Validação de padrões de documentação e auditoria de termos proibidos.

Garante que todas as funções públicas da camada de serviço (services)
possuem docstrings em formato Google Style não-vazias e que nenhum arquivo
da aplicação contém referências/termos de IA proibidos conforme as regras
do projeto.
"""

import ast
from pathlib import Path


FORBIDDEN_AI_TERMS: list[str] = [
    "bolt",
    "jules",
    "copilot",
    "chatgpt",
    "codeium",
    "ai generated",
]


def _find_service_files() -> list[Path]:
    """
    Retorna a lista de arquivos de serviço sob apps/*/services.py
    ou apps/*/services/*.py. Exclui módulos de teste e caches.
    """
    apps_dir = Path(__file__).resolve().parent.parent.parent
    service_files: list[Path] = []

    for path in apps_dir.glob("**/*.py"):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        if path.name == "services.py" or "services" in path.parts:
            service_files.append(path)

    return sorted(service_files)


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


class TestCommentingStandards:
    """
    Suíte de testes para padrões de comentários e auditoria de código limpo.
    """

    def test_all_public_service_functions_have_docstrings(self) -> None:
        """
        Garante que 100% das funções e métodos públicos em arquivos de serviço
        possuem docstrings preenchidas (não-vazias).
        """
        service_files = _find_service_files()
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
                    # Ignora funções/métodos privados que começam com '_'
                    if node.name.startswith("_"):
                        continue

                    docstring = ast.get_docstring(node)
                    if not docstring or not docstring.strip():
                        rel_path = file_path.relative_to(root_dir)
                        missing_docstrings.append(
                            f"Função pública '{node.name}' em {rel_path}:{node.lineno} "
                            "não possui docstring ou possui docstring vazia."
                        )

        assert not missing_docstrings, (
            "As seguintes funções públicas de serviço estão sem docstring:\n"
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
            # Exclui o próprio arquivo de auditoria para evitar falsos positivos
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

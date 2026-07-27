"""
Utilitários e auxiliares de testes para o núcleo da aplicação (core).
"""

from pathlib import Path


def find_service_files() -> list[Path]:
    """
    Localiza todos os arquivos da camada de serviço da aplicação.

    Busca por arquivos sob `apps/*/services.py` e `apps/*/services/*.py`,
    desconsiderando subdiretórios de teste, caches e arquivos de inicialização.

    Returns:
        Lista ordenada de caminhos (Path) para os arquivos de serviço.
    """
    apps_dir = Path(__file__).resolve().parent.parent.parent
    service_files: set[Path] = set()

    for path in apps_dir.glob("**/*.py"):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        if path.name == "__init__.py":
            continue

        if path.name == "services.py" or "services" in path.parts:
            service_files.add(path)

    return sorted(service_files)

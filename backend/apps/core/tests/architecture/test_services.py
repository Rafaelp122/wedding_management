import ast
import os
from pathlib import Path


def _get_all_service_files():
    """
    Retorna todos os caminhos de arquivos que terminam em _service.py
    ou services/*.py.
    """
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    service_files = []
    for root, _, files in os.walk(backend_root / "apps"):
        for file in files:
            if file.endswith("_service.py") or (
                "services" in root and file.endswith(".py") and file != "__init__.py"
            ):
                service_files.append(Path(root) / file)
    return service_files


def test_services_are_pure_from_http_requests():
    """
    AUDITORIA DE PUREZA: Garante que nenhum Service receba HttpRequest.
    A camada de domínio não deve conhecer detalhes da camada de transporte (Web).
    """
    service_files = _get_all_service_files()

    for service_file in service_files:
        with open(service_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Service"):
                for item in node.body:
                    if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue

                    # Verifica os nomes dos argumentos
                    arg_names = [a.arg for a in item.args.args]
                    assert "request" not in arg_names, (
                        f"O método {node.name}.{item.name} em {service_file.name} "
                        "recebe um argumento chamado 'request'. "
                        "Use instâncias ou IDs."
                    )

                    # Verifica type hints de HttpRequest
                    for arg in item.args.args:
                        if arg.annotation and isinstance(arg.annotation, ast.Name):
                            assert arg.annotation.id != "HttpRequest", (
                                f"O método {node.name}.{item.name} em "
                                f"{service_file.name} possui type hint de "
                                "'HttpRequest'. Mantenha o domínio puro."
                            )


def test_service_mutations_are_atomic():
    """
    AUDITORIA DE ATOMICIDADE: Garante que métodos de mutação tenham
    @transaction.atomic.
    Todo método create, update, delete ou setup deve ser transacional.
    """
    mutation_keywords = [
        "create",
        "update",
        "delete",
        "setup",
        "cancel",
        "sign",
        "partial",
    ]
    service_files = _get_all_service_files()

    for service_file in service_files:
        with open(service_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Service"):
                for item in node.body:
                    if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue

                    method_name = item.name.lower()
                    if not any(key in method_name for key in mutation_keywords):
                        continue

                    # Lista de decoradores (pode ser ast.Name ou ast.Attribute)
                    decorator_names = []
                    for dec in item.decorator_list:
                        if isinstance(dec, ast.Name):
                            decorator_names.append(dec.id)
                        elif isinstance(dec, ast.Attribute):
                            decorator_names.append(dec.attr)
                        elif isinstance(dec, ast.Call):
                            if isinstance(dec.func, ast.Name):
                                decorator_names.append(dec.func.id)
                            elif isinstance(dec.func, ast.Attribute):
                                decorator_names.append(dec.func.attr)

                    assert "atomic" in decorator_names, (
                        f"O método de mutação {node.name}.{item.name} em "
                        f"{service_file.name} esqueceu o decorador "
                        "@transaction.atomic!"
                    )

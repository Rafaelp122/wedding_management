import ast
import os
from pathlib import Path

from config.api import api as ninja_api


def _get_all_api_files():
    backend_root = Path(__file__).parent.parent.parent.parent.parent
    api_files = []
    for root, _, files in os.walk(backend_root / "apps"):
        for file in files:
            if file.endswith(".py") and (
                "api" in root or file.endswith("controller.py") or file == "api.py"
            ):
                if file != "__init__.py":
                    api_files.append(Path(root) / file)
    return api_files


def test_all_controllers_are_registered_in_config_api():
    """
    AUDITORIA DE REGISTRO: Garante que toda classe com @api_controller
    está no config/api.py.
    """
    api_files = _get_all_api_files()
    found_controllers = []

    for api_file in api_files:
        with open(api_file) as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_controller = False
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id == "api_controller":
                        is_controller = True
                    elif (
                        isinstance(dec, ast.Call)
                        and isinstance(dec.func, ast.Name)
                        and dec.func.id == "api_controller"
                    ):
                        is_controller = True

                if is_controller:
                    found_controllers.append(node.name)

    registered_controller_names = [
        r.controller.controller_class.__name__ for r in ninja_api._controller_routers
    ]

    for controller_name in found_controllers:
        assert controller_name in registered_controller_names, (
            f"O Controller '{controller_name}' não foi registrado no config/api.py."
        )


def test_all_controller_methods_have_operation_id():
    """
    AUDITORIA DE OPERATION_ID: Garante que todo endpoint defina um operation_id.
    Isso é CRÍTICO para que o Orval gere nomes de funções limpos no Frontend.
    """
    api_files = _get_all_api_files()
    route_decorators = [
        "http_get",
        "http_post",
        "http_patch",
        "http_delete",
        "http_put",
        "route",
    ]

    for api_file in api_files:
        with open(api_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    dec_name = ""

                    if isinstance(dec, ast.Attribute):
                        dec_name = dec.attr
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Attribute):
                            dec_name = dec.func.attr
                        elif isinstance(dec.func, ast.Name):
                            dec_name = dec.func.id
                    elif isinstance(dec, ast.Name):
                        dec_name = dec.id

                    if dec_name in route_decorators:
                        # Verifica se 'operation_id' está nos keywords do decorador
                        has_operation_id = False
                        if isinstance(dec, ast.Call):
                            for keyword in dec.keywords:
                                if keyword.arg == "operation_id":
                                    has_operation_id = True
                                    break

                        assert has_operation_id, (
                            f"O endpoint '{node.name}' em {api_file.name} não possui "
                            "'operation_id'. O Frontend (Orval) precisa disso para "
                            "gerar nomes de funções amigáveis."
                        )


def test_controllers_do_not_mutate_models_directly():
    """
    AUDITORIA DE CAMADAS: Garante que Controllers não façam mutações direto no banco.
    Toda criação/edição/deleção deve passar obrigatoriamente por um Service.
    """
    api_files = _get_all_api_files()
    forbidden_mutations = ["save", "delete", "create", "update", "bulk_create"]

    for api_file in api_files:
        # Ignora o teste de segurança e o próprio teste de arquitetura
        if "test_" in api_file.name:
            continue

        with open(api_file) as f:
            source = f.read()
            tree = ast.parse(source)

        # Primeiro, mapeamos todos os decoradores para ignorar chamadas dentro deles
        decorator_calls = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    for dec_child in ast.walk(dec):
                        if isinstance(dec_child, ast.Call):
                            decorator_calls.append(dec_child)

        for node in ast.walk(tree):
            # Procura por chamadas de função/método
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                # IGNORA se for uma chamada dentro de um decorador
                if node in decorator_calls:
                    continue

                method_name = node.func.attr
                if method_name in forbidden_mutations:
                    # Ignora se o objeto que chama o método for uma classe Service
                    caller_name = ""
                    if isinstance(node.func.value, ast.Name):
                        caller_name = node.func.value.id
                    elif isinstance(node.func.value, ast.Attribute):
                        caller_name = node.func.value.attr

                    if caller_name.endswith("Service"):
                        continue

                    is_model_mutation = False

                    # Caso 1: Model.objects.create() / update()
                    if (
                        isinstance(node.func.value, ast.Attribute)
                        and node.func.value.attr == "objects"
                    ):
                        is_model_mutation = True

                    # Caso 2: instance.save() / delete()
                    # Se não veio de um Service, assumimos violação
                    if method_name in ["save", "delete"] and not caller_name.endswith(
                        "Service"
                    ):
                        is_model_mutation = True

                    assert not is_model_mutation, (
                        f"Violação de Camadas: O arquivo {api_file.name} chama "
                        f"'{method_name}()' via '{caller_name}'. Mova esta lógica "
                        "para um Service."
                    )

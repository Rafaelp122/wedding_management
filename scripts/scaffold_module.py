#!/usr/bin/env python3
"""Script de Automação para Criação de Novos Bounded Contexts (ADR-031).

Gera a topologia física completa de um novo módulo Django Ninja sob apps/<nome>/,
stub de documentação Diátaxis em docs/architecture/domains/<nome>-domain.md e
registra o módulo no backend/tach.toml de forma idempotente.
"""

from __future__ import annotations

import argparse
import keyword
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


# Raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_APPS_DIR = ROOT_DIR / "backend" / "apps"
DEFAULT_DOCS_DIR = ROOT_DIR / "docs" / "architecture" / "domains"
DEFAULT_TACH_PATH = ROOT_DIR / "backend" / "tach.toml"

# Padrão estrito de nomenclatura: snake_case minúsculo iniciado por letra
MODULE_NAME_REGEX = re.compile(r"^[a-z][a-z0-9_]*$")

# Nomes reservados da arquitetura/sistema
SYSTEM_RESERVED_NAMES = {
    "core",
    "config",
    "admin",
    "api",
    "apps",
    "tests",
    "settings",
    "manage",
}


def validate_module_name(name: str) -> None:
    """Valida se o nome do módulo atende às regras de nomenclatura e segurança.

    Regras:
    - Deve seguir estritamente snake_case minúsculo iniciado por letra (^[a-z][a-z0-9_]*$).
    - Não pode ser palavra reservada da linguagem Python (ex: def, class, return).
    - Não pode ser nome reservado do sistema/arquitetura (ex: core, config, admin).

    Args:
        name: Nome do módulo a ser validado.

    Raises:
        ValueError: Se o nome fornecido violar qualquer uma das restrições.
    """
    if not name or not MODULE_NAME_REGEX.match(name):
        raise ValueError(
            f"Nome de módulo inválido: '{name}'. "
            "O nome deve estar estritamente em snake_case minúsculo iniciado por letra "
            "(ex: 'gift_registry', 'guest_book')."
        )

    if keyword.iskeyword(name):
        raise ValueError(
            f"Nome de módulo inválido: '{name}' é uma palavra reservada do Python."
        )

    if name in SYSTEM_RESERVED_NAMES:
        raise ValueError(
            f"Nome de módulo inválido: '{name}' é um nome reservado pelo sistema/arquitetura."
        )


def to_pascal_case(snake_str: str) -> str:
    """Converte um identificador snake_case para PascalCase.

    Exemplos:
        'suppliers' -> 'Suppliers'
        'gift_registry' -> 'GiftRegistry'
    """
    return "".join(part.capitalize() for part in snake_str.split("_") if part)


def _inject_module_block(
    content: str, mod_path: str, data: dict[str, Any]
) -> tuple[str, bool]:
    """Insere o bloco [[modules]] para o módulo caso ainda não exista."""
    modules = data.get("modules", [])
    if any(m.get("path") == mod_path for m in modules):
        return content, False

    new_module_block = (
        f"[[modules]]\n"
        f'path = "{mod_path}"\n'
        f"depends_on = [\n"
        f'    {{ path = "apps.core" }},\n'
        f'    {{ path = "apps.tenants" }},\n'
        f'    {{ path = "apps.users" }},\n'
        f"]\n\n"
    )
    config_match = re.search(
        r"(\[\[modules\]\]\s*\n\s*path\s*=\s*[\"']config[\"'])",
        content,
    )
    if config_match:
        idx = config_match.start()
        return content[:idx] + new_module_block + content[idx:], True

    iface_match = re.search(r"(\[\[interfaces\]\])", content)
    if iface_match:
        idx = iface_match.start()
        return content[:idx] + new_module_block + content[idx:], True

    return content.rstrip() + "\n\n" + new_module_block, True


def _inject_config_dependency(
    content: str, mod_path: str, data: dict[str, Any]
) -> tuple[str, bool]:
    """Insere o módulo nas dependências de config caso ainda não exista."""
    config_mod = next(
        (m for m in data.get("modules", []) if m.get("path") == "config"),
        None,
    )
    if config_mod is None:
        return content, False

    has_dep = any(d.get("path") == mod_path for d in config_mod.get("depends_on", []))
    if has_dep:
        return content, False

    config_match = re.search(
        r"(\[\[modules\]\]\s*\n\s*path\s*=\s*[\"']config[\"'][\s\S]*?depends_on\s*=\s*\[)([\s\S]*?)(\])",
        content,
    )
    if not config_match:
        return content, False

    prefix = config_match.group(1)
    deps_body = config_match.group(2)
    suffix = config_match.group(3)
    dep_entry = f'    {{ path = "{mod_path}" }},\n'
    new_deps_body = (
        deps_body.rstrip() + "\n" + dep_entry if deps_body.strip() else "\n" + dep_entry
    )
    new_config_block = f"{prefix}{new_deps_body}{suffix}"
    return (
        content[: config_match.start()]
        + new_config_block
        + content[config_match.end() :]
    ), True


def _inject_interface_block(
    content: str, mod_path: str, data: dict[str, Any]
) -> tuple[str, bool]:
    """Insere o bloco [[interfaces]] para o módulo caso ainda não exista."""
    interfaces = data.get("interfaces", [])
    if any(mod_path in iface.get("from", []) for iface in interfaces):
        return content, False

    new_interface_block = (
        f"[[interfaces]]\n"
        f'from = ["{mod_path}"]\n'
        f"expose = [\n"
        f'    "interfaces.*",\n'
        f'    "schemas.*",\n'
        f"]\n\n"
    )
    gateway_match = re.search(r"(#\s*---\s*Gateway Exposure)", content)
    if gateway_match:
        idx = gateway_match.start()
        return content[:idx] + new_interface_block + content[idx:], True

    return content.rstrip() + "\n\n" + new_interface_block, True


def update_tach_toml(tach_path: Path, module_name: str) -> bool:
    """Atualiza o arquivo tach.toml de forma estritamente idempotente.

    Registra:
    1. Bloco [[modules]] para apps.<nome> dependendo de apps.core, apps.tenants, apps.users.
    2. Dependência { path = "apps.<nome>" } no módulo config.
    3. Bloco [[interfaces]] expondo interfaces.* e schemas.*.

    Args:
        tach_path: Caminho para o arquivo tach.toml.
        module_name: Nome do módulo em snake_case.

    Returns:
        bool: True se alguma alteração foi feita, False se o arquivo já continha o registro.
    """
    if not tach_path.exists():
        raise FileNotFoundError(f"Arquivo tach.toml não encontrado em: {tach_path}")

    content = tach_path.read_text(encoding="utf-8")
    data = tomllib.loads(content)
    mod_path = f"apps.{module_name}"

    content, mod_changed = _inject_module_block(content, mod_path, data)
    data = tomllib.loads(content)

    content, dep_changed = _inject_config_dependency(content, mod_path, data)
    data = tomllib.loads(content)

    content, iface_changed = _inject_interface_block(content, mod_path, data)

    modified = mod_changed or dep_changed or iface_changed
    if modified:
        tach_path.write_text(content, encoding="utf-8")

    return modified


def create_bounded_context_files(target_dir: Path, name: str) -> None:
    """Cria a árvore de arquivos e diretórios de um Bounded Context (ADR-031).

    Garante zero código fictício/slop e apenas docstrings arquiteturais e contratos.
    """
    pascal_name = to_pascal_case(name)

    files_content: dict[str, str] = {
        "__init__.py": f'"""Bounded Context apps.{name}."""\n',
        "apps.py": (
            "from django.apps import AppConfig\n\n\n"
            f"class {pascal_name}Config(AppConfig):\n"
            '    default_auto_field = "django.db.models.BigAutoField"\n'
            f'    name = "apps.{name}"\n'
        ),
        "admin.py": (
            f'"""Configurações de administração do Django para apps.{name}."""\n\n'
            "from django.contrib import admin\n\n"
            "# Register your models here.\n"
        ),
        "api/__init__.py": (
            f'"""Roteadores e endpoints HTTP (Django Ninja) para apps.{name}."""\n'
        ),
        "api/routers.py": (
            f'"""Definição de rotas HTTP (Django Ninja) para apps.{name}."""\n\n'
            "from ninja import Router\n\n"
            f'router = Router(tags=["{name}"])\n'
        ),
        "interfaces.py": (
            '"""\n'
            f"Fronteira pública (Interface) do Bounded Context apps.{name} (ADR-031).\n\n"
            "Toda comunicação síncrona transacional originada em outros contextos com este módulo\n"
            "DEVE passar exclusivamente por este arquivo. É estritamente PROIBIDO importar models,\n"
            f"services ou managers de apps.{name} diretamente em outros bounded contexts.\n"
            '"""\n\n'
            "from __future__ import annotations\n\n"
            "__all__: list[str] = []\n"
        ),
        "managers.py": (
            '"""\n'
            f"QuerySets e Managers customizados para apps.{name}.\n\n"
            "Centraliza o isolamento de dados por empresa/tenant e consultas customizadas.\n"
            '"""\n\n'
            "from apps.core.managers import TenantQuerySet\n\n"
            "__all__ = [\n"
            '    "TenantQuerySet",\n'
            "]\n"
        ),
        "models/__init__.py": (
            f'"""Modelos de dados e entidades do Rich Domain Model para apps.{name}."""\n'
        ),
        "schemas/__init__.py": (
            f'"""Schemas Pydantic (Validação Nível 1 - Fail Fast) para apps.{name}."""\n'
        ),
        "selectors/__init__.py": (
            f'"""Query Selectors (Leituras e Projeções puras de dados) para apps.{name}."""\n'
        ),
        "services/__init__.py": (
            f'"""Services (Orquestração de Casos de Uso e Mutações Nível 3) para apps.{name}."""\n'
        ),
        "tasks.py": (
            f'"""Tarefas assíncronas em segundo plano (background tasks) para apps.{name}."""\n'
        ),
        "tests/__init__.py": (
            f'"""Suíte de testes automatizados para apps.{name}."""\n'
        ),
        "tests/factories.py": (
            f'"""Factories do FactoryBoy para geração de fixtures de teste em apps.{name}."""\n'
        ),
        "tests/test_models.py": (
            f'"""Testes de modelos e invariantes de domínio (Nível 2) para apps.{name}."""\n'
        ),
        "tests/test_services.py": (
            f'"""Testes unitários da camada de serviços (Services) para apps.{name}."""\n'
        ),
        "tests/test_selectors.py": (
            f'"""Testes unitários da camada de seletores (Selectors) para apps.{name}."""\n'
        ),
        "tests/test_apis.py": (
            f'"""Testes de integração de rotas e endpoints de API para apps.{name}."""\n'
        ),
        "tests/test_interfaces.py": (
            f'"""Testes de conformidade da fronteira pública (interfaces.py) para apps.{name} (ADR-031)."""\n'
        ),
    }

    for rel_path, code in files_content.items():
        file_path = target_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code, encoding="utf-8")


def create_documentation_stub(docs_dir: Path, name: str) -> Path:
    """Cria o stub de documentação Diátaxis do domínio em docs/architecture/domains/.

    Contém as 5 seções obrigatórias:
    1. Visão Geral
    2. Regras de Negócio
    3. Arquitetura & Interfaces
    4. Contratos & API
    5. Rastreabilidade
    """
    pascal_title = to_pascal_case(name)
    kebab_name = name.replace("_", "-")
    doc_path = docs_dir / f"{kebab_name}-domain.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    content = f"""# Domínio de {pascal_title} (`apps.{name}`)

> **Categoria:** Domínios de Arquitetura (Bounded Contexts)
> **Relacionados:** [Catálogo Canônico de Regras](../business-rules/index.md) · [ADR-016: Multi-Tenancy Pragmático](../adr/016-pragmatic-multi-tenancy.md) · [ADR-030: Rich Domain Model](../adr/030-rich-domain-model-service-layer.md) · [ADR-031: Comunicação Entre Módulos](../adr/031-inter-module-communication.md)

O **Domínio de {pascal_title} (`apps.{name}`)** centraliza a gestão e regras de negócio relacionadas a este contexto operacional.

---

## 1. Visão Geral

Descreva a visão de negócio, os problemas resolvidos pelo contexto e as principais capacidades operacionais disponibilizadas.

### Principais Capacidades
- **Capacidade Operacional:** Descrição da funcionalidade central do módulo.
- **Isolamento Multi-Tenant:** Garantia de segregação de dados no nível de linha por empresa/assessoria (`Company`).

---

## 2. Regras de Negócio

Catálogo canônico de regras e invariantes de domínio específicas deste Bounded Context.

| Código | Nome da Regra | Descrição e Invariante |
| :--- | :--- | :--- |
| `BR-{pascal_title[:3].upper()}-01` | Invariante Principal | Descrição da regra de negócio intrínseca do contexto. |

---

## 3. Arquitetura & Interfaces

Detalhes de isolamento de Bounded Context e comunicação transacional conforme a [ADR-031](../adr/031-inter-module-communication.md).

### Fronteira Pública (`interfaces.py`)
Toda comunicação síncrona com outros módulos deve passar exclusivamente pela fachada em `apps.{name}.interfaces`.

### Dependências
```mermaid
graph TD
    apps_{name}["apps.{name}"] --> apps_core["apps.core"]
    apps_{name} --> apps_tenants["apps.tenants"]
    apps_{name} --> apps_users["apps.users"]
```

---

## 4. Contratos & API

Definição de endpoints HTTP do Django Ninja e contratos de dados.

- **Prefixo de Rota:** `/api/v1/{kebab_name}`
- **Roteador:** `apps.{name}.api.routers.router`
- **Tag Swagger:** `{name}`

---

## 5. Rastreabilidade

Matriz de rastreabilidade entre requisitos, decisões arquiteturais e arquivos do domínio:

| Componente | Caminho Físico | Responsabilidade |
| :--- | :--- | :--- |
| Modelos | `backend/apps/{name}/models/` | Entidades e invariantes de domínio (Nível 2) |
| Serviços | `backend/apps/{name}/services/` | Orquestração de casos de uso e mutações (Nível 3) |
| Seletores | `backend/apps/{name}/selectors/` | Projeções de leitura e otimização de queries |
| API | `backend/apps/{name}/api/` | Controladores HTTP e validação Nível 1 |
| Interface | `backend/apps/{name}/interfaces.py` | Contrato público síncrono para outros Bounded Contexts |
"""

    doc_path.write_text(content, encoding="utf-8")
    return doc_path


def print_registration_reminders(name: str) -> None:
    """Imprime lembretes úteis dos passos manuais pós-criação de módulo."""
    kebab_name = name.replace("_", "-")
    print(f"\n✨ Bounded Context 'apps.{name}' scaffolded com sucesso!")
    print("\nLembretes de registro pós-criação:")
    print("1. Registre o app em 'backend/config/settings/base.py':")
    print("   INSTALLED_APPS = [")
    print("       ...")
    print(f'       "apps.{name}",')
    print("   ]")
    print("\n2. Registre a rota HTTP em 'backend/config/api.py':")
    print(f"   from apps.{name}.api.routers import router as {name}_router")
    print(f'   api.add_router("/{kebab_name}/", {name}_router)')
    print()


def scaffold_module(
    name: str,
    *,
    apps_dir: Path | None = None,
    docs_dir: Path | None = None,
    tach_path: Path | None = None,
) -> Path:
    """Orquestra o scaffold completo de um novo Bounded Context.

    Args:
        name: Nome do módulo em snake_case minúsculo.
        apps_dir: Diretório base onde o módulo será criado (default: backend/apps).
        docs_dir: Diretório de domínios da documentação (default: docs/architecture/domains).
        tach_path: Caminho para o tach.toml (default: backend/tach.toml).

    Returns:
        Path: Caminho do diretório do módulo criado.

    Raises:
        ValueError: Se o nome for inválido.
        FileExistsError: Se o diretório do módulo já existir.
    """
    validate_module_name(name)

    target_apps_dir = apps_dir if apps_dir is not None else DEFAULT_APPS_DIR
    target_docs_dir = docs_dir if docs_dir is not None else DEFAULT_DOCS_DIR
    target_tach_path = tach_path if tach_path is not None else DEFAULT_TACH_PATH

    module_dir = target_apps_dir / name

    if module_dir.exists():
        raise FileExistsError(
            f"O diretório do módulo '{name}' já existe em {module_dir}. "
            "Operação abortada para evitar sobrescrita acidental de código existente."
        )

    # 1. Cria a topologia física completa de Bounded Context
    create_bounded_context_files(module_dir, name)

    # 2. Cria o stub de documentação Diátaxis
    create_documentation_stub(target_docs_dir, name)

    # 3. Registra no tach.toml de forma idempotente
    if target_tach_path.exists():
        update_tach_toml(target_tach_path, name)

    return module_dir


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada para execução via CLI."""
    parser = argparse.ArgumentParser(
        description="Scaffold de novo Bounded Context no Wedding Management (ADR-031)."
    )
    parser.add_argument(
        "module_name",
        type=str,
        help="Nome do módulo em snake_case minúsculo (ex: 'gift_registry', 'guest_book').",
    )
    parser.add_argument(
        "--apps-dir",
        type=Path,
        default=None,
        help="Diretório onde a pasta do módulo será criada (opcional).",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Diretório da documentação Diátaxis para o stub (opcional).",
    )
    parser.add_argument(
        "--tach-path",
        type=Path,
        default=None,
        help="Caminho do arquivo tach.toml (opcional).",
    )

    args = parser.parse_args(argv)

    try:
        scaffold_module(
            args.module_name,
            apps_dir=args.apps_dir,
            docs_dir=args.docs_dir,
            tach_path=args.tach_path,
        )
        print_registration_reminders(args.module_name)
        return 0
    except (ValueError, FileExistsError) as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        return 1
    except (OSError, RuntimeError) as e:
        print(f"💥 Erro operacional durante o scaffold: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

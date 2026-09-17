#!/usr/bin/env python3
"""Script de Sincronização e Validação Automática de Versões nos Documentos.

Este script atua como ponte entre a Fonte Única da Verdade (SSOT) dos manifestos de pacotes:
  - backend/pyproject.toml
  - frontend/package.json
  - landing/package.json

E os pontos visuais da documentação que exibem versões de tecnologias:
  - README.md (Badges)
  - docs/index.md (Tags de cabeçalho e Tabela de Stack Tecnológica)

Utiliza marcadores delimitadores em comentários HTML:
  <!-- sync-versions:<seção>:start -->
  ...
  <!-- sync-versions:<seção>:end -->

Modos de Execução:
  --check: (Padrão no CI) Valida se os blocos delimitados estão sincronizados com os manifestos.
  --write: Atualiza os arquivos Markdown no disco com base nas versões dos manifestos.
"""

import argparse
import difflib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
README_PATH = ROOT_DIR / "README.md"
DOCS_INDEX_PATH = ROOT_DIR / "docs" / "index.md"
BACKEND_TOML_PATH = ROOT_DIR / "backend" / "pyproject.toml"
FRONTEND_PKG_PATH = ROOT_DIR / "frontend" / "package.json"
LANDING_PKG_PATH = ROOT_DIR / "landing" / "package.json"


def _clean_version(ver_str: str) -> str:
    """Limpa prefixos de versionamento (^, ~, >=, =)."""
    return re.sub(r"^[^\d]+", "", ver_str).strip()


def _get_major_minor(clean_ver: str) -> tuple[str, str]:
    """Retorna (major, major.minor) a partir de uma versão semântica."""
    parts = clean_ver.split(".")
    major = parts[0] if parts else "0"
    minor = parts[1] if len(parts) > 1 else "0"
    return major, f"{major}.{minor}"


def extract_manifest_versions(root_dir: Path = ROOT_DIR) -> dict[str, Any]:
    """Extrai as versões das tecnologias a partir dos manifestos de pacotes."""
    backend_toml = root_dir / "backend" / "pyproject.toml"
    frontend_pkg = root_dir / "frontend" / "package.json"
    landing_pkg = root_dir / "landing" / "package.json"

    versions: dict[str, Any] = {}

    # 1. Backend (pyproject.toml)
    with open(backend_toml, "rb") as f:
        pyproject = tomllib.load(f)

    req_python = pyproject.get("project", {}).get("requires-python", ">=3.12")
    versions["python_raw"] = req_python
    py_clean = _clean_version(req_python)
    _, py_major_minor = _get_major_minor(py_clean)
    versions["python_tag"] = f"{py_major_minor}+"
    versions["python_table"] = f"Python {py_major_minor}+"

    deps = pyproject.get("project", {}).get("dependencies", [])
    dev_deps = pyproject.get("dependency-groups", {}).get("dev", [])

    # Django
    django_dep = next(
        (d for d in deps if d.startswith("django>=") or d.startswith("django==")),
        "django>=6.0.8",
    )
    django_match = re.search(r"django>=?([0-9.]+)", django_dep)
    django_ver = django_match.group(1) if django_match else "6.0"
    django_major, django_major_minor = _get_major_minor(django_ver)
    versions["django_badge"] = django_major_minor
    versions["django_tag"] = f"Django {django_major_minor}"
    versions["django_table"] = f"Django {django_major_minor}+"

    # Django Ninja
    ninja_dep = next(
        (d for d in deps if d.startswith("django-ninja>=")), "django-ninja>=1.6.2"
    )
    ninja_match = re.search(r"django-ninja>=?([0-9.]+)", ninja_dep)
    ninja_ver = ninja_match.group(1) if ninja_match else "1.6"
    _, ninja_major_minor = _get_major_minor(ninja_ver)
    versions["ninja_badge"] = f"{ninja_major_minor}+"
    versions["ninja_tag"] = f"Django Ninja {ninja_major_minor}+"
    versions["ninja_table"] = f"Ninja {ninja_major_minor}+"

    # Pytest
    pytest_dep = next(
        (d for d in dev_deps if d.startswith("pytest>=")), "pytest>=9.1.1"
    )
    pytest_match = re.search(r"pytest>=?([0-9.]+)", pytest_dep)
    pytest_ver = pytest_match.group(1) if pytest_match else "9.1"
    _, pytest_major_minor = _get_major_minor(pytest_ver)
    versions["pytest_table"] = f"Pytest {pytest_major_minor}+"

    # 2. Frontend (frontend/package.json)
    with open(frontend_pkg, "r", encoding="utf-8") as f:
        front = json.load(f)

    front_deps = front.get("dependencies", {})
    front_dev_deps = front.get("devDependencies", {})

    # React
    react_raw = front_deps.get("react", "^19.2.8")
    react_clean = _clean_version(react_raw)
    react_major, react_major_minor = _get_major_minor(react_clean)
    versions["react_badge"] = react_major
    versions["react_tag"] = f"React {react_major}"
    versions["react_table"] = f"React {react_major_minor}+"

    # Tailwind CSS
    tailwind_raw = front_dev_deps.get(
        "tailwindcss", front_deps.get("tailwindcss", "^4.3.3")
    )
    tailwind_clean = _clean_version(tailwind_raw)
    tailwind_major, tailwind_major_minor = _get_major_minor(tailwind_clean)
    versions["tailwind_badge"] = f"v{tailwind_major}"
    versions["tailwind_tag"] = f"Tailwind CSS v{tailwind_major}"
    versions["tailwind_table"] = f"Tailwind {tailwind_major_minor}+"

    # Vite
    vite_raw = front_dev_deps.get("vite", "^8.2.1")
    _, vite_major_minor = _get_major_minor(_clean_version(vite_raw))
    versions["vite_table"] = f"Vite {vite_major_minor}+"

    # TypeScript
    ts_raw = front_dev_deps.get("typescript", "^7.0.2")
    _, ts_major_minor = _get_major_minor(_clean_version(ts_raw))
    versions["ts_table"] = f"TS {ts_major_minor}+"

    # Orval
    orval_raw = front_dev_deps.get("orval", "^8.24.0")
    _, orval_major_minor = _get_major_minor(_clean_version(orval_raw))
    versions["orval_table"] = f"Orval {orval_major_minor}+"

    # Zod
    zod_raw = front_deps.get("zod", "^4.4.3")
    _, zod_major_minor = _get_major_minor(_clean_version(zod_raw))
    versions["zod_table"] = f"Zod {zod_major_minor}+"

    # Vitest
    vitest_raw = front_dev_deps.get("vitest", "^4.0.18")
    _, vitest_major_minor = _get_major_minor(_clean_version(vitest_raw))
    versions["vitest_table"] = f"Vitest {vitest_major_minor}+"

    # Playwright
    playwright_raw = front_dev_deps.get("@playwright/test", "^1.62.1")
    _, playwright_major_minor = _get_major_minor(_clean_version(playwright_raw))
    versions["playwright_table"] = f"Playwright {playwright_major_minor}+"

    # 3. Landing (landing/package.json)
    with open(landing_pkg, "r", encoding="utf-8") as f:
        landing = json.load(f)

    landing_dev = landing.get("devDependencies", {})
    astro_raw = landing_dev.get("astro", "7.1.1")
    astro_clean = _clean_version(astro_raw)
    astro_major, astro_major_minor = _get_major_minor(astro_clean)
    versions["astro_badge"] = astro_major_minor
    versions["astro_tag"] = f"Astro {astro_major}"
    versions["astro_table"] = f"Astro {astro_major_minor}+"

    return versions


def render_readme_badges(v: dict[str, Any]) -> str:
    """Renderiza os badges centrais para o README.md."""
    return f"""  <img src="https://img.shields.io/badge/python-{v["python_tag"]}-3776AB?logo=python&logoColor=white&style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/django-{v["django_badge"]}-092E20?logo=django&logoColor=white&style=flat-square" alt="Django">
  <img src="https://img.shields.io/badge/django--ninja-{v["ninja_badge"]}-087EA4?style=flat-square" alt="Django Ninja">
  <img src="https://img.shields.io/badge/react-{v["react_badge"]}-61DAFB?logo=react&logoColor=black&style=flat-square" alt="React {v["react_badge"]}">
  <img src="https://img.shields.io/badge/astro-{v["astro_badge"]}-FF5D01?logo=astro&logoColor=white&style=flat-square" alt="Astro {v["astro_badge"]}">
  <img src="https://img.shields.io/badge/tailwind-{v["tailwind_badge"]}-38B2AC?logo=tailwindcss&logoColor=white&style=flat-square" alt="{v["tailwind_tag"]}">
  <img src="https://img.shields.io/badge/postgresql-neon-00E599?logo=postgresql&logoColor=black&style=flat-square" alt="Neon DB">
  <img src="https://img.shields.io/badge/storage-cloudflare--r2-F38020?logo=cloudflare&logoColor=white&style=flat-square" alt="Cloudflare R2">
  <img src="https://img.shields.io/badge/iac-terraform-7B42BC?logo=terraform&logoColor=white&style=flat-square" alt="Terraform">
  <img src="https://img.shields.io/badge/e2e-playwright-2EAD33?logo=playwright&logoColor=white&style=flat-square" alt="Playwright">"""


def render_docs_tags(v: dict[str, Any]) -> str:
    """Renderiza as tags de cabeçalho para o docs/index.md."""
    return f"""  <span class="md-tag" style="background-color: #3776AB; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Python {v["python_tag"]}</span>
  <span class="md-tag" style="background-color: #092E20; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">{v["django_tag"]}</span>
  <span class="md-tag" style="background-color: #087EA4; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">{v["ninja_tag"]}</span>
  <span class="md-tag" style="background-color: #61DAFB; color: #09090B; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">{v["react_tag"]}</span>
  <span class="md-tag" style="background-color: #FF5D01; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">{v["astro_tag"]}</span>
  <span class="md-tag" style="background-color: #38B2AC; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">{v["tailwind_tag"]}</span>
  <span class="md-tag" style="background-color: #00E599; color: #09090B; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">PostgreSQL Neon</span>
  <span class="md-tag" style="background-color: #F38020; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Cloudflare R2</span>
  <span class="md-tag" style="background-color: #7B42BC; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Terraform IaC</span>
  <span class="md-tag" style="background-color: #2EAD33; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Playwright E2E</span>"""


def render_docs_table(v: dict[str, Any]) -> str:
    """Renderiza a tabela de stack tecnológica para o docs/index.md."""
    return f"""| Camada | Tecnologia Principal | Versão Exata | Papel & Responsabilidade |
| :--- | :--- | :--- | :--- |
| **Landing Page Comercial** | Astro, Tailwind CSS v4, React 19 | `{v["astro_table"]}`, `{v["tailwind_table"]}`, `{v["react_table"]}` | Portal institucional público de alta conversão, renderização estática (SSG) e SEO. |
| **Frontend SPA** | React 19, TypeScript, Tailwind CSS v4, shadcn/ui | `{v["react_table"]}`, `{v["vite_table"]}`, `{v["ts_table"]}` | Interface do usuário rica e autenticada para cerimonialistas e casais. |
| **Camada de Contratos** | Django Ninja, OpenAPI 3.1, Orval, Zod | `{v["ninja_table"]}`, `{v["orval_table"]}`, `{v["zod_table"]}` | Sincronização automática e tipagem estrita de ponta a ponta sem clientes manuais. |
| **Backend & APIs** | Python, Django, Django Ninja, Pydantic v2 | `{v["python_table"]}`, `{v["django_table"]}`, `{v["ninja_table"]}` | Roteamento performático, validação de payload, autenticação JWT e serialização. |
| **Lógica & Domínio** | Rich Domain Model ([ADR-030](architecture/adr/030-rich-domain-model-service-layer.md)), Service Layer, `TenantQuerySet` | Padrão CQRS & Use Cases | Validação em 3 níveis (Pydantic, Model, Service), tolerância zero e isolamento multi-tenant. |
| **Persistência de Dados** | Neon Serverless PostgreSQL | `psycopg 3.3+` | Banco relacional escalável com isolamento lógico estrito por empresa (`company_id`). |
| **Armazenamento de Arquivos** | Cloudflare R2 (S3-Compatible) | `django-storages 1.14+`, `boto3 1.43+` | Armazenamento de PDFs contratuais via Presigned URLs com custo de egresso zero. |
| **Tarefas & Workers** | Huey, Redis/Valkey, Cloud Scheduler | `huey 2.5+`, `redis 5.0+` | Execução de rotinas assíncronas em segundo plano e cron tasks via OIDC. |
| **Infraestrutura como Código** | Terraform, Google Cloud Run, Cloud Scheduler | `Terraform 1.10+` | Provisionamento declarativo serverless e esteiras de automação GitOps. |
| **Qualidade & Testes** | Pytest, Vitest, Playwright E2E, Ruff, Mypy, Oxlint | `{v["pytest_table"]}`, `{v["vitest_table"]}`, `{v["playwright_table"]}` | Pirâmide completa de testes (unitários, integração, E2E) e linters rigorosos. |"""


def process_markers(
    file_path: Path,
    marker_name: str,
    expected_content: str,
    write: bool,
) -> tuple[bool, str]:
    """Valida ou substitui o conteúdo entre marcadores semânticos no arquivo."""
    if not file_path.exists():
        return False, f"Arquivo não encontrado: {file_path}"

    original_text = file_path.read_text(encoding="utf-8")
    start_tag = f"<!-- sync-versions:{marker_name}:start -->"
    end_tag = f"<!-- sync-versions:{marker_name}:end -->"

    pattern = re.compile(
        rf"({re.escape(start_tag)}\n)(.*?)(\n[ \t]*{re.escape(end_tag)})",
        re.DOTALL,
    )

    match = pattern.search(original_text)
    if not match:
        return (
            False,
            f"[{file_path.name}] Marcador não encontrado: '{start_tag}' e '{end_tag}' ausentes no documento.",
        )

    current_inner = match.group(2)
    # Compara normalizando quebras de linha
    if current_inner.strip() == expected_content.strip():
        return True, f"[{file_path.name}:{marker_name}] Perfeitamente sincronizado."

    if write:
        new_text = pattern.sub(rf"\g<1>{expected_content}\g<3>", original_text)
        file_path.write_text(new_text, encoding="utf-8")
        return True, f"[{file_path.name}:{marker_name}] Atualizado com sucesso."

    # Gerar diff descritivo
    diff = difflib.unified_diff(
        current_inner.strip().splitlines(keepends=True),
        expected_content.strip().splitlines(keepends=True),
        fromfile=f"{file_path.name} (atual)",
        tofile=f"{file_path.name} (manifesto)",
    )
    diff_text = "".join(diff)
    return (
        False,
        f"[{file_path.name}:{marker_name}] Version drift detectado! Execute 'just sync-docs' para corrigir.\n{diff_text}",
    )


def sync_all(write: bool = False) -> int:
    """Executa a sincronização ou validação de todas as seções mapeadas."""
    try:
        versions = extract_manifest_versions()
    except Exception as e:
        print(f"❌ Erro ao ler manifestos de pacotes: {e}", file=sys.stderr)
        return 1

    tasks = [
        (README_PATH, "badges", render_readme_badges(versions)),
        (DOCS_INDEX_PATH, "tags", render_docs_tags(versions)),
        (DOCS_INDEX_PATH, "table", render_docs_table(versions)),
    ]

    all_passed = True
    action = "Sincronizando" if write else "Validando"
    print(f"🔍 {action} versões de pacotes contra a documentação técnica...\n")

    for file_path, marker_name, expected in tasks:
        success, message = process_markers(
            file_path, marker_name, expected, write=write
        )
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}\n")
            all_passed = False

    if not all_passed:
        if not write:
            print(
                "\n🚨 Falha na validação de versões! A documentação possui tags desatualizadas em relação aos manifestos."
            )
            print(
                "👉 Execute 'just sync-docs' para atualizar automaticamente os arquivos."
            )
        return 1

    print(
        "\n✨ Todas as versões da documentação estão 100% sincronizadas com os manifestos."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sincroniza e valida versões de pacotes em relação à documentação técnica."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_true",
        default=True,
        help="Apenas valida se as versões estão sincronizadas (código 1 se houver drift). Padrão.",
    )
    group.add_argument(
        "--write",
        action="store_true",
        help="Sobrescreve os arquivos Markdown com as versões atuais dos manifestos.",
    )

    args = parser.parse_args(argv)
    is_write = args.write
    return sync_all(write=is_write)


if __name__ == "__main__":
    sys.exit(main())

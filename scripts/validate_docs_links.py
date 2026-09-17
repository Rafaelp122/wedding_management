#!/usr/bin/env python3
"""
Script de Validação Automática de Links da Documentação.
Varre todos os arquivos Markdown na pasta docs/ e nas skills do projeto (.agents/skills/wedding-*/) e verifica:
1. Se não sobraram Wikilinks ([[nota]]) fora de blocos de código.
2. Se não existem links de máquinas locais (file:// ou file:///home/).
3. Se todos os links Markdown relativos ([rotulo](destino.md)) apontam para arquivos existentes.
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
SKILLS_DIR = BASE_DIR / ".agents" / "skills"

# Regex para capturar blocos de código (fenced ```...``` e inline `...`)
CODE_BLOCK_PATTERN = re.compile(r"(```[\s\S]*?```)|(`[^`\n]+`)")

# Regex para capturar links markdown: [label](url)
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Regex para capturar wikilinks residuais: [[target]]
WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


def remove_code_blocks(text: str) -> str:
    """Substitui blocos de código por espaços para não analisar links dentro deles."""
    return CODE_BLOCK_PATTERN.sub(lambda m: " " * len(m.group(0)), text)


def audit_markdown_file(path: Path, errors: list) -> int:
    """Audita um arquivo markdown individual e retorna a contagem de links checados."""
    links_checked = 0
    content = path.read_text(encoding="utf-8")
    clean_content = remove_code_blocks(content)

    rel_file_path = path.relative_to(BASE_DIR)

    # 1. Verificar se restaram Wikilinks [[...]]
    wikilinks = WIKILINK_PATTERN.findall(clean_content)
    if wikilinks:
        for wl in wikilinks:
            errors.append(
                f"❌ [{rel_file_path}] Wikilink residual não convertido: [[{wl}]]"
            )

    # 2. Verificar links Markdown [label](target)
    for match in MARKDOWN_LINK_PATTERN.finditer(clean_content):
        label, target = match.groups()
        target = target.strip()

        # Rejeitar links de máquina local (file://)
        if target.startswith("file://"):
            errors.append(
                f"❌ [{rel_file_path}] Link de máquina local proibido: '[{label}]({target})' — Use caminhos relativos."
            )
            continue

        # Ignorar links externos ou links de âncora pura
        if (
            target.startswith("http://")
            or target.startswith("https://")
            or target.startswith("mailto:")
            or target.startswith("tel:")
            or target.startswith("#")
        ):
            continue

        links_checked += 1

        # Remover fragmentos de âncora (#linha ou #secao)
        clean_target = target.split("#")[0]
        if not clean_target:
            continue

        # Resolver caminho relativo ao arquivo atual
        target_path = (path.parent / clean_target).resolve()

        if not target_path.exists():
            errors.append(
                f"❌ [{rel_file_path}] Link quebrado: '[{label}]({target})' -> Arquivo não encontrado: '{clean_target}'"
            )

    return links_checked


def audit_python_files_for_doc_links(
    backend_dir: Path, errors: list
) -> tuple[int, int]:
    """Audita referências para a documentação em docstrings e comentários do código Python."""
    py_files_checked = 0
    py_links_checked = 0
    doc_link_pattern = re.compile(r"docs/[a-zA-Z0-9_\-./]+\.md")

    for py_file in sorted(backend_dir.rglob("*.py")):
        if any(
            ignored in py_file.parts
            for ignored in (".venv", "__pycache__", ".pytest_cache")
        ):
            continue

        py_files_checked += 1
        content = py_file.read_text(encoding="utf-8")
        rel_path = py_file.relative_to(BASE_DIR)

        for match in doc_link_pattern.finditer(content):
            doc_ref = match.group(0)
            py_links_checked += 1
            target_path = BASE_DIR / doc_ref

            if not target_path.exists():
                errors.append(
                    f"❌ [{rel_path}] Link quebrado no código Python: '{doc_ref}' -> Arquivo Markdown não encontrado."
                )

    return py_files_checked, py_links_checked


def main():
    print(
        "🔍 Iniciando validação automática de links da documentação, skills e código...\n"
    )

    files_checked = 0
    links_checked = 0
    errors = []

    # 1. Arquivos Markdown na raiz do repositório (README.md, AGENTS.md, DESIGN.md)
    target_files = sorted(BASE_DIR.glob("*.md"))

    # 2. Documentação sob docs/
    target_files.extend(sorted(DOCS_DIR.glob("**/*.md")))

    # 3. Skills dos agentes
    if SKILLS_DIR.exists():
        for skill_dir in sorted(SKILLS_DIR.glob("wedding-*")):
            target_files.extend(sorted(skill_dir.glob("**/*.md")))

    for path in target_files:
        files_checked += 1
        links_checked += audit_markdown_file(path, errors)

    # 4. Auditoria Bidirecional no Código Python (Code -> Docs)
    backend_dir = BASE_DIR / "backend"
    py_files_count = 0
    py_links_count = 0
    if backend_dir.exists():
        py_files_count, py_links_count = audit_python_files_for_doc_links(
            backend_dir, errors
        )

    print("📊 Resumo da Validação:")
    print(f"   - Arquivos Markdown auditados: {files_checked}")
    print(f"   - Links Markdown verificados:  {links_checked}")
    print(f"   - Arquivos Python inspecionados: {py_files_count}")
    print(f"   - Referências Code -> Docs verificadas: {py_links_count}")

    if errors:
        print(
            f"\n🚨 Foram encontrados {len(errors)} erro(s) de link na documentação ou código:\n"
        )
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print(
            "\n✨ Todos os links da documentação, skills e código estão 100% válidos!"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()

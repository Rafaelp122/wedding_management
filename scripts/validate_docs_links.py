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


def main():
    print("🔍 Iniciando validação automática de links da documentação e skills...\n")

    files_checked = 0
    links_checked = 0
    errors = []

    target_files = sorted(DOCS_DIR.glob("**/*.md"))
    if SKILLS_DIR.exists():
        for skill_dir in sorted(SKILLS_DIR.glob("wedding-*")):
            target_files.extend(sorted(skill_dir.glob("**/*.md")))

    for path in target_files:
        files_checked += 1
        links_checked += audit_markdown_file(path, errors)

    print("📊 Resumo da Validação:")
    print(f"   - Arquivos auditados: {files_checked}")
    print(f"   - Links verificados:  {links_checked}")

    if errors:
        print(
            f"\n🚨 Foram encontrados {len(errors)} erro(s) de link na documentação:\n"
        )
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print(
            "\n✨ Todos os links da documentação e skills estão válidos e os arquivos alvo existem!"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()

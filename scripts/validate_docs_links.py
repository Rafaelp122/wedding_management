#!/usr/bin/env python3
"""
Script de Validação Automática de Links da Documentação.
Varre todos os arquivos Markdown na pasta docs/ e verifica:
1. Se não sobraram Wikilinks ([[nota]]) fora de blocos de código.
2. Se todos os links Markdown relativos ([rotulo](destino.md)) apontam para arquivos existentes.
"""

import sys
import re
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# Regex para capturar blocos de código (fenced ```...``` e inline `...`)
CODE_BLOCK_PATTERN = re.compile(r"(```[\s\S]*?```)|(`[^`\n]+`)")

# Regex para capturar links markdown: [label](url)
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Regex para capturar wikilinks residuais: [[target]]
WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


def remove_code_blocks(text: str) -> str:
    """Substitui blocos de código por espaços para não analisar links dentro deles."""
    return CODE_BLOCK_PATTERN.sub(lambda m: " " * len(m.group(0)), text)


def main():
    print("🔍 Iniciando validação automática de links da documentação...\n")

    files_checked = 0
    links_checked = 0
    errors = []

    for path in sorted(DOCS_DIR.glob("**/*.md")):
        files_checked += 1
        content = path.read_text(encoding="utf-8")
        clean_content = remove_code_blocks(content)

        rel_file_path = path.relative_to(DOCS_DIR)

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

            # Ignorar links externos ou links de âncora pura
            if (
                target.startswith("http://")
                or target.startswith("https://")
                or target.startswith("mailto:")
                or target.startswith("tel:")
                or target.startswith("#")
                or target.startswith("file://")
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
            "\n✨ Todos os links da documentação estão válidos e os arquivos alvo existem!"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Script de Validação e Auditoria de Snippets de Código na Documentação.

Este script garante a integridade contínua e o desacoplamento entre o código e a documentação:
1. Valida se todas as transclusões de código PyMdown (`--8<-- "path/to/file:..."`) apontam para arquivos reais.
2. Rejeita ativamente faixas numéricas rígidas (`:start:end`), conforme ADR-028 e ADR-030.
3. Valida se as tags semânticas delimitadoras `# --8<-- [start:tag]` e `# --8<-- [end:tag]` existem nos arquivos de origem.
4. Falha com código de saída 1 se qualquer inconsistência for encontrada, protegendo o CI/CD contra code-drift.
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"

# Regex para transclusões de snippets PyMdown: --8<-- "caminho/do/arquivo:tag_ou_linhas"
SNIPPET_REGEX = re.compile(r'--8<--\s*["\']([^"\']+)["\']')


def validate_snippets() -> list[str]:
    """Valida todas as transclusões de snippets no MkDocs."""
    errors = []
    snippet_count = 0
    line_based_count = 0
    tag_based_count = 0
    whole_file_count = 0

    for md_file in DOCS_DIR.rglob("*.md"):
        if "superpowers" in md_file.parts:
            continue

        content = md_file.read_text(encoding="utf-8")
        rel_path = md_file.relative_to(ROOT_DIR)

        matches = SNIPPET_REGEX.findall(content)
        for match in matches:
            snippet_count += 1
            parts = match.split(":")
            target_path_str = parts[0]
            target_path = ROOT_DIR / target_path_str

            if not target_path.exists():
                # Tentar relativo a docs/
                target_path = DOCS_DIR / target_path_str

            if not target_path.exists():
                errors.append(
                    f"[{rel_path}] Snippet inexistente: '{target_path_str}' não foi encontrado no repositório."
                )
                continue

            # 1. Proibição de faixas numéricas de linha (:start:end)
            if len(parts) > 1 and parts[1].isdigit():
                line_based_count += 1
                errors.append(
                    f"[{rel_path}] Transclusão por faixa numérica proibida: '{match}'. "
                    f"Conforme ADR-028 e ADR-030 (§ 2.3), faixas numéricas de linha geram code-drift frágil. "
                    f"Substitua por links canônicos para classes/métodos ou use tags semânticas (# --8<-- [start:tag])."
                )
                continue

            # 2. Validação de tags semânticas (ex: "file.py:tag_name")
            if len(parts) > 1:
                tag_name = parts[1]
                tag_based_count += 1
                target_content = target_path.read_text(encoding="utf-8")
                start_tag = f"[start:{tag_name}]"
                end_tag = f"[end:{tag_name}]"

                if start_tag not in target_content or end_tag not in target_content:
                    errors.append(
                        f"[{rel_path}] Tag de snippet inválida '{tag_name}' no arquivo '{target_path_str}'. "
                        f"Certifique-se de delimitar o bloco com '# --8<-- [{start_tag}]' e '# --8<-- [{end_tag}]'."
                    )
            else:
                whole_file_count += 1

    print(f"   - Snippets PyMdown verificados: {snippet_count}")
    print(f"     • Tags semânticas válidas: {tag_based_count}")
    print(f"     • Arquivos inteiros: {whole_file_count}")
    if line_based_count > 0:
        print(f"     • Faixas numéricas proibidas: {line_based_count}")
    return errors


def main() -> int:
    print(
        "🔍 Iniciando auditoria de sincronização de código na documentação (Code-Drift Guardian)..."
    )
    errors = validate_snippets()

    if errors:
        print("\n❌ ERROS DE SINCRONIZAÇÃO DE CÓDIGO ENCONTRADOS:")
        for err in errors:
            print(f"   🚨 {err}")
        print(
            "\n💡 O build falhou para evitar documentação defasada ou acoplada a números de linha."
        )
        return 1

    print("✨ Todos os snippets e referências de código estão 100% sincronizados!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Testes unitários e de integração para sincronização de versões.

Garante que:
1. As versões canônicas são extraídas dos manifestos pyproject.toml e package.json.
2. A detecção de drift funciona (fail-fast com diff claro) quando há divergência.
3. A substituição controlada (write mode) atualiza apenas o miolo delimitado.
4. Os arquivos README.md e docs/index.md estão 100% sincronizados.
"""

import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# isort: split
from scripts.sync_doc_versions import (  # noqa: E402
    extract_manifest_versions,
    process_markers,
    sync_all,
)


@pytest.mark.unit
class TestDocVersionSyncUnit:
    """Testes unitários de extração e manipulação de marcadores semânticos."""

    def test_extract_manifest_versions_contains_all_keys(self) -> None:
        """Valida se todas as chaves de versão esperadas são extraídas com sucesso."""
        versions = extract_manifest_versions()

        expected_keys = [
            "python_tag",
            "django_badge",
            "django_tag",
            "django_table",
            "ninja_badge",
            "ninja_tag",
            "ninja_table",
            "pytest_table",
            "react_badge",
            "react_tag",
            "react_table",
            "tailwind_badge",
            "tailwind_tag",
            "tailwind_table",
            "vite_table",
            "ts_table",
            "orval_table",
            "zod_table",
            "vitest_table",
            "playwright_table",
            "astro_badge",
            "astro_tag",
            "astro_table",
        ]

        for key in expected_keys:
            assert key in versions, (
                f"Chave '{key}' não encontrada nas versões extraídas."
            )
            assert str(versions[key]).strip() != "", f"Chave '{key}' está vazia."

    def test_process_markers_detects_match(self, tmp_path: Path) -> None:
        """Garante que conteúdo idêntico retorna sucesso e não altera o arquivo."""
        doc = tmp_path / "test.md"
        doc.write_text(
            "Header\n"
            "<!-- sync-versions:test:start -->\n"
            "conteúdo esperado\n"
            "<!-- sync-versions:test:end -->\n"
            "Footer",
            encoding="utf-8",
        )

        success, msg = process_markers(doc, "test", "conteúdo esperado", write=False)
        assert success is True
        assert "Perfeitamente sincronizado" in msg

    def test_process_markers_detects_drift_in_check_mode(self, tmp_path: Path) -> None:
        """Garante que drift de versão é detectado no modo check com diff detalhado."""
        doc = tmp_path / "test.md"
        doc.write_text(
            "Header\n"
            "<!-- sync-versions:test:start -->\n"
            "versao antiga\n"
            "<!-- sync-versions:test:end -->\n"
            "Footer",
            encoding="utf-8",
        )

        success, msg = process_markers(doc, "test", "versao nova", write=False)
        assert success is False
        assert "Version drift detectado" in msg
        assert "-versao antiga" in msg
        assert "+versao nova" in msg

    def test_process_markers_updates_content_in_write_mode(
        self, tmp_path: Path
    ) -> None:
        """Garante que o modo write atualiza exatamente o bloco delimitado."""
        doc = tmp_path / "test.md"
        doc.write_text(
            "Header\n"
            "<!-- sync-versions:test:start -->\n"
            "versao antiga\n"
            "<!-- sync-versions:test:end -->\n"
            "Footer",
            encoding="utf-8",
        )

        success, msg = process_markers(doc, "test", "versao nova", write=True)
        assert success is True
        assert "Atualizado com sucesso" in msg

        updated = doc.read_text(encoding="utf-8")
        assert "versao nova" in updated
        assert "versao antiga" not in updated
        assert "Header" in updated
        assert "Footer" in updated

    def test_process_markers_fails_when_markers_missing(self, tmp_path: Path) -> None:
        """Garante que ausência de marcadores semânticos é reportada como erro."""
        doc = tmp_path / "test.md"
        doc.write_text("Header sem marcadores", encoding="utf-8")

        success, msg = process_markers(doc, "test", "conteúdo", write=False)
        assert success is False
        assert "Marcador não encontrado" in msg


@pytest.mark.integration
class TestDocVersionSyncIntegration:
    """Testes de integração com os arquivos reais do repositório."""

    def test_repository_documentation_is_in_sync(self) -> None:
        """Verifica se a documentação está em paridade com os manifestos."""
        exit_code = sync_all(write=False)
        assert exit_code == 0, (
            "A documentação do repositório está desalinhada em relação aos manifestos. "
            "Execute 'just sync-docs' para sincronizar."
        )

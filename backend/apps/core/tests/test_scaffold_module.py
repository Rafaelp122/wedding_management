"""Testes unitários para o script de scaffold de Bounded Contexts (scripts/scaffold_module.py).

Valida:
1. Validação de nomes em snake_case estrito (rejeição de maiúsculas, hifens, números iniciais).
2. Bloqueio estrito de palavras reservadas do Python e nomes do sistema/arquitetura.
3. Criação da árvore física completa de arquivos e docstrings sem código slop/fictício.
4. Proteção contra sobrescrita (FileExistsError) se o diretório do módulo já existir.
5. Injeção estritamente idempotente de dependências e interfaces no tach.toml.
"""

from __future__ import annotations

import shutil
import sys
import tomllib
from pathlib import Path

import pytest


# Adiciona a raiz do projeto ao sys.path para importação do script CLI
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# isort: split
from scripts.scaffold_module import (  # type: ignore[import-not-found]  # noqa: E402
    create_bounded_context_files,
    create_documentation_stub,
    scaffold_module,
    to_pascal_case,
    update_tach_toml,
    validate_module_name,
)


@pytest.mark.unit
class TestModuleNameValidation:
    """Testes para regras de validação sintática e semântica de nomes de módulos."""

    @pytest.mark.parametrize(
        "valid_name",
        [
            "guest_book",
            "catalog",
            "wedding_vows",
            "gift_registry",
            "a",
            "foo_bar_123",
            "module_v2",
        ],
    )
    def test_validate_module_name_valid(self, valid_name: str) -> None:
        """Nomes válidos em snake_case iniciado por letra devem passar sem exceções."""
        validate_module_name(valid_name)

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "GuestBook",
            "guest-book",
            "123guest",
            "_internal",
            "guest book",
            "guest.book",
            "",
            "wedding-vows",
            "Logistics",
        ],
    )
    def test_validate_module_name_invalid_pattern(self, invalid_name: str) -> None:
        """Nomes com maiúsculas, hifens, espaços ou números iniciais devem ser rejeitados."""
        with pytest.raises(ValueError, match="estritamente em snake_case"):
            validate_module_name(invalid_name)

    @pytest.mark.parametrize(
        "reserved_keyword",
        [
            "def",
            "class",
            "import",
            "return",
            "try",
            "for",
            "while",
            "pass",
            "lambda",
            "async",
            "await",
        ],
    )
    def test_validate_module_name_python_keywords(self, reserved_keyword: str) -> None:
        """Palavras reservadas da linguagem Python devem ser bloqueadas."""
        with pytest.raises(ValueError, match="palavra reservada do Python"):
            validate_module_name(reserved_keyword)

    @pytest.mark.parametrize(
        "system_name",
        [
            "core",
            "config",
            "admin",
            "api",
            "apps",
            "tests",
            "settings",
            "manage",
        ],
    )
    def test_validate_module_name_system_reserved(self, system_name: str) -> None:
        """Nomes estruturais do sistema e framework devem ser rejeitados."""
        with pytest.raises(ValueError, match="nome reservado pelo sistema"):
            validate_module_name(system_name)

    def test_to_pascal_case_conversion(self) -> None:
        """Valida a conversão de snake_case para PascalCase para AppConfig."""
        assert to_pascal_case("guest_book") == "GuestBook"
        assert to_pascal_case("suppliers") == "Suppliers"
        assert to_pascal_case("wedding_vows_service") == "WeddingVowsService"


@pytest.mark.unit
class TestScaffoldModuleFileTree:
    """Testes para a criação física dos arquivos de Bounded Context (ADR-031)."""

    EXPECTED_FILES = [
        "__init__.py",
        "apps.py",
        "admin.py",
        "api/__init__.py",
        "api/routers.py",
        "interfaces.py",
        "managers.py",
        "models/__init__.py",
        "schemas/__init__.py",
        "selectors/__init__.py",
        "services/__init__.py",
        "tasks.py",
        "tests/__init__.py",
        "tests/factories.py",
        "tests/test_models.py",
        "tests/test_services.py",
        "tests/test_selectors.py",
        "tests/test_apis.py",
        "tests/test_interfaces.py",
    ]

    def test_create_bounded_context_files_structure(self, tmp_path: Path) -> None:
        """Valida se todos os 19 arquivos e diretórios canônicos são gerados sem código slop."""
        target_dir = tmp_path / "guest_registry"
        target_dir.mkdir(parents=True)

        create_bounded_context_files(target_dir, "guest_registry")

        for expected_rel_path in self.EXPECTED_FILES:
            file_path = target_dir / expected_rel_path
            assert file_path.exists(), (
                f"Arquivo esperado não foi criado: {expected_rel_path}"
            )
            assert file_path.is_file(), f"Deveria ser um arquivo: {expected_rel_path}"

        # Valida conteúdo de apps.py
        apps_code = (target_dir / "apps.py").read_text(encoding="utf-8")
        assert "class GuestRegistryConfig(AppConfig):" in apps_code
        assert 'name = "apps.guest_registry"' in apps_code

        # Valida conteúdo de api/routers.py
        routers_code = (target_dir / "api" / "routers.py").read_text(encoding="utf-8")
        assert 'router = Router(tags=["guest_registry"])' in routers_code

        # Valida conteúdo de interfaces.py (Fronteira pública ADR-031)
        interfaces_code = (target_dir / "interfaces.py").read_text(encoding="utf-8")
        assert "ADR-031" in interfaces_code
        assert "Fronteira pública" in interfaces_code

        # Valida conteúdo de managers.py (import de TenantQuerySet de apps.core.managers)
        managers_code = (target_dir / "managers.py").read_text(encoding="utf-8")
        assert "from apps.core.managers import TenantQuerySet" in managers_code

        # Valida que não há entidades fictícias ('Item', 'dummy', etc.)
        models_code = (target_dir / "models" / "__init__.py").read_text(
            encoding="utf-8"
        )
        assert "class Item" not in models_code
        assert "def " not in models_code

        services_code = (target_dir / "services" / "__init__.py").read_text(
            encoding="utf-8"
        )
        assert "class " not in services_code

    def test_create_documentation_stub_structure(self, tmp_path: Path) -> None:
        """Valida que o stub Diátaxis contém as 5 seções obrigatórias."""
        docs_dir = tmp_path / "domains"
        doc_file = create_documentation_stub(docs_dir, "guest_registry")

        assert doc_file.exists()
        assert doc_file.name == "guest-registry-domain.md"

        content = doc_file.read_text(encoding="utf-8")
        assert "# Domínio de GuestRegistry (`apps.guest_registry`)" in content
        assert "## 1. Visão Geral" in content
        assert "## 2. Regras de Negócio" in content
        assert "## 3. Arquitetura & Interfaces" in content
        assert "## 4. Contratos & API" in content
        assert "## 5. Rastreabilidade" in content


@pytest.mark.unit
class TestScaffoldModuleIntegration:
    """Testes de fluxo completo de execução e proteções de integridade."""

    def test_scaffold_module_full_flow(self, tmp_path: Path) -> None:
        """Executa scaffold_module em ambiente temporário e checa árvore e tach.toml."""
        apps_dir = tmp_path / "backend" / "apps"
        docs_dir = tmp_path / "docs" / "architecture" / "domains"
        tach_file = tmp_path / "backend" / "tach.toml"
        tach_file.parent.mkdir(parents=True)
        tach_file.write_text(
            '[[modules]]\npath = "apps.core"\ndepends_on = []\n\n'
            '[[modules]]\npath = "config"\ndepends_on = [\n    { path = "apps.core" },\n]\n\n'
            '[[interfaces]]\nfrom = ["apps.core"]\nexpose = ["*"]\n',
            encoding="utf-8",
        )

        mod_dir = scaffold_module(
            "gift_registry",
            apps_dir=apps_dir,
            docs_dir=docs_dir,
            tach_path=tach_file,
        )

        assert mod_dir.exists()
        assert (mod_dir / "apps.py").exists()
        assert (docs_dir / "gift-registry-domain.md").exists()

        # Verifica injeção no tach.toml temporário
        parsed_tach = tomllib.loads(tach_file.read_text(encoding="utf-8"))
        module_paths = [m["path"] for m in parsed_tach["modules"]]
        assert "apps.gift_registry" in module_paths

        config_mod = next(m for m in parsed_tach["modules"] if m["path"] == "config")
        config_deps = [d["path"] for d in config_mod["depends_on"]]
        assert "apps.gift_registry" in config_deps

        interface_sources = [
            source
            for iface in parsed_tach["interfaces"]
            for source in iface.get("from", [])
        ]
        assert "apps.gift_registry" in interface_sources

    def test_scaffold_module_fails_if_module_already_exists(
        self, tmp_path: Path
    ) -> None:
        """Garante que FileExistsError é disparado caso o diretório do módulo já exista."""
        apps_dir = tmp_path / "backend" / "apps"
        docs_dir = tmp_path / "docs" / "architecture" / "domains"
        tach_file = tmp_path / "backend" / "tach.toml"
        tach_file.parent.mkdir(parents=True)
        tach_file.write_text(
            '[[modules]]\npath = "config"\ndepends_on = []\n',
            encoding="utf-8",
        )

        # Primeira execução com sucesso
        scaffold_module(
            "gift_registry",
            apps_dir=apps_dir,
            docs_dir=docs_dir,
            tach_path=tach_file,
        )

        # Segunda tentativa deve disparar FileExistsError (proteção contra sobrescrita)
        with pytest.raises(FileExistsError, match="já existe"):
            scaffold_module(
                "gift_registry",
                apps_dir=apps_dir,
                docs_dir=docs_dir,
                tach_path=tach_file,
            )


@pytest.mark.unit
class TestTachTomlInjection:
    """Testes para a injeção idempotente no arquivo tach.toml."""

    def test_tach_injection_is_idempotent(self, tmp_path: Path) -> None:
        """Garante que chamadas repetidas não duplicam blocos nem dependências no tach.toml."""
        tach_file = tmp_path / "tach.toml"
        tach_file.write_text(
            '[[modules]]\npath = "apps.core"\ndepends_on = []\n\n'
            '[[modules]]\npath = "config"\ndepends_on = [\n    { path = "apps.core" },\n]\n\n'
            "# --- Gateway Exposure ---\n"
            '[[interfaces]]\nfrom = ["apps.core"]\nexpose = ["*"]\n',
            encoding="utf-8",
        )

        # Primeira injeção
        first_modified = update_tach_toml(tach_file, "guest_book")
        assert first_modified is True

        content_after_first = tach_file.read_text(encoding="utf-8")
        parsed = tomllib.loads(content_after_first)

        # Módulo inserido
        mod = next(m for m in parsed["modules"] if m["path"] == "apps.guest_book")
        assert [d["path"] for d in mod["depends_on"]] == [
            "apps.core",
            "apps.tenants",
            "apps.users",
        ]

        # Config atualizado
        config = next(m for m in parsed["modules"] if m["path"] == "config")
        assert {"path": "apps.guest_book"} in config["depends_on"]

        # Interface inserida
        iface = next(i for i in parsed["interfaces"] if "apps.guest_book" in i["from"])
        assert iface["expose"] == ["interfaces.*", "schemas.*"]

        # Segunda injeção no mesmo arquivo (deve ser estritamente idempotente)
        second_modified = update_tach_toml(tach_file, "guest_book")
        assert second_modified is False

        content_after_second = tach_file.read_text(encoding="utf-8")
        assert content_after_first == content_after_second

    def test_tach_injection_with_real_tach_structure(self, tmp_path: Path) -> None:
        """Valida que a manipulação de TOML funciona preservando a estrutura real do tach.toml."""
        real_tach = ROOT_DIR / "backend" / "tach.toml"
        if not real_tach.exists():
            pytest.skip(
                "Arquivo backend/tach.toml não encontrado para teste de integração."
            )

        temp_tach = tmp_path / "tach.toml"
        shutil.copyfile(real_tach, temp_tach)

        modified = update_tach_toml(temp_tach, "vows_catalog")
        assert modified is True

        parsed = tomllib.loads(temp_tach.read_text(encoding="utf-8"))
        assert any(m["path"] == "apps.vows_catalog" for m in parsed["modules"])

        # Chamada subsequente não deve modificar nada
        modified_again = update_tach_toml(temp_tach, "vows_catalog")
        assert modified_again is False

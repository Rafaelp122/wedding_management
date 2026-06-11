import pytest
from django.core.exceptions import ValidationError

from apps.tenants.models import Company
from apps.tenants.services.tenant_service import TenantService


@pytest.mark.django_db
class TestTenantService:
    """Testes para o TenantService."""

    def test_create_company_success(self):
        """Garante que a empresa é criada corretamente com um slug único."""
        display_name = "Rafael Araujo"
        company = TenantService.create_company(display_name)

        assert isinstance(company, Company)
        assert company.name == f"Workspace de {display_name}"
        assert display_name.lower().split()[0] in company.slug
        assert company.is_active is True

    def test_create_company_slug_uniqueness(self):
        """Garante que duas empresas com o mesmo nome ganham slugs diferentes."""
        display_name = "Mesmo Nome"
        company1 = TenantService.create_company(display_name)
        company2 = TenantService.create_company(display_name)

        assert company1.slug != company2.slug
        assert company1.id != company2.id

    def test_get_or_create_admin_workspace(self):
        """Garante que o workspace administrativo é único e persistente."""
        admin_company1 = TenantService.get_or_create_admin_workspace()
        admin_company2 = TenantService.get_or_create_admin_workspace()

        assert admin_company1.slug == "admin-workspace"
        assert admin_company1.id == admin_company2.id
        assert Company.objects.filter(slug="admin-workspace").count() == 1

    def test_create_company_with_custom_name(self):
        """company_name explícito substitui o nome padrão 'Workspace de ...'."""
        company = TenantService.create_company(
            display_name="Rafael", company_name="Cerimonial XPTO"
        )
        assert company.name == "Cerimonial XPTO"
        assert "Workspace de" not in company.name

    def test_create_company_special_chars_in_display_name(self):
        """Caracteres especiais e acentos são normalizados no slug."""
        company = TenantService.create_company(display_name="João & Maria")
        assert "joao" in company.slug
        assert "&" not in company.slug

    def test_create_company_whitespace_only_display_name(self):
        """Display name apenas com espaços gera slug mínimo com UUID."""
        company = TenantService.create_company(display_name="   ")
        assert company.name == "Workspace de    "
        assert company.slug  # slug não-vazio (contém UUID)

    def test_create_company_display_name_too_long_raises(self):
        """Display name >255 chars faz name exceder max_length → ValidationError."""
        long_name = "A" * 300

        with pytest.raises(ValidationError):
            TenantService.create_company(display_name=long_name)

    def test_create_company_custom_name_too_long_raises(self):
        """company_name >255 chars excede max_length → ValidationError."""
        long_name = "B" * 300

        with pytest.raises(ValidationError):
            TenantService.create_company(display_name="Rafael", company_name=long_name)

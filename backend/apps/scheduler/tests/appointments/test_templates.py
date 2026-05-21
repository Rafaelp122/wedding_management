import pytest

from apps.core.exceptions import BusinessRuleViolation
from apps.scheduler.services.templates import (
    TEMPLATE_CHOICES,
    TEMPLATES,
    get_template_events,
)


@pytest.mark.django_db
class TestGetTemplateEvents:
    """Testes para a função de obtenção de templates de cronograma."""

    def test_get_religious_12m_template(self):
        """Retorna eventos do template religious_12m com estrutura correta."""
        events = get_template_events("religious_12m")

        assert len(events) == 10
        for event in events:
            assert "title" in event
            assert "event_type" in event
            assert "offset_days" in event
            assert isinstance(event["offset_days"], int)

    def test_get_beach_6m_template(self):
        """Retorna eventos do template beach_6m."""
        events = get_template_events("beach_6m")

        assert len(events) == 8
        assert events[0]["title"] == "Definir local na praia"

    def test_get_civil_buffet_3m_template(self):
        """Retorna eventos do template civil_buffet_3m."""
        events = get_template_events("civil_buffet_3m")

        assert len(events) == 7

    def test_invalid_template_raises_business_rule_violation(self):
        """Template inexistente levanta BusinessRuleViolation."""
        with pytest.raises(BusinessRuleViolation) as exc_info:
            get_template_events("invalid_template_name")

        assert exc_info.value.code == "template_not_found"
        assert "invalid_template_name" in str(exc_info.value.detail)

    def test_all_template_names_are_valid(self):
        """Todos os nomes em TEMPLATE_CHOICES são válidos."""
        for name in TEMPLATE_CHOICES:
            events = get_template_events(name)
            assert isinstance(events, list)
            assert len(events) > 0

    def test_templates_are_not_mutated_on_access(self):
        """get_template_events não modifica a estrutura original do template."""
        events = get_template_events("religious_12m")

        assert "offset_days" in events[0], (
            "Após o acesso, offset_days deve permanecer no dict original"
        )

        # O template no registry deve permanecer intacto
        original = TEMPLATES["religious_12m"]
        assert "offset_days" in original[0]

    def test_empty_template_name_raises(self):
        """Nome vazio ou nulo levanta erro apropriado."""
        with pytest.raises(BusinessRuleViolation):
            get_template_events("")

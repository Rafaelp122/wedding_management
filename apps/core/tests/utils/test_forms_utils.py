import pytest
from django import forms
from django.test import SimpleTestCase

from apps.core.utils.forms_utils import add_attr, add_placeholder


@pytest.mark.unit
class FormUtilsTest(SimpleTestCase):
    def test_add_attr_creates_new_attribute(self):
        """
        Se o atributo não existe, deve criar.
        """
        field = forms.CharField()
        # O widget.attrs começa vazio ou com defaults

        add_attr(field, "class", "nova-classe")

        self.assertEqual(field.widget.attrs["class"], "nova-classe")

    def test_add_attr_appends_to_existing_attribute(self):
        """
        Se o atributo já existe, deve concatenar (com espaço) e não sobrescrever.
        """
        field = forms.CharField()
        field.widget.attrs["class"] = "classe-original"

        add_attr(field, "class", "nova-classe")

        expected = "classe-original nova-classe"
        self.assertEqual(field.widget.attrs["class"], expected)

    def test_add_attr_strips_whitespace(self):
        """
        Garante que não ficam espaços sobrando nas pontas.
        """
        field = forms.CharField()
        add_attr(field, "class", " teste ")  # Com espaços

        self.assertEqual(field.widget.attrs["class"], "teste")

    def test_add_placeholder(self):
        """
        Testa o helper específico de placeholder.
        """
        field = forms.CharField()
        add_placeholder(field, "Digite aqui")

        self.assertEqual(field.widget.attrs["placeholder"], "Digite aqui")

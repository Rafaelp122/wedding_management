import pytest
from django import forms
from django.test import SimpleTestCase

from apps.core.mixins.forms import FormStylingMixin, FormStylingMixinLarge


@pytest.mark.unit
class FormStylingMixinTest(SimpleTestCase):
    def setUp(self):
        # Criamos um formulário Dummy que herda o Mixin para testar
        class TestForm(FormStylingMixin, forms.Form):
            nome = forms.CharField(required=True)
            ativo = forms.BooleanField(required=False)

        self.form_class = TestForm

    def test_init_applies_standard_css_classes(self):
        """
        Deve aplicar 'form-control ps-5' em campos normais e
        'form-check-input' em checkboxes.
        """
        form = self.form_class()

        # Verifica campo CharField
        class_nome = form.fields["nome"].widget.attrs.get("class")
        self.assertIn("form-control", class_nome)
        self.assertIn("ps-5", class_nome)

        # Verifica campo BooleanField (Checkbox)
        class_ativo = form.fields["ativo"].widget.attrs.get("class")
        self.assertEqual(class_ativo, "form-check-input")

    def test_post_clean_applies_error_class(self):
        """
        Se houver erro de validação, deve adicionar 'is-invalid'.
        """
        # Instancia o form com dados vazios para forçar erro no campo 'nome' (required)
        form = self.form_class(data={})

        # Força a validação
        form.is_valid()

        # Verifica se o campo 'nome' (que deu erro) ganhou a classe is-invalid
        class_nome = form.fields["nome"].widget.attrs.get("class")
        self.assertIn("is-invalid", class_nome)
        # Deve manter as classes originais também
        self.assertIn("form-control", class_nome)


@pytest.mark.unit
class FormStylingMixinLargeTest(SimpleTestCase):
    def setUp(self):
        class TestFormLarge(FormStylingMixinLarge, forms.Form):
            titulo = forms.CharField()
            check = forms.BooleanField()

        self.form_class = TestFormLarge

    def test_init_applies_large_css_classes(self):
        """
        Deve aplicar 'form-control-lg' e 'custom-font-size'.
        """
        form = self.form_class()

        class_titulo = form.fields["titulo"].widget.attrs.get("class")

        self.assertIn("form-control-lg", class_titulo)
        self.assertIn("custom-font-size", class_titulo)
        # Checkbox continua igual
        class_check = form.fields["check"].widget.attrs.get("class")
        self.assertEqual(class_check, "form-check-input")

    def test_post_clean_applies_error_class_large(self):
        """
        Verifica se o tratamento de erro funciona também no Mixin Large.
        """
        # Força erro (campo vazio required)
        form = self.form_class(data={})
        form.is_valid()

        class_titulo = form.fields["titulo"].widget.attrs.get("class")
        self.assertIn("is-invalid", class_titulo)

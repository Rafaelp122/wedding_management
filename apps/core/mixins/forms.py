from django import forms
from ..utils.forms_utils import add_attr


class FormStylingMixin:
    """Mixin que aplica classes CSS padrão aos campos de formulário"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona classes de estilo para cada campo do formulário
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, "class", "form-check-input")
            else:
                add_attr(field, "class", "form-control ps-5")

    def _post_clean(self):
        super()._post_clean()

        # Marca os campos com erro como inválidos (para exibir feedback visual)
        if self.errors:
            for field_name in self.errors:
                field = self.fields.get(field_name)
                if field:
                    add_attr(field, "class", "is-invalid")


class FormStylingMixinLarge:
    """
    Mixin que aplica classes CSS padrão aos campos de formulário.\n
    Versão do mixin com campos maiores (usado em formulários mais destacados).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aplica classes de estilo em tamanho grande
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, "class", "form-check-input")
            else:
                add_attr(
                    field, "class", "form-control form-control-lg ps-5 custom-font-size"
                )

    def _post_clean(self):
        super()._post_clean()

        # Marca os campos inválidos com a classe CSS de erro
        if self.errors:
            for field_name in self.errors:
                field = self.fields.get(field_name)
                if field:
                    add_attr(field, "class", "is-invalid")

from django import forms
from .django_forms import add_attr


# Mixin que aplica classes CSS padrão aos campos de formulário
class FormStylingMixin:
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


# Versão do mixin com campos maiores (usado em formulários mais destacados)
class FormStylingMixinLarge:
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

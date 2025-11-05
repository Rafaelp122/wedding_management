from django import forms

from .django_forms import add_attr


class FormStylingMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, "class", "form-check-input")
            else:
                add_attr(field, "class", "form-control ps-5")

            if field_name in self.errors:
                add_attr(field, "class", "is-invalid")


class FormStylingMixinLarge:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, "class", "form-check-input")
            else:
                add_attr(
                    field, "class", "form-control form-control-lg ps-5 custom-font-size"
                )

            if field_name in self.errors:
                add_attr(field, "class", "is-invalid")

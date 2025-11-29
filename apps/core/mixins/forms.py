from typing import Any, ClassVar

from django import forms

from ..utils.forms_utils import add_attr


class BaseFormStylingMixin:
    """
    Mixin base que aplica classes CSS padrão aos campos de formulário.

    Este mixin automatiza a aplicação de classes Bootstrap para estilizar
    formulários, incluindo tratamento especial para checkboxes e
    marcação visual de campos com erro de validação.

    Attributes:
        form_control_classes: Classes CSS para campos normais.
                             Pode ser sobrescrito em subclasses.
        checkbox_classes: Classes CSS para checkboxes.
                         Padrão: "form-check-input"

    Usage:
        class MyForm(FormStylingMixin, forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ['name', 'email']
    """

    # Classes CSS aplicadas aos campos normais (não-checkbox)
    form_control_classes: str = "form-control ps-5"

    # Classes CSS aplicadas aos checkboxes
    checkbox_classes: str = "form-check-input"

    fields: dict[str, forms.Field]
    errors: dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._apply_form_styling()

    def _apply_form_styling(self) -> None:
        """
        Aplica as classes CSS apropriadas a cada campo do formulário.

        Itera sobre todos os campos, aplicando classes específicas
        para checkboxes e classes padrão para outros tipos de campo.
        """
        for _field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, "class", self.checkbox_classes)
            else:
                add_attr(field, "class", self.form_control_classes)

    def _post_clean(self) -> None:
        """
        Hook chamado após a validação do formulário.

        Adiciona a classe 'is-invalid' aos campos que apresentam
        erros de validação, permitindo feedback visual ao usuário.
        """
        super()._post_clean()  # type: ignore[misc]

        if self.errors:
            for field_name in self.errors:
                field = self.fields.get(field_name)
                if field:
                    add_attr(field, "class", "is-invalid")


class FormStylingMixin(BaseFormStylingMixin):
    """
    Mixin que aplica classes CSS Bootstrap padrão aos campos.

    Este é o mixin padrão para formulários normais,
    com tamanho regular de campos.

    Herda de BaseFormStylingMixin e usa as classes CSS padrão.
    """

    pass


class FormStylingMixinLarge(BaseFormStylingMixin):
    """
    Mixin que aplica classes CSS Bootstrap em tamanho grande.

    Versão do mixin com campos maiores, usada em formulários
    mais destacados como páginas de login, registro ou formulários
    principais da aplicação.

    Sobrescreve as classes CSS para usar tamanho grande (lg)
    e adiciona classe customizada de fonte.
    """

    # Sobrescreve as classes para usar tamanho grande
    form_control_classes: str = "form-control form-control-lg ps-5 custom-font-size"


class FormLayoutMixin:
    """
    Mixin genérico para definir layout responsivo de formulários.

    Este mixin adiciona informações de layout (classes CSS Bootstrap)
    e ícones Font Awesome ao contexto do template, seguindo o
    princípio DRY (Don't Repeat Yourself).

    Attributes:
        form_layout_dict: Dicionário com classes CSS Bootstrap para
                         cada campo do formulário. Ex: {"name": "col-md-6"}
        default_col_class: Classe CSS padrão para campos não
                          especificados. Default: "col-12"
        form_icons: Dicionário com ícones Font Awesome para cada campo.
                   Ex: {"name": "fas fa-user"}

    Usage:
        # Na view:
        class MyFormView(FormLayoutMixin, CreateView):
            form_layout_dict = {
                "name": "col-md-6",
                "email": "col-md-6",
            }
            form_icons = {
                "name": "fas fa-user",
                "email": "fas fa-envelope",
            }

    Note:
        Este mixin deve ser usado em Views (não em Forms),
        pois adiciona contexto ao template através de get_context_data().
    """

    form_layout_dict: ClassVar[dict[str, str]] = {}
    default_col_class: str = "col-12"
    form_icons: ClassVar[dict[str, str]] = {}

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Adiciona as variáveis de layout ao contexto do template.

        Args:
            **kwargs: Argumentos de contexto adicionais.

        Returns:
            Dicionário com o contexto completo incluindo dados de layout.
        """
        ctx = super().get_context_data(**kwargs)  # type: ignore[misc]
        ctx["form_layout_dict"] = self.form_layout_dict
        ctx["default_col_class"] = self.default_col_class
        ctx["form_icons"] = self.form_icons
        return ctx

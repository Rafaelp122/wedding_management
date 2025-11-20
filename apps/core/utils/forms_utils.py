# Funções utilitárias para manipular atributos de campos de formulário

from django import forms


def add_attr(field: forms.Field, attr_name: str, attr_new_val: str) -> None:
    """
    Adiciona ou atualiza um atributo HTML em um campo de formulário.

    Args:
        field: Campo do formulário Django.
        attr_name: Nome do atributo HTML (ex: 'class', 'placeholder').
        attr_new_val: Novo valor a ser adicionado ao atributo.
    """
    existing = field.widget.attrs.get(attr_name, "")
    field.widget.attrs[attr_name] = f"{existing} {attr_new_val}".strip()


def add_placeholder(field: forms.Field, placeholder_val: str) -> None:
    """
    Adiciona um placeholder a um campo de formulário.

    Args:
        field: Campo do formulário Django.
        placeholder_val: Texto do placeholder.
    """
    add_attr(field, "placeholder", placeholder_val)

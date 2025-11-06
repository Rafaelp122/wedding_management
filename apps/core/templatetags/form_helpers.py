from django import template

register = template.Library()


@register.simple_tag
def get_field_class(field, layout_dict, default_class="col-12"):
    """
    Retorna a classe de coluna CSS para um campo de formulário específico.
    """
    # Se layout_dict não for um dicionário (ex: chegou como string vazia),
    # o tratamos como um dicionário vazio para evitar o erro.
    if not isinstance(layout_dict, dict):
        layout_dict = {}

    return layout_dict.get(field.name, default_class)


@register.filter
def get_icon_class(field, icon_dict):
    """Retorna a classe do ícone para o campo, ou vazio se não existir."""
    # Mesma verificação de segurança para o dicionário de ícones.
    if not isinstance(icon_dict, dict):
        icon_dict = {}

    return icon_dict.get(field.name, "")

from django import template

register = template.Library()


@register.simple_tag
def get_field_class(field, layout_dict, default_class='col-12'):
    """
    Retorna a classe de coluna CSS para um campo de formulário específico.

    Argumentos:
        field: O objeto do campo do formulário (do loop `for field in form`).
        layout_dict: Um dicionário Python onde as chaves são os nomes dos campos
                     e os valores são as classes CSS.
        default_class: A classe CSS a ser retornada se o nome do campo não for
                       encontrado no dicionário.
    """
    # Usa o método .get() do dicionário, que é uma forma segura de buscar uma chave.
    # Se a chave `field.name` não existir, ele retorna o valor de `default_class`.
    return layout_dict.get(field.name, default_class)


@register.filter
def get_icon_class(field, icon_dict):
    """Retorna a classe do ícone para o campo, ou vazio se não existir."""
    return icon_dict.get(field.name, '')

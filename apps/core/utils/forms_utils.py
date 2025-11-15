# Funções utilitárias para manipular atributos de campos de formulário


def add_attr(field, attr_name, attr_new_val):
    # Adiciona ou atualiza um atributo HTML em um campo de formulário
    existing = field.widget.attrs.get(attr_name, "")
    field.widget.attrs[attr_name] = f"{existing} {attr_new_val}".strip()


def add_placeholder(field, placeholder_val):
    # Adiciona um placeholder a um campo de formulário
    add_attr(field, "placeholder", placeholder_val)

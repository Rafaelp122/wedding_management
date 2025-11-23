"""
Constantes específicas do app weddings.
Centraliza valores mágicos e configurações.
"""

# Paginação
WEDDING_ITEMS_PER_PAGE = 6
PAGINATION_SIDES = 2
PAGINATION_ENDS = 1

# IDs e Seletores HTMX
WEDDING_LIST_CONTAINER_ID = "#wedding-list-container"

# Templates
WEDDING_LIST_TEMPLATE = "weddings/partials/_list_and_pagination.html"
WEDDING_FORM_MODAL_TEMPLATE = "partials/form_modal.html"
WEDDING_DELETE_MODAL_TEMPLATE = "partials/confirm_delete_modal.html"

# URLs
WEDDING_LIST_URL_NAME = "weddings:my_weddings"

# Aria Labels
WEDDING_PAGINATION_ARIA_LABEL = "Paginação de Casamentos"

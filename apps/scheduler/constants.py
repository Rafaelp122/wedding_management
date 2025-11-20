"""
Constants for the Scheduler app.

Centralizes magic strings, DOM IDs, HTMX triggers, and other
configuration values to improve maintainability.
"""

# ===== HTMX Triggers ===== #
EVENT_SAVED_TRIGGER = "eventSaved"

# ===== DOM IDs ===== #
TAB_SCHEDULER_ID = "tab-scheduler"
CALENDAR_CONTAINER_ID = "calendar"
FORM_MODAL_ID = "form-modal"
FORM_MODAL_CONTAINER_ID = "form-modal-container"

# ===== Template Names ===== #
SCHEDULER_PARTIAL_TEMPLATE = "scheduler/partials/_scheduler_partial.html"
EVENT_FORM_MODAL_TEMPLATE = "partials/form_modal.html"
EVENT_DETAIL_TEMPLATE = "scheduler/partials/_event_detail.html"
CONFIRM_DELETE_TEMPLATE = "partials/confirm_delete_modal.html"

# ===== Modal Configuration ===== #
MODAL_CREATE_TITLE = "Novo Evento"
MODAL_EDIT_TITLE = "Editar Evento"
SUBMIT_CREATE_TEXT = "Criar Evento"
SUBMIT_EDIT_TEXT = "Salvar Alterações"
DELETE_OBJECT_TYPE = "o evento"

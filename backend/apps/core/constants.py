from apps.core.schemas import ErrorResponse


# Erros comuns para operações de leitura (GET)
READ_ERROR_RESPONSES = {
    404: ErrorResponse,
}


# Erros comuns para operações que alteram dados (POST, PATCH, DELETE)
# Mapeia os status das exceptions no core/exceptions.py
MUTATION_ERROR_RESPONSES = {
    400: ErrorResponse,
    404: ErrorResponse,
    409: ErrorResponse,
    422: ErrorResponse,
}


# Categorias padrão de orçamento criadas automaticamente ao inicializar um casamento
DEFAULT_BUDGET_CATEGORIES = [
    "Espaço e Buffet",
    "Decoração e Flores",
    "Fotografia e Vídeo",
    "Assessoria",
    "Música e Entretenimento",
    "Vestuário e Acessórios",
]

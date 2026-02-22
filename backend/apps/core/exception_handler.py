import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler


logger = logging.getLogger("wedding_management.api")


def custom_exception_handler(exc, context):
    """
    Manipulador global de exceções da API REST.

    Intercepta exceções geradas durante o processamento de uma requisição HTTP,
    padroniza o formato da resposta JSON e garante o registro adequado nos logs.
    Implementa a conversão automática de exceções nativas do Django para seus
    equivalentes no Django REST Framework.

    Args:
        exc (Exception): A instância da exceção original capturada.
        context (dict): Dicionário injetado pelo DRF contendo contexto de execução
            (ex: 'request' e a 'view' atual).

    Returns:
        Response | None: Objeto Response formatado com o payload padronizado:
            {"error_code": str, "message": str, "details": dict (opcional)}.
            Retorna None para erros não mapeados (500 Internal Server Error),
            delegando a captura final para a infraestrutura (Sentry/Django Base).
    """
    # Normalização: Converte exceções internas do framework (Models/Core)
    # para que o DRF consiga aplicar os status HTTP corretos (400, 403, 404).
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(
            detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages
        )
    elif isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    # Delegação para a rotina padrão do DRF gerar o objeto Response base.
    response = exception_handler(exc, context)

    view_name = (
        context["view"].__class__.__name__
        if context and "view" in context
        else "UnknownView"
    )

    # Processamento de exceções mapeadas (Erros HTTP 4xx).
    if response is not None:
        message = "Ocorreu um erro de validação."

        # Extração hierárquica da mensagem primária gerada pelo DRF.
        if isinstance(response.data, dict) and "detail" in response.data:
            message = response.data["detail"]
        elif isinstance(response.data, list) and len(response.data) > 0:
            message = str(response.data[0])

        # Construção do payload de contrato estrito com o frontend.
        custom_data = {
            "error_code": getattr(exc, "default_code", "validation_error"),
            "message": message,
        }

        # Isolamento de falhas de campos específicos (ex: erros de formulário).
        if isinstance(response.data, dict):
            details = {k: v for k, v in response.data.items() if k != "detail"}
            if details:
                custom_data["details"] = details

        response.data = custom_data

        # Registro de auditoria. Nível WARNING por tratar-se de falhas de negócio
        # ou requisições malformadas, não falhas de infraestrutura.
        logger.warning(
            f"API Error ({response.status_code}) na view {view_name}: {message}",
            extra={
                "error_code": custom_data["error_code"],
                "details": custom_data.get("details"),
            },
        )

    # Processamento de exceções críticas (Erros HTTP 5xx).
    else:
        # Falhas estruturais (ex: falha de DB, KeyErrors).
        # Exige nível ERROR e captura do stacktrace para diagnóstico imediato.
        logger.error(
            f"FATAL UNHANDLED ERROR em {view_name}: {exc!s}",
            exc_info=True,
        )

    return response

from rest_framework import status
from rest_framework.exceptions import APIException


class ApplicationError(APIException):
    """
    Exceção base para toda a arquitetura.
    O Handler global só vai formatar elegantemente os erros que herdarem disto.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ocorreu um erro na aplicação."
    default_code = "application_error"

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail

        if code is not None:
            self.code = code
        else:
            self.code = self.default_code


class BusinessRuleViolation(ApplicationError):
    """
    Para falhas de lógica (ex: ADR-010 Tolerância Zero).
    Status 422: O formato está certo, mas a regra de negócio impede o processamento.
    """

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Violação de regra de negócio."
    default_code = "business_rule_violation"


class DomainIntegrityError(ApplicationError):
    """
    Para violações de fronteiras (ex: associar despesa ao casamento errado).
    Status 409: Conflito de estado no servidor.
    """

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Erro de integridade ou conflito de dados."
    default_code = "domain_integrity_error"

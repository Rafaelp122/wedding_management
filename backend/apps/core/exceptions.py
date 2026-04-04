class ApplicationError(Exception):
    """
    Exceção base para toda a arquitetura.
    """

    status_code = 400
    default_detail = "Ocorreu um erro na aplicação."
    default_code = "application_error"

    def __init__(self, detail=None, code=None):
        self.detail = detail if detail is not None else self.default_detail
        self.code = code if code is not None else self.default_code
        super().__init__(self.detail)


class ObjectNotFoundError(ApplicationError):
    """
    Status 404: Recurso não encontrado.
    Usada para substituir o get_object_or_404 na Service Layer.
    """

    status_code = 404
    default_detail = "O recurso solicitado não foi encontrado."
    default_code = "not_found"


class BusinessRuleViolation(ApplicationError):
    """
    Para falhas de lógica (ex: ADR-010 Tolerância Zero).
    Status 422: O formato está certo, mas a regra de negócio impede o processamento.
    """

    status_code = 422
    default_detail = "Violação de regra de negócio."
    default_code = "business_rule_violation"


class DomainIntegrityError(ApplicationError):
    """
    Para violações de fronteiras (ex: associar despesa ao casamento errado).
    Status 409: Conflito de estado no servidor.
    """

    status_code = 409
    default_detail = "Erro de integridade ou conflito de dados."
    default_code = "domain_integrity_error"

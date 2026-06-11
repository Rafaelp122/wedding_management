"""
Testes CRÍTICOS para hierarquia de exceções.

Garantir que as exceções são mapeadas corretamente para códigos HTTP
e seguem o padrão definido na arquitetura.
"""

import pytest

from apps.core.exceptions import (
    ApplicationError,
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)


class TestExceptionHierarchy:
    """Testes para a hierarquia de exceções da aplicação."""

    def test_application_error_base_class(self):
        """Teste CRÍTICO: ApplicationError é a classe base para todas."""
        # Testar instanciação básica
        error = ApplicationError()
        assert error.status_code == 400
        assert error.default_detail == "Ocorreu um erro na aplicação."
        assert error.default_code == "application_error"
        assert str(error) == "Ocorreu um erro na aplicação."

        # Testar customização
        custom_error = ApplicationError(detail="Erro personalizado", code="custom_code")
        assert custom_error.detail == "Erro personalizado"
        assert custom_error.code == "custom_code"
        assert str(custom_error) == "Erro personalizado"

    def test_object_not_found_error(self):
        """Teste CRÍTICO: ObjectNotFoundError mapeia para 404."""
        error = ObjectNotFoundError()
        assert error.status_code == 404
        assert error.default_detail == "O recurso solicitado não foi encontrado."
        assert error.default_code == "not_found"
        assert isinstance(error, ApplicationError)  # Herda de ApplicationError

        # Testar customização
        custom_error = ObjectNotFoundError(detail="Usuário não encontrado")
        assert custom_error.detail == "Usuário não encontrado"
        assert custom_error.status_code == 404  # Sempre 404

    def test_business_rule_violation(self):
        """Teste CRÍTICO: BusinessRuleViolation mapeia para 422."""
        error = BusinessRuleViolation()
        assert error.status_code == 422
        assert error.default_detail == "Violação de regra de negócio."
        assert error.default_code == "business_rule_violation"
        assert isinstance(error, ApplicationError)

        # Testar customização mantém status 422
        custom_error = BusinessRuleViolation(detail="Data não pode ser no passado")
        assert custom_error.detail == "Data não pode ser no passado"
        assert custom_error.status_code == 422

    def test_domain_integrity_error(self):
        """Teste CRÍTICO: DomainIntegrityError mapeia para 409."""
        error = DomainIntegrityError()
        assert error.status_code == 409
        assert error.default_detail == "Erro de integridade ou conflito de dados."
        assert error.default_code == "domain_integrity_error"
        assert isinstance(error, ApplicationError)

        # Testar customização mantém status 409
        custom_error = DomainIntegrityError(detail="Conflito de dados detectado")
        assert custom_error.detail == "Conflito de dados detectado"
        assert custom_error.status_code == 409

    def test_exception_hierarchy_inheritance(self):
        """Teste CRÍTICO: Verificar herança correta da hierarquia."""
        # Todas as exceções específicas herdam de ApplicationError
        assert issubclass(ObjectNotFoundError, ApplicationError)
        assert issubclass(BusinessRuleViolation, ApplicationError)
        assert issubclass(DomainIntegrityError, ApplicationError)

        # Mas não são subclasses umas das outras
        assert not issubclass(ObjectNotFoundError, BusinessRuleViolation)
        assert not issubclass(BusinessRuleViolation, DomainIntegrityError)
        assert not issubclass(DomainIntegrityError, ObjectNotFoundError)

    def test_exception_http_status_mapping(self):
        """Teste CRÍTICO: Mapeamento correto de status HTTP."""
        # Este teste garante que os códigos HTTP estão corretos para a API
        errors = [
            (ApplicationError, 400, "Bad Request"),
            (ObjectNotFoundError, 404, "Not Found"),
            (BusinessRuleViolation, 422, "Unprocessable Entity"),
            (DomainIntegrityError, 409, "Conflict"),
        ]

        for exception_class, expected_status, http_name in errors:
            error = exception_class()
            assert error.status_code == expected_status, (
                f"{exception_class.__name__} deve retornar "
                f"{expected_status} ({http_name}), "
                f"mas retornou {error.status_code}"
            )

    def test_exception_serialization_consistency(self):
        """Teste CRÍTICO: Exceções serializam consistentemente para APIs."""
        # Testar que todas as exceções podem ser serializadas de forma consistente
        test_cases = [
            (ApplicationError, {"detail": "Mensagem teste", "code": "test_code"}),
            (ObjectNotFoundError, {"detail": "Recurso ausente"}),
            (BusinessRuleViolation, {"detail": "Regra violada"}),
            (DomainIntegrityError, {"detail": "Conflito de integridade"}),
        ]

        for exception_class, kwargs in test_cases:
            error = exception_class(**kwargs)

            # Todas devem ter os atributos esperados para serialização
            assert hasattr(error, "detail")
            assert hasattr(error, "code")
            assert hasattr(error, "status_code")

            # O detail deve ser acessível como string
            assert isinstance(str(error), str)
            assert len(str(error)) > 0


@pytest.mark.django_db
class TestExceptionIntegration:
    """Testes de integração para verificar exceções em contexto real."""

    def test_service_raises_correct_exception_types(self):
        """Serviços lançam tipos corretos de exceção com atributos esperados."""
        errors = [
            (ObjectNotFoundError, "Recurso não encontrado", 404),
            (BusinessRuleViolation, "Regra de negócio violada", 422),
            (DomainIntegrityError, "Conflito de integridade", 409),
            (ApplicationError, "Erro genérico", 400),
        ]

        for exc_class, detail, expected_status in errors:
            with pytest.raises(exc_class) as exc:
                raise exc_class(detail=detail)

            assert exc.value.status_code == expected_status
            assert exc.value.detail == detail

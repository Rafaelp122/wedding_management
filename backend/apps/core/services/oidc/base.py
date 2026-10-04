from typing import Protocol, TypedDict


class OIDCClaims(TypedDict, total=False):
    """Claims utilizadas no fluxo de autenticação segura via OIDC entre serviços."""

    iss: str
    aud: str
    email: str


class OIDCVerifier(Protocol):
    """
    Protocolo de interface para serviços de validação de tokens OIDC.

    Decisão Arquitetural:
        ADR-005 (docs/architecture/adr/005-oidc-scheduler.md)
    """

    def verify_token(self, token: str) -> OIDCClaims:
        """
        Valida o token OIDC e retorna as claims contidas no payload.

        Decisão Arquitetural:
            ADR-005 (docs/architecture/adr/005-oidc-scheduler.md)

        Args:
            token: Token JWT OIDC recebido no cabeçalho Authorization.

        Returns:
            Dicionário contendo as claims verificadas do token OIDC.

        Raises:
            PermissionError: Se o token for válido mas a conta de serviço não for autorizada.
            ValueError: Se o token for inválido, expirado ou malformado.
        """
        ...  # pragma: no cover

from typing import Protocol, TypedDict


class OIDCClaims(TypedDict, total=False):
    """Claims usadas pelo fluxo OIDC de autenticação entre serviços."""

    iss: str
    aud: str
    email: str


class OIDCVerifier(Protocol):
    """
    Protocolo definindo a interface para serviços de verificação OIDC (ADR-005).
    """

    def verify_token(self, token: str) -> OIDCClaims:
        """
        Valida o token OIDC e retorna as claims contidas no token.

        Args:
            token: O token JWT OIDC recebido no cabeçalho Authorization.

        Returns:
            Dicionário contendo as claims verificadas do token OIDC.

        Raises:
            PermissionError: Se o token for válido mas a conta não for autorizada.
            ValueError: Se o token for inválido ou malformado.
        """
        ...  # pragma: no cover

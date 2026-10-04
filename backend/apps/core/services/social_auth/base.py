from dataclasses import dataclass
from typing import Protocol, TypedDict


class GoogleIDTokenClaims(TypedDict, total=False):
    """Claims consumidas após a validação do ID token do Google."""

    email: str
    email_verified: bool
    given_name: str
    family_name: str
    sub: str


@dataclass(frozen=True)
class OAuthUserInfo:
    """
    Estrutura imutável com os dados do usuário obtidos do provedor OAuth.
    """

    email: str
    email_verified: bool
    first_name: str
    last_name: str
    sub: str


class OAuthProvider(Protocol):
    """
    Protocolo de interface para provedores de autenticação social (OAuth2).
    """

    def verify_token(self, token: str) -> OAuthUserInfo:
        """
        Valida o token emitido pelo provedor e extrai os dados normalizados do usuário.

        Args:
            token: Token JWT de identidade emitido pelo provedor OAuth.

        Returns:
            Dados normalizados do usuário autenticado no provedor.

        Raises:
            HttpError: Se a verificação do token falhar ou os dados forem inválidos.
        """
        ...

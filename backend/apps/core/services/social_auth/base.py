from dataclasses import dataclass
from typing import Protocol


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
    Interface para provedores de autenticação social (OAuth2).
    """

    def verify_token(self, token: str) -> OAuthUserInfo:
        """
        Verifica o token do provedor e retorna as informações do usuário.

        Args:
            token: O token JWT/ID emitido pelo provedor OAuth.

        Returns:
            OAuthUserInfo com os dados extraídos e validados.

        Raises:
            HttpError: Se a verificação falhar ou os dados forem inválidos.
        """
        ...

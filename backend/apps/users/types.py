from typing import TYPE_CHECKING, Union

from django.contrib.auth.models import AnonymousUser


if TYPE_CHECKING:
    from .models import User
else:
    # Para evitar circular import em tempo de execução, podemos usar strings
    # ou carregar depois. Mas como é um Alias de tipo, Union[User, AnonymousUser]
    # é o que queremos.
    from apps.users.models import User

AuthContextUser = Union["User", AnonymousUser]

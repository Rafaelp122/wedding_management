from functools import wraps

from django.core.exceptions import PermissionDenied

# Não é necessário importar o modelo User se você só vai usar request.user
# from apps.users.models import User 


def planner_required(view_func):
    """
    Decorator que verifica se um usuário está logado (é um "planner").
    Se estiver, anexa o objeto do usuário a request.planner.
    Se não, levanta uma exceção de permissão negada.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # A verificação principal é se o usuário está autenticado.
        if not request.user.is_authenticated:
            raise PermissionDenied("Acesso negado. Você precisa estar logado.")

        # Se ele está logado, request.user JÁ É o objeto do planner.
        # Não é preciso fazer uma consulta. Apenas o atribuímos.
        request.planner = request.user

        # Agora, chame a view original.
        return view_func(request, *args, **kwargs)

    return _wrapped_view

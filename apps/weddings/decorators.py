from functools import wraps
from django.core.exceptions import PermissionDenied
from apps.users.models import Planner

def planner_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            planner = Planner.objects.get(user=request.user)

            request.planner = planner
        except Planner.DoesNotExist:
            raise PermissionDenied("Acesso negado. Você não é um planner.")
        

        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
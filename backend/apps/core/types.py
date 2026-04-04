from django.contrib.auth.models import AnonymousUser

from apps.users.models import User


AuthContextUser = User | AnonymousUser

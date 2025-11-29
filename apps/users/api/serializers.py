"""
Serializers da API de Users.
"""

from typing import ClassVar

from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer básico para User (criação e atualização).

    Usado nos endpoints:
    - POST /api/v1/users/ (registro)
    - PUT/PATCH /api/v1/users/{id}/
    """

    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm Password"
    )

    class Meta:
        model = User
        fields: ClassVar[list] = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "is_active",
            "date_joined",
        ]
        read_only_fields: ClassVar[list] = ["id", "date_joined", "is_active"]
        extra_kwargs: ClassVar[dict] = {
            "password": {"write_only": True},
            "password2": {"write_only": True},
        }

    def validate(self, data):
        """Valida que as senhas são iguais."""
        if "password" in data and "password2" in data:
            if data["password"] != data["password2"]:
                raise serializers.ValidationError(
                    {"password2": "As senhas não coincidem."}
                )
        return data

    def create(self, validated_data):
        """Cria novo usuário com senha criptografada."""
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        """Atualiza usuário, tratando senha separadamente."""
        validated_data.pop("password2", None)
        password = validated_data.pop("password", None)

        # Atualiza campos normais
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Atualiza senha se fornecida
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de usuários.

    Usado em:
    - GET /api/v1/users/

    Retorna apenas informações essenciais.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields: ClassVar[list] = [
            "id",
            "username",
            "email",
            "full_name",
            "is_active",
            "date_joined",
        ]

    def get_full_name(self, obj):
        """Retorna nome completo do usuário."""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer com detalhes completos do usuário.

    Usado em:
    - GET /api/v1/users/{id}/
    - GET /api/v1/users/me/ (perfil do usuário autenticado)

    Inclui contagens de recursos relacionados.
    """

    full_name = serializers.SerializerMethodField()
    weddings_count = serializers.SerializerMethodField()
    events_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields: ClassVar[list] = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "weddings_count",
            "events_count",
        ]
        read_only_fields: ClassVar[list] = ["id", "date_joined", "last_login"]

    def get_full_name(self, obj):
        """Retorna nome completo do usuário."""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username

    def get_weddings_count(self, obj):
        """Retorna número de casamentos do planner."""
        return obj.wedding_set.count() if hasattr(obj, "wedding_set") else 0

    def get_events_count(self, obj):
        """Retorna número de eventos do planner."""
        return obj.events.count() if hasattr(obj, "events") else 0


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para troca de senha.

    Usado em:
    - POST /api/v1/users/{id}/change-password/
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """Valida que as novas senhas são iguais."""
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "As senhas não coincidem."}
            )
        return data

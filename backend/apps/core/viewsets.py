from django.core.exceptions import ImproperlyConfigured
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets


@extend_schema_view(
    list=extend_schema(summary="Listar registros isolados por usuário"),
    retrieve=extend_schema(summary="Obter um registro específico via UUID"),
    create=extend_schema(
        summary="Criar novo registro via Service Layer",
        responses={
            201: OpenApiResponse(description="Criado com sucesso"),
            400: OpenApiResponse(description="Erro de formato/sintaxe (DRF)"),
            422: OpenApiResponse(description="Erro de validação de regra de negócio"),
            409: OpenApiResponse(description="Erro de integridade/conflito"),
        },
    ),
    update=extend_schema(
        summary="Atualizar registro via Service Layer",
        responses={
            200: OpenApiResponse(description="Atualizado com sucesso"),
            400: OpenApiResponse(description="Erro de formato/sintaxe (DRF)"),
            422: OpenApiResponse(description="Erro de validação de regra de negócio"),
        },
    ),
    partial_update=extend_schema(summary="Atualização parcial via Service Layer"),
    destroy=extend_schema(
        summary="Remover registro via Service Layer",
        responses={
            204: OpenApiResponse(description="Removido com sucesso"),
            409: OpenApiResponse(
                description="Erro de integridade (Ex: Protegido contra deleção)"
            ),
        },
    ),
)
class BaseViewSet(viewsets.ModelViewSet):
    """BaseViewSet obrigatório para todos os endpoints.

    Este viewset aplica as regras arquiteturais adotadas pelo projeto:

    1. **Estrita** (ADR-006): a camada de visualização deve ser "burra". Toda
       a lógica de negócio é implementada em classes de serviço (service layer).
       O viewset apenas faz delegação e validações iniciais.
    2. **Multitenant** (ADR-009): garante que qualquer consulta seja automaticamente
       filtrada para o usuário solicitado usando o método `for_user()` do manager.

    Características principais:

    * Busca por `uuid` em vez de `pk` padrão.
    * Obriga subclasses a definir `service_class` com métodos `create`, `update`
      e `delete`.
    * Usa esquemas do drf-spectacular para documentação OpenAPI/Swagger.

    Atributos esperados nas subclasses:

    ``queryset``
        Deve ser definido para que `get_queryset()` possa aplicar o filtro
        multitenant. Caso contrário, um erro de configuração é levantado.
    ``serializer_class``
        Serializador padrão usado pelo `ModelViewSet`.
    ``service_class``
        Classe que implementa os métodos de negócio. Não pode ser None e
        deve fornecer os métodos obrigatórios mencionados acima.
    """

    # campo utilizado pelo DRF para localizar instâncias
    lookup_field = "uuid"

    # deve ser sobrescrito pelas subclasses; validado em `initial()`
    service_class = None

    def initial(self, request, *args, **kwargs):
        """Primeiras verificações antes de qualquer ação.

        Executado no início do ciclo de request do DRF. Nossa implementação
        adiciona validações "fail-fast" para evitar erros posteriores em
        pontos distantes do código:

        * Certifica-se de que `service_class` foi configurado na subclasse.
        * Verifica se a classe de serviço expõe os métodos obrigatórios
          (create, update, delete); essa checagem garante que a interface
          esperada esteja presente, evitando `AttributeError` em métodos
          como `perform_create`.

        Em caso de problema, um `ImproperlyConfigured` é levantado com
        mensagem clara indicando o método/falha.
        """
        super().initial(request, *args, **kwargs)

        # validação de configuração mínima
        if self.service_class is None:
            raise ImproperlyConfigured(
                f"FATAL: {self.__class__.__name__} não define 'service_class'. "
                "Leia o ADR-006."
            )

        # checa existência dos métodos obrigatórios na service class
        required_methods = ["create", "update", "delete"]
        for method in required_methods:
            if not hasattr(self.service_class, method):
                raise ImproperlyConfigured(
                    f"FATAL: O serviço '{self.service_class.__name__}' não implementa "
                    f"o método obrigatório '{method}'."
                )

    def get_queryset(self):
        """Recupera o queryset base, aplicando filtro por usuário.

        O método padrão do `ModelViewSet` já usa `self.queryset`, mas aqui nós
        estendemos para:

        * garantir que `self.queryset` não seja None (falha rápido se esqueceu de
          definir na subclasse);
        * chamar `.for_user(self.request.user)` no manager, o que implementa o
          isolamento multitenant conforme ADR-009.

        O queryset retornado é sempre do tipo "todos os objetos do modelo para o
        usuário atual".
        """
        if self.queryset is None:
            raise ImproperlyConfigured(
                f"FATAL: {self.__class__.__name__} precisa de um 'queryset' definido."
            )
        # all() é necessário para acessar .model antes de filtrar por usuário
        return self.queryset.model.objects.all().for_user(self.request.user)

    def perform_create(self, serializer):
        """Chamada delegada ao serviço para criação.

        O serializer já validou os dados; passamos o `user` autenticado e o
        dicionário `validated_data` para o método `create` da classe de serviço.
        O objeto retornado é atribuído à `serializer.instance` para que o DRF
        possa construir a resposta apropriada.
        """
        serializer.instance = self.service_class.create(
            user=self.request.user, data=serializer.validated_data
        )

    def perform_update(self, serializer):
        """Chamada delegada ao serviço para atualização.

        Busca a instância atual via `self.get_object()` (já filtrada pelo
        queryset multitenant) e repassa ao serviço junto com os dados validados.
        """
        serializer.instance = self.service_class.update(
            instance=self.get_object(),
            user=self.request.user,
            data=serializer.validated_data,
        )

    def perform_destroy(self, instance):
        """Chamada delegada ao serviço para remoção.

        Não retornamos nada; o serviço é responsável por apagar o registro e
        tratar quaisquer regras associadas (log de auditoria, verificações de
        integridade, etc.).
        """
        self.service_class.delete(user=self.request.user, instance=instance)

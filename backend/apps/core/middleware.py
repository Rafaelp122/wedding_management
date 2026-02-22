import uuid

from .logging import _thread_locals


class RequestIDMiddleware:
    """
    Injeta um ID único em cada requisição para permitir o rastreio de logs.
    Sem isto, debugar problemas em concorrência é apenas adivinhação.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Tenta obter do Header (se vier de um Gateway/Proxy) ou gera um novo UUID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 2. Armazena no thread local para que o RequestIDFilter o possa ler
        _thread_locals.request_id = request_id

        # 3. Adiciona ao objeto request caso precises dele numa View ou Service
        request.request_id = request_id

        # Passa o controlo para a próxima camada (View/Service)
        response = self.get_response(request)

        # 4. Devolve o ID no Header da resposta.
        # O Frontend (React) DEVE ler isto e mostrá-lo ao utilizador em caso de erro.
        response["X-Request-ID"] = request_id

        return response

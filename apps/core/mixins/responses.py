"""
Mixins para respostas HTTP padronizadas.
"""
from django.http import JsonResponse


class JsonResponseMixin:
    """
    Mixin genérico para respostas JSON padronizadas.

    Facilita o retorno de respostas JSON com formato consistente
    em toda a aplicação, seguindo o padrão:
    {'success': bool, 'message': str, ...outros dados}

    Usage:
        class MyApiView(JsonResponseMixin, View):
            def post(self, request):
                if data_valid:
                    return self.json_success('Salvo com sucesso!')
                return self.json_error('Erro de validação')
    """

    def json_success(self, message: str, **extra) -> JsonResponse:
        """
        Retorna uma resposta JSON de sucesso padronizada.

        Args:
            message: Mensagem de sucesso para o usuário.
            **extra: Dados adicionais para incluir na resposta.

        Returns:
            JsonResponse com success=True e a mensagem.

        Example:
            return self.json_success(
                'Item criado!',
                item_id=123,
                redirect_url='/items/'
            )
        """
        data = {'success': True, 'message': message}
        data.update(extra)
        return JsonResponse(data)

    def json_error(self, message: str, **extra) -> JsonResponse:
        """
        Retorna uma resposta JSON de erro padronizada.

        Args:
            message: Mensagem de erro para o usuário.
            **extra: Dados adicionais para incluir na resposta.

        Returns:
            JsonResponse com success=False e a mensagem.

        Example:
            return self.json_error(
                'Validação falhou',
                errors={'email': ['Email inválido']}
            )
        """
        data = {'success': False, 'message': message}
        data.update(extra)
        return JsonResponse(data)

from typing import Protocol


class StorageService(Protocol):
    """
    Protocolo definindo a interface para serviços de armazenamento de arquivos.
    """

    def generate_presigned_put_url(
        self, bucket: str, object_key: str, content_type: str, expires_in: int = 900
    ) -> str:
        """
        Gera uma URL pré-assinada para upload direto via PUT.

        Args:
            bucket: O nome do bucket de destino no storage.
            object_key: O caminho/nome único do objeto no bucket.
            content_type: O tipo MIME do arquivo (ex: application/pdf).
            expires_in: O tempo de expiração da URL em segundos.

        Returns:
            A URL pré-assinada em formato de string.
        """
        ...  # pragma: no cover

    def generate_presigned_get_url(
        self, bucket: str, object_key: str, expires_in: int = 900
    ) -> str:
        """
        Gera uma URL pré-assinada para download/leitura segura de um objeto via GET.

        Args:
            bucket: O nome do bucket no storage.
            object_key: O caminho/nome único do objeto no bucket.
            expires_in: O tempo de expiração da URL em segundos.

        Returns:
            A URL pré-assinada de download em formato de string.
        """
        ...  # pragma: no cover

    def upload_bytes(
        self, bucket: str, object_key: str, data: bytes, content_type: str
    ) -> str:
        """
        Faz upload direto de uma sequência de bytes para o bucket de storage.

        Args:
            bucket: O nome do bucket de destino no storage.
            object_key: O caminho/nome único do objeto no bucket.
            data: Conteúdo binário a ser persistido.
            content_type: O tipo MIME do arquivo (ex: application/pdf).

        Returns:
            A chave única do objeto persistido no storage (object_key).
        """
        ...  # pragma: no cover

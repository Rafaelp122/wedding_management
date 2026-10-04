from typing import Protocol


class StorageService(Protocol):
    """
    Protocolo de interface para serviços de armazenamento de arquivos.
    """

    def generate_presigned_put_url(
        self, bucket: str, object_key: str, content_type: str, expires_in: int = 900
    ) -> str:
        """
        Gera URL pré-assinada para upload direto de arquivos via PUT.

        Args:
            bucket: Nome do bucket de destino no storage.
            object_key: Identificador ou caminho do objeto no bucket.
            content_type: Tipo MIME do arquivo a ser enviado.
            expires_in: Tempo de expiração da URL em segundos (padrão de 900s).

        Returns:
            URL pré-assinada para upload.
        """
        ...  # pragma: no cover

    def generate_presigned_get_url(
        self, bucket: str, object_key: str, expires_in: int = 900
    ) -> str:
        """
        Gera URL pré-assinada para leitura ou download seguro via GET.

        Args:
            bucket: Nome do bucket no storage.
            object_key: Identificador ou caminho do objeto no bucket.
            expires_in: Tempo de expiração da URL em segundos (padrão de 900s).

        Returns:
            URL pré-assinada para download.
        """
        ...  # pragma: no cover

    def upload_bytes(
        self, bucket: str, object_key: str, data: bytes, content_type: str
    ) -> str:
        """
        Realiza upload direto de conteúdo binário para o storage.

        Args:
            bucket: Nome do bucket de destino no storage.
            object_key: Identificador ou caminho do objeto no bucket.
            data: Conteúdo binário a ser persistido.
            content_type: Tipo MIME do arquivo.

        Returns:
            Chave do objeto persistido no storage.
        """
        ...  # pragma: no cover

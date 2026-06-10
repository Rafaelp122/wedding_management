from django.core.exceptions import ValidationError


class MaxFileSizeValidator:
    """Valida tamanho máximo de arquivo com tolerância a falhas de I/O.

    Se o storage não estiver acessível (rede, arquivo deletado), a
    validação é bypassada em vez de bloquear saves não relacionados.
    O service ``upload_file`` permanece como guardião primário com
    fast-fail antes do I/O.
    """

    def __init__(self, max_size: int) -> None:
        self.max_size = max_size

    def __call__(self, value) -> None:
        try:
            size = value.size
        except OSError:
            return

        if size is not None and size > self.max_size:
            mb = self.max_size // (1024 * 1024)
            raise ValidationError(
                f"Arquivo excede o limite de {mb}MB.",
                code="max_file_size",
            )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MaxFileSizeValidator):
            return self.max_size == other.max_size
        return False

    def deconstruct(self) -> tuple:
        path = "apps.core.validators.MaxFileSizeValidator"
        args = (self.max_size,)
        kwargs: dict = {}
        return path, args, kwargs

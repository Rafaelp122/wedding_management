from django.db import models


class BaseModel(models.Model):
    """
    Modelo base abstrato que fornece campos de data e hora
    para quando o objeto foi criado e modificado pela última vez.
    """

    created_at = models.DateTimeField(
        verbose_name="Data de Criação",
        auto_now_add=True,
        editable=False,
        help_text="Data e hora em que este objeto foi criado.",
    )
    updated_at = models.DateTimeField(
        verbose_name="Última Atualização",
        auto_now=True,
        help_text="Data e hora em que foi atualizado pela última vez.",
    )

    class Meta:
        """
        Esta classe Meta define o modelo como 'abstract = True',
        o que impede o Django de criar uma tabela no banco de dados
        apenas para esta classe.
        """

        abstract = True

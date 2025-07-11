from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

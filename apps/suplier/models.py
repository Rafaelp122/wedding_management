from django.db import models


class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    servicos_oferecidos = models.TextField()

    def __str__(self):
        return self.nome

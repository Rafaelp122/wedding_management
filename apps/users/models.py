from django.db import models
from django.contrib.auth.models import User


class Cerimonialista(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    servicos_oferecidos = models.TextField()

    def __str__(self):
        return self.nome

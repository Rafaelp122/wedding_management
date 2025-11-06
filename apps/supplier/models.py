from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=20, unique=True)  # Brazilian ID
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    offered_services = models.TextField()

    def __str__(self):
        return self.name

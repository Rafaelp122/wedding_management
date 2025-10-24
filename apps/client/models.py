from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

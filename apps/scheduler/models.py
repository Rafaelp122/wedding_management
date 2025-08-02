from django.db import models

from apps.weddings.models import Wedding


class Schedule(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    datetime = models.DateTimeField()
    type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True)
    wedding = models.ForeignKey(
        Wedding, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.title

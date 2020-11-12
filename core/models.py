from django.db import models

# Create your models here.


class Dato(models.Model):
    valor = models.FloatField()
    location = models.CharField(max_length=15, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return self.location


class Connection(models.Model):
    origin = models.CharField(max_length=100, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.timestamp.strftime('%Y-%m-%d %H:%M: ') +self.origin

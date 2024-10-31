from django.db import models

class Czlowiek(models.Model):
    imie = models.CharField(
        max_length=30,
        null=False,
        blank=False,
        verbose_name="Imie"
    )
    nazwisko = models.CharField(
        max_length=40,
        null=False,
        blank=False,
        verbose_name="Nazwisko",
        default=""
    )
    
    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
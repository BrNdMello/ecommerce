# categorias/models.py
from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        ordering = ['nome']  # Ordena por nome
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
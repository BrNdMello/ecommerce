# pedidos/models.py
from django.db import models
from django.contrib.auth.models import User
from produtos.models import Produto

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aguardando_pagamento', 'Aguardando Pagamento'), # Alterado/Adicionado para Pix
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )

    METODO_PAGAMENTO_CHOICES = (
        ('pix', 'Pix'), # Única opção
    )
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) #
    nome = models.CharField(max_length=100) #
    email = models.EmailField() #
    endereco = models.CharField(max_length=250) #
    cep = models.CharField(max_length=20) #
    cidade = models.CharField(max_length=100) #
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pendente') #
    data_criacao = models.DateTimeField(auto_now_add=True) #
    
    metodo_pagamento = models.CharField(
        max_length=50,
        choices=METODO_PAGAMENTO_CHOICES,
        default='pix' # Pix como padrão
    )
    
    def __str__(self):
        return f'Pedido {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE) #
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE) #
    preco = models.DecimalField(max_digits=10, decimal_places=2) #
    quantidade = models.PositiveIntegerField(default=1) #
    
    def __str__(self):
        return str(self.id)
    
    def get_cost(self):
        return self.preco * self.quantidade
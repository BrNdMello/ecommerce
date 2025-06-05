# pedidos/forms.py
from django import forms
from .models import Pedido #

class FormCriarPedido(forms.ModelForm):
    class Meta:
        model = Pedido #
        # Campo 'metodo_pagamento' removido dos fields, será definido na view.
        fields = ['nome', 'email', 'endereco', 'cep', 'cidade'] #
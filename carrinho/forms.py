# carrinho/forms.py - DEPOIS (Definição correta de formulário)
from django import forms

class FormAdicionarProdutoCarrinho(forms.Form):
    # Exemplo: escolhas para quantidade de 1 a 20
    PRODUTO_QUANTIDADE_CHOICES = [(i, str(i)) for i in range(1, 21)]
    
    quantidade = forms.TypedChoiceField(
                                choices=PRODUTO_QUANTIDADE_CHOICES,
                                coerce=int,
                                label="Quantidade",
                                initial=1 # Define um valor inicial
                            )
    # Campo oculto para indicar se a quantidade deve substituir ou adicionar à existente
    override = forms.BooleanField(required=False, # Não é obrigatório
                                  initial=False,  # Valor inicial
                                  widget=forms.HiddenInput) # Renderizado como <input type="hidden">
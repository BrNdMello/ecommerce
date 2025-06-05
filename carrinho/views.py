# carrinho/views.py - DEPOIS da refatoração
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST # Adicionado para segurança
from produtos.models import Produto
from .cart import Carrinho # Importa a classe Carrinho

@require_POST # Garante que esta view só pode ser acessada via POST
def adicionar_carrinho(request, produto_id):
    carrinho = Carrinho(request) # Usa a classe Carrinho
    produto = get_object_or_404(Produto, id=produto_id)
    # A lógica de adicionar 1 unidade é mantida, mas agora através da classe Carrinho
    carrinho.adicionar(produto=produto, quantidade=1, override_quantidade=False)
    return redirect('carrinho:detalhe')

@require_POST # Garante que esta view só pode ser acessada via POST
def remover_carrinho(request, produto_id):
    carrinho = Carrinho(request) # Usa a classe Carrinho
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho.remover(produto)
    return redirect('carrinho:detalhe')

def detalhe_carrinho(request):
    carrinho = Carrinho(request) # Instancia o objeto Carrinho
    # O objeto 'carrinho' agora é passado diretamente.
    # A iteração e o cálculo do total são feitos pela classe Carrinho e acessados no template.
    return render(request, 'carrinho/detalhe.html', {'carrinho': carrinho})
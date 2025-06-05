# produtos/views.py
from django.shortcuts import render, get_object_or_404
from .models import Categoria, Produto

def lista_produtos(request, categoria_slug=None):
    categoria = None
    categorias = Categoria.objects.all()
    produtos = Produto.objects.filter(disponivel=True)
    
    if categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        produtos = produtos.filter(categoria=categoria)
    
    return render(request, 'produtos/lista.html', {
        'categoria': categoria,
        'categorias': categorias,
        'produtos': produtos
    })

def detalhe_produto(request, id, slug):
    produto = get_object_or_404(Produto, id=id, slug=slug, disponivel=True)
    categorias = Categoria.objects.all()
    return render(request, 'produtos/detalhe.html', {
        'produto': produto,
        'categorias': categorias
    })
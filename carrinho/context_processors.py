# carrinho/context_processors.py
from .cart import Carrinho # Importa a sua classe Carrinho

def carrinho_context(request):
    """
    Torna o objeto Carrinho disponível globalmente nos templates.
    """
    return {'carrinho': Carrinho(request)}
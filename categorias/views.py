# categorias/views.py
from django.shortcuts import render
from .models import Categoria  # Certifique-se de criar um modelo Categoria

def lista(request):
    categorias = Categoria.objects.all()  # Pegando todas as categorias
    return render(request, 'categorias/lista.html', {'categorias': categorias})

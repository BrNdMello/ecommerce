# categorias/urls.py
from django.urls import path
from . import views

app_name = 'categorias'  # Definindo o namespace para o app

urlpatterns = [
    path('', views.lista, name='lista'),  # Defina a URL 'lista' para a view lista
]

from django.urls import path
from . import views

app_name = 'carrinho'

urlpatterns = [
    path('', views.detalhe_carrinho, name='detalhe'),
    path('adicionar/<int:produto_id>/', views.adicionar_carrinho, name='adicionar'),
    path('remover/<int:produto_id>/', views.remover_carrinho, name='remover'),
]

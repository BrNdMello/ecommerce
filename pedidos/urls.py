# pedidos/urls.py
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('criar/', views.criar_pedido, name='criar'),
    path('meus-pedidos/', views.lista_meus_pedidos, name='lista_meus_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('webhook-pix/', views.webhook_pix, name='webhook_pix'),  # Para futura integração
]
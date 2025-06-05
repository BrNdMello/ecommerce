# ecommerce/urls.py (arquivo principal de URLs)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Importe a view de registro do app apropriado.
from pedidos import views as pedidos_views # Mudamos o alias para ser mais genérico ou use o que preferir

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('produtos.urls', namespace='produtos')),
    path('carrinho/', include('carrinho.urls', namespace='carrinho')),
    path('pedidos/', include('pedidos.urls', namespace='pedidos')),
    path('categorias/', include('categorias.urls', namespace='categorias')), # Comentado

    # --- URLs de Autenticação ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='produtos:lista'), name='logout'), 
    
    # --- URL de Registro Apontando para a View Implementada ---
    path('registrar/', pedidos_views.registrar_view, name='registrar'), # Garanta que 'pedidos_views' é o alias correto
    
    # --- Fim URLs de Autenticação ---
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from .models import Produto, Categoria

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nome',)

admin.site.register(Categoria)


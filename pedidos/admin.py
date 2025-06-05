# pedidos/admin.py
from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('get_cost',)
    
    def get_cost(self, obj):
        if obj.pk:
            return f"R$ {obj.get_cost():.2f}"
        return "-"
    get_cost.short_description = "Custo Total"

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'nome', 'email', 'status', 'metodo_pagamento', 'get_total_cost_display', 'data_criacao']
    list_filter = ['status', 'metodo_pagamento', 'data_criacao']
    search_fields = ['nome', 'email', 'usuario__username']
    readonly_fields = ['data_criacao', 'get_total_cost_display']
    inlines = [ItemPedidoInline]
    
    def get_total_cost_display(self, obj):
        return f"R$ {obj.get_total_cost():.2f}"
    get_total_cost_display.short_description = "Total do Pedido"
    
    fieldsets = (
        ('Informações do Cliente', {
            'fields': ('usuario', 'nome', 'email')
        }),
        ('Endereço de Entrega', {
            'fields': ('endereco', 'cep', 'cidade')
        }),
        ('Status do Pedido', {
            'fields': ('status', 'metodo_pagamento')
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'get_total_cost_display'),
            'classes': ('collapse',)
        })
    )

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'produto', 'quantidade', 'preco', 'get_cost']
    list_filter = ['pedido__data_criacao']
    search_fields = ['produto__nome', 'pedido__nome']
    
    def get_cost(self, obj):
        return f"R$ {obj.get_cost():.2f}"
    get_cost.short_description = "Custo Total"
from django.contrib import admin
from .models import Categoria, Autor, Livro, Pedido, ItemPedido, PerfilUsuario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'autor', 'categoria', 'preco', 'preco_promocional', 'estoque', 'destaque', 'mais_vendido')
    list_filter = ('categoria', 'destaque', 'mais_vendido', 'idioma')
    search_fields = ('nome', 'autor__nome', 'isbn')
    list_editable = ('preco', 'preco_promocional', 'estoque', 'destaque', 'mais_vendido')
    fieldsets = (
        ('Informações Básicas', {'fields': ('nome', 'autor', 'categoria', 'descricao')}),
        ('Preços e Estoque', {'fields': ('preco', 'preco_promocional', 'estoque')}),
        ('Imagem', {'fields': ('imagem', 'imagem_url')}),
        ('Detalhes Técnicos', {'fields': ('editora', 'paginas', 'idioma', 'isbn', 'avaliacoes')}),
        ('Destaques', {'fields': ('destaque', 'mais_vendido')}),
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'status', 'total', 'metodo_pagamento', 'criado_em')
    list_filter = ('status',)
    search_fields = ('usuario__username', 'usuario__email')
    list_editable = ('status',)
    inlines = [ItemPedidoInline]
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefone', 'cidade', 'estado')
    search_fields = ('usuario__username', 'usuario__email')
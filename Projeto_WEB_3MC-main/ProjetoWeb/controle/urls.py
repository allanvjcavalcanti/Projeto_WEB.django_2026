from django.urls import path
from .views import (
    home, login_view, auth_view, cadastro_view,
    perfil, logout_view, carrinho, categorias,
    pesquisa, autores, mais_vendidos, promocoes, produto_detalhe, checkout
)

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('auth/', auth_view, name='auth'),
    path('cadastro/', cadastro_view, name='cadastro'),
    path('perfil/', perfil, name='perfil'),
    path('logout/', logout_view, name='logout'),
    path('carrinho/', carrinho, name='carrinho'),
    path('checkout/', checkout, name='checkout'),
    path('categorias/', categorias, name='categorias'),
    path('pesquisa/', pesquisa, name='pesquisa'),
    path('autores/', autores, name='autores'),
    path('mais-vendidos/', mais_vendidos, name='mais_vendidos'),
    path('promocoes/', promocoes, name='promocoes'),
    path('produto/<int:produto_id>/', produto_detalhe, name='produto_detalhe'),
]
from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icone = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Autor(models.Model):
    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='autores/', blank=True, null=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Livro(models.Model):
    nome = models.CharField(max_length=255)
    autor = models.ForeignKey(Autor, on_delete=models.SET_NULL, null=True, related_name='livros')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='livros')
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    preco_promocional = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    imagem = models.ImageField(upload_to='livros/', blank=True, null=True)
    imagem_url = models.CharField(max_length=500, blank=True)
    descricao = models.TextField(blank=True)
    editora = models.CharField(max_length=255, blank=True)
    paginas = models.PositiveIntegerField(blank=True, null=True)
    idioma = models.CharField(max_length=50, default='Português')
    isbn = models.CharField(max_length=20, blank=True)
    avaliacoes = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    estoque = models.PositiveIntegerField(default=0)
    destaque = models.BooleanField(default=False)
    mais_vendido = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_imagem(self):
        if self.imagem:
            return self.imagem.url
        if self.imagem_url:
            return self.imagem_url
        return '/static/img/sem-capa.jpg'

    def em_promocao(self):
        return self.preco_promocional is not None and self.preco_promocional < self.preco

    def preco_atual(self):
        if self.em_promocao():
            return self.preco_promocional
        return self.preco


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    endereco_entrega = models.TextField(blank=True)
    metodo_pagamento = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Pedido #{self.id} — {self.usuario.username}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantidade}x {self.livro.nome}'

    def subtotal(self):
        return self.quantidade * self.preco_unitario


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.TextField(blank=True)
    cep = models.CharField(max_length=10, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f'Perfil de {self.usuario.username}'
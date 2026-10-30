import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Livro, Categoria, Autor, Pedido, ItemPedido, PerfilUsuario


def home(request):
    livros_destaque = Livro.objects.filter(destaque=True).select_related('autor', 'categoria')[:8]
    livros_promocao = Livro.objects.filter(preco_promocional__isnull=False).select_related('autor')[:4]
    return render(request, 'home.html', {
        'livros_destaque': livros_destaque,
        'livros_promocao': livros_promocao,
    })


def categorias(request):
    todas_categorias = Categoria.objects.all()
    categoria_slug = request.GET.get('categoria')
    livros = Livro.objects.all().select_related('autor', 'categoria')
    if categoria_slug:
        livros = livros.filter(categoria__slug=categoria_slug)
    return render(request, 'categorias.html', {
        'categorias': todas_categorias,
        'livros': livros,
        'categoria_ativa': categoria_slug,
    })


def autores(request):
    todos_autores = Autor.objects.prefetch_related('livros').all()
    return render(request, 'autores.html', {'autores': todos_autores})


def mais_vendidos(request):
    livros = Livro.objects.filter(mais_vendido=True).select_related('autor', 'categoria')
    return render(request, 'mais_vendidos.html', {'livros': livros})


def promocoes(request):
    livros = Livro.objects.filter(preco_promocional__isnull=False).select_related('autor', 'categoria')
    return render(request, 'promocoes.html', {'livros': livros})


def carrinho(request):
    return render(request, 'carrinho.html')


def checkout(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'ok': False, 'erro': 'Faça login para finalizar o pedido.'}, status=401)
        try:
            data = json.loads(request.body)
            itens = data.get('itens', [])
            total = float(data.get('total', 0))
            metodo = data.get('metodo_pagamento', '')
            endereco = data.get('endereco', '')

            pedido = Pedido.objects.create(
                usuario=request.user,
                total=total,
                metodo_pagamento=metodo,
                endereco_entrega=endereco,
                status='pago',
            )

            for item in itens:
                livro = Livro.objects.filter(id=item.get('id')).first()
                if livro:
                    ItemPedido.objects.create(
                        pedido=pedido,
                        livro=livro,
                        quantidade=item.get('qtd', 1),
                        preco_unitario=livro.preco_atual(),
                    )
                    qtd = item.get('qtd', 1)
                    if livro.estoque >= qtd:
                        livro.estoque -= qtd
                        livro.save()

            return JsonResponse({'ok': True, 'pedido_id': pedido.id})
        except Exception as e:
            return JsonResponse({'ok': False, 'erro': str(e)}, status=400)

    return render(request, 'checkout.html')


def pesquisa(request):
    query = request.GET.get('q', '').strip()
    livros = Livro.objects.none()
    if query:
        livros = Livro.objects.filter(
            Q(nome__icontains=query) |
            Q(autor__nome__icontains=query) |
            Q(categoria__nome__icontains=query) |
            Q(descricao__icontains=query)
        ).select_related('autor', 'categoria').distinct()
    return render(request, 'pesquisa.html', {'livros': livros, 'query': query})


def produto_detalhe(request, produto_id):
    produto = get_object_or_404(Livro.objects.select_related('autor', 'categoria'), id=produto_id)
    relacionados = Livro.objects.filter(categoria=produto.categoria).exclude(id=produto_id)[:4]
    return render(request, 'produto_detalhe.html', {
        'produto': produto,
        'relacionados': relacionados,
    })


def login_view(request):
    return render(request, 'login.html')


def auth_view(request):
    if request.method == 'POST':
        usuario = authenticate(request, username=request.POST.get('user'), password=request.POST.get('pass'))
        if usuario:
            login(request, usuario)
            return redirect('home')
        return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos'})
    return redirect('login')


def cadastro_view(request):
    if request.method == 'POST':
        username = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        if User.objects.filter(username=username).exists():
            return render(request, 'login.html', {'erro_cadastro': 'Usuário já existe'})
        user = User.objects.create_user(username=username, email=email, password=senha)
        PerfilUsuario.objects.create(usuario=user)
        usuario = authenticate(request, username=username, password=senha)
        if usuario:
            login(request, usuario)
            return redirect('home')
    return redirect('login')


@login_required(login_url='/login/')
def perfil(request):
    perfil_obj, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('itens__livro')

    if request.method == 'POST':
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        perfil_obj.telefone = request.POST.get('telefone', '')
        perfil_obj.endereco = request.POST.get('endereco', '')
        perfil_obj.cep = request.POST.get('cep', '')
        perfil_obj.cidade = request.POST.get('cidade', '')
        perfil_obj.estado = request.POST.get('estado', '')
        perfil_obj.save()
        return redirect('perfil')

    return render(request, 'perfil.html', {
        'usuario': request.user,
        'perfil': perfil_obj,
        'pedidos': pedidos,
    })


def logout_view(request):
    logout(request)
    return redirect('home')
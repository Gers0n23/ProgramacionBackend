from django.shortcuts import render, redirect
from .forms import ProductoForm
from .models import Producto, Categoria, Marca, Caracteristica
from django.db.models import Q

def registro_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            return redirect('resultado_producto', producto_id=producto.id)
    else:
        form = ProductoForm()
    return render(request, 'registro.html', {'form': form})

def consulta_productos(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    caracteristicas = Caracteristica.objects.all()

    categoria = request.GET.get('categoria')
    marca = request.GET.get('marca')
    caracteristica = request.GET.get('caracteristica')

    if categoria:
        productos = productos.filter(categoria__id=categoria)
    if marca:
        productos = productos.filter(marca__id=marca)
    if caracteristica:
        productos = productos.filter(caracteristicas__id=caracteristica)

    context = {
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'caracteristicas': caracteristicas,
    }
    return render(request, 'consulta.html', context)

def resultado_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    return render(request, 'resultado.html', {'producto': producto})
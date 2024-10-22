from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductoForm, CaracteristicaForm
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

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista.html', {'productos': productos})

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear.html', {'form': form})

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar.html', {'form': form, 'producto': producto})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('lista_productos')
    return render(request, 'productos/eliminar.html', {'producto': producto})

# Vistas de Características
def lista_caracteristicas(request):
    caracteristicas = Caracteristica.objects.all()
    return render(request, 'caracteristicas/lista.html', {'caracteristicas': caracteristicas})

def crear_caracteristica(request):
    if request.method == 'POST':
        form = CaracteristicaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Característica creada exitosamente.')
            return redirect('lista_caracteristicas')
    else:
        form = CaracteristicaForm()
    return render(request, 'caracteristicas/crear.html', {'form': form})

def editar_caracteristica(request, pk):
    caracteristica = get_object_or_404(Caracteristica, pk=pk)
    if request.method == 'POST':
        form = CaracteristicaForm(request.POST, instance=caracteristica)
        if form.is_valid():
            form.save()
            messages.success(request, 'Característica actualizada exitosamente.')
            return redirect('lista_caracteristicas')
    else:
        form = CaracteristicaForm(instance=caracteristica)
    return render(request, 'caracteristicas/editar.html', {'form': form, 'caracteristica': caracteristica})

def eliminar_caracteristica(request, pk):
    caracteristica = get_object_or_404(Caracteristica, pk=pk)
    if request.method == 'POST':
        caracteristica.delete()
        messages.success(request, 'Característica eliminada exitosamente.')
        return redirect('lista_caracteristicas')
    return render(request, 'caracteristicas/eliminar.html', {'caracteristica': caracteristica})




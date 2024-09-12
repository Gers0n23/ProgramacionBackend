from django.shortcuts import render, redirect
from .forms import ProductoForm
from .models import Producto

productos = []

def registro_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            productos.append(producto)
            return render(request, 'resultado.html', {'producto': producto})
    else:
        form = ProductoForm()
    return render(request, 'registro.html', {'form': form})

def consulta_productos(request):
    return render(request, 'consulta.html', {'productos': productos})
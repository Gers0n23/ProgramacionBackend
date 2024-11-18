from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .forms import ProductoForm, CaracteristicaForm
from .models import Producto, Categoria, Marca, Caracteristica
from django.db.models import Q
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.http import JsonResponse
import json

# Función para verificar si el usuario está en el grupo ADMIN_PRODUCTS
def is_product_admin(user):
    return user.groups.filter(name='ADMIN_PRODUCTS').exists()

# Decorador personalizado
def admin_products_required(view_func):
    decorated_view = user_passes_test(is_product_admin)(view_func)
    return login_required(decorated_view)

def custom_logout(request):
    logout(request)
    return redirect('/')

@require_http_methods(["GET", "POST"])
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Guardar datos en la sesión
            request.session['user_name'] = user.get_full_name() or user.username
            request.session['login_time'] = timezone.now().isoformat()
            request.session['is_admin_products'] = is_product_admin(user)
            return redirect('consulta_productos')  # Cambiado de 'lista_productos' a 'consulta_productos'
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'login.html')

@login_required
def registro_producto(request):
    if not request.session.get('is_admin_products', False):
        messages.error(request, 'No tiene permisos para registrar productos')
        return redirect('lista_productos')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            return redirect('resultado_producto', producto_id=producto.id)
    else:
        form = ProductoForm()
    return render(request, 'registro.html', {'form': form})

@login_required
def consulta_productos(request):
    productos = Producto.objects.all()
    
    # Búsqueda
    search = request.GET.get('search')
    if search:
        productos = productos.filter(nombre__icontains=search)

    # Filtros
    categoria = request.GET.get('categoria')
    marca = request.GET.get('marca')

    if categoria:
        productos = productos.filter(categoria__id=categoria)
    if marca:
        productos = productos.filter(marca__id=marca)

    context = {
        'productos': productos,
        'categorias': Categoria.objects.all(),
        'marcas': Marca.objects.all(),
    }
    return render(request, 'consulta.html', context)

@login_required
def resultado_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    return render(request, 'resultado.html', {'producto': producto})

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista.html', {'productos': productos})

@admin_products_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
        'login_time': request.session.get('login_time')
    })

@admin_products_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)  # Añadido request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar.html', {
        'form': form,
        'producto': producto,
        'user_name': request.session.get('user_name'),
        'login_time': request.session.get('login_time')
    })

@admin_products_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('lista_productos')
    return render(request, 'productos/eliminar.html', {
        'producto': producto,
        'user_name': request.session.get('user_name'),
        'login_time': request.session.get('login_time')
    })

# Vistas de Características
@login_required
def lista_caracteristicas(request):
    caracteristicas = Caracteristica.objects.all()
    return render(request, 'caracteristicas/lista.html', {
        'caracteristicas': caracteristicas,
        'user_name': request.session.get('user_name'),
        'login_time': request.session.get('login_time')
    })

@admin_products_required
def crear_caracteristica(request):
    if request.method == 'POST':
        form = CaracteristicaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Característica creada exitosamente.')
            return redirect('lista_caracteristicas')
    else:
        form = CaracteristicaForm()
    return render(request, 'caracteristicas/crear.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
        'login_time': request.session.get('login_time')
    })

@admin_products_required
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
    return render(request, 'caracteristicas/editar.html', {
        'form': form,
        'caracteristica': caracteristica,
        'user_name': request.session.get('user_name'),
        'login_time': request.session.get('login_time')
    })

@admin_products_required
def eliminar_caracteristica(request, pk):
    caracteristica = get_object_or_404(Caracteristica, pk=pk)
    if request.method == 'POST':
        caracteristica.delete()
        messages.success(request, 'Característica eliminada exitosamente.')
        return redirect('lista_caracteristicas')
    return render(request, 'caracteristicas/eliminar.html', {
        'caracteristica': caracteristica,
        'user_name': request.session.get('user_name'),
        'login_time': request.session.get('login_time')
    })

def get_cart(request):
    """Obtiene o inicializa el carrito en la sesión"""
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
    return cart

def obtener_detalles_carrito(cart):
    """Convierte el diccionario del carrito en una lista de items con detalles."""
    items = []
    for producto_id, item in cart.items():
        items.append({
            'id': producto_id,
            'nombre': item.get('nombre', ''),
            'precio': item.get('precio', 0.0),
            'cantidad': item.get('cantidad', 0),
            'subtotal': item.get('precio', 0.0) * item.get('cantidad', 0),
            'imagen': item.get('imagen', '')
        })
    return items

@require_http_methods(["POST"])
@login_required
def agregar_al_carrito(request):
    try:
        data = json.loads(request.body)
        producto_id = str(data.get('producto_id'))
        cantidad = int(data.get('cantidad', 1))
        
        if cantidad <= 0:
            return JsonResponse({'error': 'La cantidad debe ser positiva'}, status=400)
            
        cart = get_cart(request)
        producto = Producto.objects.get(id=producto_id)
        
        if producto_id in cart:
            cart[producto_id]['cantidad'] += cantidad
        else:
            cart[producto_id] = {
                'cantidad': cantidad,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'imagen': producto.imagen.url if producto.imagen else None
            }
            
        request.session['cart'] = cart
        total_items = sum(item['cantidad'] for item in cart.values())
        items = obtener_detalles_carrito(cart)
        
        return JsonResponse({
            'message': 'Producto agregado al carrito',
            'total_items': total_items,
            'items': items
        })
        
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
@login_required
def quitar_del_carrito(request):
    try:
        data = json.loads(request.body)
        producto_id = str(data.get('producto_id'))
        
        cart = get_cart(request)
        if producto_id in cart:
            del cart[producto_id]
            request.session['cart'] = cart
            total_items = sum(item['cantidad'] for item in cart.values())
            items = obtener_detalles_carrito(cart)
            return JsonResponse({
                'message': 'Producto eliminado del carrito',
                'total_items': total_items,
                'items': items
            })
        return JsonResponse({'error': 'Producto no encontrado en el carrito'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
@login_required
def actualizar_carrito(request):
    try:
        data = json.loads(request.body)
        producto_id = str(data.get('producto_id'))
        cantidad = int(data.get('cantidad'))
        
        if cantidad <= 0:
            return JsonResponse({'error': 'La cantidad debe ser positiva'}, status=400)
            
        cart = get_cart(request)
        if producto_id in cart:
            cart[producto_id]['cantidad'] = cantidad
            request.session['cart'] = cart
            total_items = sum(item['cantidad'] for item in cart.values())
            items = obtener_detalles_carrito(cart)
            return JsonResponse({
                'message': 'Carrito actualizado',
                'total_items': total_items,
                'items': items
            })
        return JsonResponse({'error': 'Producto no encontrado en el carrito'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def obtener_carrito(request):
    cart = get_cart(request)
    total_items = sum(item['cantidad'] for item in cart.values())
    items = obtener_detalles_carrito(cart)
    return JsonResponse({
        'items': items,
        'total_items': total_items
    })

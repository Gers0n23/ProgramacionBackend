"""
URL configuration for gestion_productos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from productos import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URL del administrador
    path('admin/', admin.site.urls),
    
    # URLs de autenticación
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # URLs para Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('registro/', views.registro_producto, name='registro_producto'),
    path('consulta/', views.consulta_productos, name='consulta_productos'),
    path('resultado/<int:producto_id>/', views.resultado_producto, name='resultado_producto'),
    
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    
    # URLs para Características
    path('caracteristicas/', views.lista_caracteristicas, name='lista_caracteristicas'),
    path('caracteristica/crear/', views.crear_caracteristica, name='crear_caracteristica'),
    path('caracteristica/editar/<int:pk>/', views.editar_caracteristica, name='editar_caracteristica'),
    path('caracteristica/eliminar/<int:pk>/', views.eliminar_caracteristica, name='eliminar_caracteristica'),
    
    # URLs Carrito de compras
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/quitar/', views.quitar_del_carrito, name='quitar_del_carrito'),
    path('carrito/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/cargar/', views.obtener_carrito, name='cargar_carrito'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
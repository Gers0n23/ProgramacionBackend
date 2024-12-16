from django.contrib import admin
from .models import Producto, Categoria, Marca, Caracteristica

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio', 'marca', 'categoria', 'fecha_vencimiento')
    list_filter = ('marca', 'categoria')
    search_fields = ('codigo', 'nombre')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Caracteristica)
class CaracteristicaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
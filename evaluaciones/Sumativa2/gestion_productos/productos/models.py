from django.db import models
from django import forms

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Caracteristica(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    caracteristicas = models.ManyToManyField(Caracteristica)
    fecha_vencimiento = models.DateField()

    def __str__(self):
        return self.nombre
    
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'precio', 'marca', 'categoria', 'caracteristicas', 'fecha_vencimiento']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'caracteristicas': forms.CheckboxSelectMultiple(),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
        labels = {
            'codigo': 'Código del Producto',
            'nombre': 'Nombre del Producto',
            'precio': 'Precio ($)',
            'marca': 'Marca',
            'categoria': 'Categoría',
            'caracteristicas': 'Características',
            'fecha_vencimiento': 'Fecha de Vencimiento',
        }

class CaracteristicaForm(forms.ModelForm):
    class Meta:
        model = Caracteristica
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ingrese el nombre de la característica'})
        }
        labels = {
            'nombre': 'Nombre de la Característica'
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombre = nombre.strip()
            if len(nombre) < 2:
                raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return nombre
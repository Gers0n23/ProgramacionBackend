from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'marca', 'fecha_vencimiento']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
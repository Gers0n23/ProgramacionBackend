from django import forms
from .models import Producto, Categoria, Marca, Caracteristica

class ProductoForm(forms.ModelForm):
    caracteristicas = forms.ModelMultipleChoiceField(
        queryset=Caracteristica.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'precio', 'marca', 'categoria', 'caracteristicas', 'fecha_vencimiento']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()
        self.fields['marca'].queryset = Marca.objects.all()
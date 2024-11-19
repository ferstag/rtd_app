from django import forms
from .models import Pedido
from django.core.exceptions import ValidationError

class FormularioForm(forms.ModelForm):
    nombre_cliente = forms.CharField()
    email = forms.EmailField()
    telefono_cliente = forms.IntegerField()
    comentario = forms.CharField(max_length=200)
    
    nombre_cliente.widget.attrs['class'] = 'form-control'
    email.widget.attrs['class'] = 'form-control'
    telefono_cliente.widget.attrs['class'] = 'form-control'
    comentario.widget.attrs['class'] = 'form-control'

    def clean_telefono_cliente(self):
        telefono = self.cleaned_data.get('telefono_cliente')
        if len(str(telefono)) != 10:
            raise ValidationError('El número de contacto debe tener 10 dígitos.')
        return telefono

    def clean_comentario(self):
        comentario = self.cleaned_data.get('comentario')
        if len(comentario) > 200:
            raise ValidationError('El comentario debe tener menos de 200 caracteres.')
        return comentario

    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'email', 'telefono_cliente', 'comentario']
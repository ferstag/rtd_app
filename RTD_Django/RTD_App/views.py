from django.shortcuts import render

from django.shortcuts import render
from .models import Producto
from django.db.models import Sum, Max

def catalogo(request):
    productos = Producto.objects.all().order_by("nombre")
    stock_total = Producto.objects.aggregate(Sum("stock"))
    mayor_precio = Producto.objects.aggregate(Max("precio"))
    data = {
        'producto':productos,
        'stock_total': stock_total['stock__sum'],
        'mayor_precio': mayor_precio['precio__max'],
    }
    
    return render (request, 'catalogo.html', data)

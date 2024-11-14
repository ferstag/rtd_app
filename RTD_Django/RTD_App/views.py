from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, Pedido
from django.db.models import Sum, Max
from django.contrib import messages

def catalogo(request):
    productos = Producto.objects.all().order_by("nombre")
    stock_total = Producto.objects.aggregate(Sum("stock"))
    mayor_precio = Producto.objects.aggregate(Max("precio"))
    data = {
        'productos':productos,
        'stock_total': stock_total['stock__sum'],
        'mayor_precio': mayor_precio['precio__max'],
    }
    
    return render (request, 'catalogo.html', data)


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    
    if producto.stock < cantidad:
        messages.error(request, "Stock insuficiente.")
    else:
        carrito_item, created = Carrito.objects.get_or_create(item=producto, defaults={'cantidad': 0, 'subtotal': 0, 'total': 0})
        
        # Actualizamos la cantidad y subtotal
        carrito_item.cantidad += cantidad
        carrito_item.subtotal = carrito_item.cantidad * producto.precio
        carrito_item.total = carrito_item.subtotal  # Aseguramos que total tenga un valor válido
        
        carrito_item.save()
        
        messages.success(request, f"{producto.nombre} añadido al carrito.")
    
    return redirect('carrito')


# Remove Product from Cart
def eliminar_del_carrito(request, producto_id):
    carrito_item = get_object_or_404(Carrito, item_id=producto_id)
    carrito_item.delete()
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('carrito')

# View Cart
def carrito(request):
    carrito_items = Carrito.objects.all()
    total = sum(item.subtotal for item in carrito_items)
    return render(request, 'carrito.html', {'carrito_items': carrito_items, 'total': total})


# Modify Product Quantity in Cart
def modificar_cantidad(request, producto_id):
    carrito_item = get_object_or_404(Carrito, item_id=producto_id)
    nueva_cantidad = int(request.POST.get('cantidad'))
    if nueva_cantidad <= 0:
        messages.error(request, "La cantidad debe ser mayor a cero.")
    elif carrito_item.item.stock < nueva_cantidad:
        messages.error(request, "Stock insuficiente.")
    else:
        carrito_item.cantidad = nueva_cantidad
        carrito_item.subtotal = carrito_item.item.precio * nueva_cantidad
        carrito_item.total = sum(item.subtotal for item in Carrito.objects.all())
        carrito_item.save()
        messages.success(request, "Cantidad modificada.")
    return redirect('carrito')

# Empty Cart
def vaciar_carrito(request):
    Carrito.objects.all().delete()
    messages.success(request, "Carrito vacío.")
    return redirect('carrito')

# Confirm Purchase
def confirmar_compra(request):
    carrito_items = Carrito.objects.all()
    if not carrito_items:
        messages.error(request, "El carrito está vacío.")
        return redirect('carrito')
    
    # Create order
    #pedido = Pedido.objects.create(
        #nombre_cliente=request.POST.get('nombre_cliente'),
        #email=request.POST.get('email'),
        #telefono_cliente=request.POST.get('telefono_cliente'),
        #comentario=request.POST.get('comentario', '')
    #)
    
    for item in carrito_items:
        pedido.productos.add(item.item)  # Assuming Pedido has a ManyToManyField to Producto
    
    messages.success(request, "Compra confirmada.")
    return redirect('generar_voucher')

# Generate Voucher
def generar_voucher(request):
    carrito_items = Carrito.objects.all()
    total = sum(item.subtotal for item in carrito_items)
    return render(request, 'voucher.html', {'carrito_items': carrito_items, 'total': total})
    

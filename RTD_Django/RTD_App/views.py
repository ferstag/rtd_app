from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, Pedido
from django.db.models import Sum, Max
from django.contrib import messages
from .forms import FormularioForm

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
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib import messages
    from .models import Producto, Carrito

    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if producto.stock < cantidad:
        messages.error(request, "Stock insuficiente.")
        return redirect('catalogo')

    # Verificar o crear la clave de sesión
    if not request.session.session_key:
        request.session.create()
    
    session_id = request.session.session_key  # Obtener el ID de la sesión actual

    # Obtener o crear un carrito para esta sesión y producto
    carrito_item, created = Carrito.objects.get_or_create(
        session_id=session_id,
        item=producto,
        defaults={'cantidad': 0, 'subtotal': 0, 'total': 0}
    )

    # Actualizar cantidad y subtotal
    carrito_item.cantidad += cantidad
    carrito_item.subtotal = carrito_item.cantidad * producto.precio
    carrito_item.save()

    # Calcular el total del carrito sumando los subtotales
    total_carrito = Carrito.objects.filter(session_id=session_id).aggregate(total=Sum('subtotal'))['total']


    # Actualizar el total en todos los items del carrito (si es necesario)
    Carrito.objects.filter(session_id=session_id).update(total=total_carrito)

    messages.success(request, f"{producto.nombre} añadido al carrito.")
    return redirect('carrito', carrito_id=session_id)

# Remove Product from Cart
def eliminar_del_carrito(request, producto_id):
    # Verifica que el usuario tenga una sesión activa
    if not request.session.session_key:
        messages.error(request, "No se encontró una sesión activa.")
        return redirect('catalogo')

    # Filtra por session_id y item_id para obtener el carrito específico
    session_id = request.session.session_key
    carrito_item = get_object_or_404(Carrito, item_id=producto_id, session_id=session_id)

    carrito_item.delete()
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('carrito', carrito_id=session_id)


# View Cart
def carrito(request, carrito_id):
    carrito_items = Carrito.objects.filter(session_id=carrito_id)
    total = sum(item.subtotal for item in carrito_items)
    return render(request, 'carrito.html', {
        'carrito_items': carrito_items,
        'total': total,
        'carrito_id': carrito_id  # Asegura que el ID del carrito esté en el contexto
    })


# Modify Product Quantity in Cart
def modificar_cantidad(request, producto_id):
    # Filtramos también por el session_id para obtener el carrito correspondiente a la sesión actual
    carrito_item = get_object_or_404(Carrito, item_id=producto_id, session_id=request.session.session_key)
    
    nueva_cantidad = int(request.POST.get('cantidad'))
    
    if nueva_cantidad <= 0:
        messages.error(request, "La cantidad debe ser mayor a cero.")
    elif carrito_item.item.stock < nueva_cantidad:
        messages.error(request, "Stock insuficiente.")
    else:
        carrito_item.cantidad = nueva_cantidad
        carrito_item.subtotal = carrito_item.item.precio * nueva_cantidad
        carrito_item.total = sum(item.subtotal for item in Carrito.objects.filter(session_id=request.session.session_key))
        carrito_item.save()
        messages.success(request, "Cantidad modificada.")
    
    return redirect('carrito', carrito_id=request.session.session_key)

# Empty Cart
def vaciar_carrito(request, carrito_id):
    Carrito.objects.filter(session_id=carrito_id).delete()
    messages.success(request, "Carrito vacío.")
    return redirect('carrito', carrito_id=carrito_id)



# Confirm Purchase
def confirmar_compra(request):
    carrito_items = Carrito.objects.all()
    if not carrito_items:
        messages.error(request, "El carrito está vacío.")
        return redirect('carrito')

    for item in carrito_items:
        pedido.productos.add(item.item)  # Assuming Pedido has a ManyToManyField to Producto
    
    messages.success(request, "Compra confirmada.")
    return redirect('generar_voucher')


# Generate Voucher
def generar_voucher(request, carrito_id):
    # Buscar el carrito utilizando el session_id
    carrito_items = Carrito.objects.filter(session_id=carrito_id)  # Usar session_id para el filtro
    if not carrito_items:
        messages.error(request, "Carrito no encontrado.")
        return redirect('carrito')

    total = sum(item.subtotal for item in carrito_items)

    return render(request, 'voucher.html', {
        'carrito_items': carrito_items,
        'total': total
    })



def formulario(request):
    if request.method == 'POST':
        form = FormularioForm(request.POST)
        if form.is_valid():
            form.save() 
    else:
        form = FormularioForm()

    return render(request, 'formulario.html', {'form': form})

def landingPage(request):
    return render(request, 'landing.html')

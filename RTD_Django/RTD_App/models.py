from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.TextField(max_length=255)
    precio = models.IntegerField()
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='productos')

class Pedido(models.Model):
    nombre_cliente = models.CharField(max_length=50)
    email = models.EmailField()
    telefono_cliente = models.PositiveIntegerField()
    comentario = models.TextField(max_length=200)

class Carrito(models.Model):
    item = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    total = models.PositiveIntegerField()

    def __str__(self):
        return f"Total Carrito: ${self.total}" 
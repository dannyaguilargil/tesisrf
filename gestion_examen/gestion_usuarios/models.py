from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class imagenes(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario autenticado', blank=True, null=True )
    imagen = models.ImageField(upload_to='imgs/', blank=True, null=True )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
  
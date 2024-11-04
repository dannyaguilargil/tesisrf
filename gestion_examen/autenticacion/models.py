from django.db import models
from django.contrib.auth.models import User
from  gestion_examenes.models import  examen

class autenticacion(models.Model):
    id = models.AutoField(primary_key=True)
    examen=models.ForeignKey(examen,on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario autenticado')
    reconocimientofacial = models.BooleanField(default=False, verbose_name='Reconocimiento facial')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Id:{self.id} - Examen {self.examen} "
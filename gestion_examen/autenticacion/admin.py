from django.contrib import admin
from .models import  autenticacion

# Register your models here.
class Autenticacion(admin.ModelAdmin):
    list_display=('id', 'examen', 'usuario', 'reconocimientofacial', 'fecha_actualizacion')
    search_fields = ('id',)
admin.site.register(autenticacion, Autenticacion)
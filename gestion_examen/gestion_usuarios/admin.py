from django.contrib import admin
from .models import  imagenes
from django.utils.html import format_html
import os
# Register your models here.
class Imagen(admin.ModelAdmin):
    list_display=('id','usuario','fecha_creacion','fecha_actualizacion','imagen')
    search_fields = ('usuario',)#cuadrito de busqueda dentro del panel de administracion


    def display_imagen(self, obj):
            if obj.imagen:
                file_url = obj.imagen.url
                file_url = file_url.replace('/gestion_examen/', '/')
                #file_url = reverse('sistemas_cuentas:archivo', args=[obj.numero])
                return format_html('<a href="{}" target="_blank";>Ver imagen</a>', file_url)
            else:
                return '-'
    display_imagen.short_description = 'Archivo'


admin.site.register(imagenes, Imagen)
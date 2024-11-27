from django.contrib import admin
from .models import  modalidad,semestre,carrera,materia,seccion,planificacion,examen,pregunta,opcion,respuestaexamen,respuesta
from django.contrib import admin
from django.utils.html import format_html



# Register your models here.
class Modalidad(admin.ModelAdmin):
    list_display=('id', 'descripcion', 'fecha_creacion', 'fecha_actualizacion')
    search_fields = ('id',)
admin.site.register(modalidad, Modalidad)

class Semestre(admin.ModelAdmin):
    list_display=('id', 'periodo', 'fechainicio', 'fechafinal','fecha_creacion')
    search_fields = ('id',)
admin.site.register(semestre, Semestre)

class Carrera(admin.ModelAdmin):
    list_display=('id', 'nombre', 'modalidad', 'semestre', 'fecha_creacion')
    search_fields = ('id',)
admin.site.register(carrera, Carrera)

class Materia(admin.ModelAdmin):
    list_display=('id', 'nombre', 'carrera', 'fecha_creacion')
    search_fields = ('id',)
admin.site.register(materia, Materia)

class Seccion(admin.ModelAdmin):
    list_display=('id', 'descripcion', 'fecha_creacion', 'fecha_actualizacion')
    search_fields = ('id',)
admin.site.register(seccion, Seccion)

class Planificacion(admin.ModelAdmin):
    list_display=('id', 'materia', 'seccion', 'usuario', 'fecha_actualizacion')
    search_fields = ('id',)
admin.site.register(planificacion, Planificacion)

class PreguntaInline(admin.TabularInline):
    model = pregunta
    extra = 0  # Número de formularios vacíos adicionales a mostrar

class Examen(admin.ModelAdmin):
    list_display=('id', 'fechainicio', 'fechafinal', 'cantidadpreguntas', 'duracion', 'fecha_actualizacion')
    inlines = [PreguntaInline]
    search_fields = ('id',)
    def save_model(self, request, obj, form, change):
        # Llama al método original para guardar el examen
        super().save_model(request, obj, form, change)

        # Si es un nuevo examen
        if not change:
            cantidad_preguntas = obj.cantidadpreguntas
            preguntas_existentes = pregunta.objects.filter(examen=obj).count()

            # Crear preguntas vacías solo si no hay suficientes preguntas
            if preguntas_existentes < cantidad_preguntas:
                for _ in range(cantidad_preguntas - preguntas_existentes):
                    pregunta.objects.create(examen=obj, texto='')  # Crea preguntas vacías

        # Si se está editando un examen existente
        else:
            # Obtener las preguntas enviadas desde el formulario
            preguntas_enviadas = form.cleaned_data.get('pregunta_set', [])
            preguntas_enviadas_count = len(preguntas_enviadas)

            # Calcular cuántas preguntas adicionales son necesarias
            if preguntas_enviadas_count < obj.cantidadpreguntas:
                for _ in range(obj.cantidadpreguntas - preguntas_enviadas_count):
                    pregunta.objects.create(examen=obj, texto='')  # Crea preguntas vacías

admin.site.register(examen, Examen)

class Pregunta(admin.ModelAdmin):
    list_display=('examen', 'texto', 'fecha_actualizacion')
    search_fields = ('id',)
admin.site.register(pregunta, Pregunta)

class Opcion(admin.ModelAdmin):
    list_display=('pregunta', 'texto', 'es_correcta')
    search_fields = ('pregunta',)
admin.site.register(opcion, Opcion)

class RespuestaExamen(admin.ModelAdmin):
    list_display=('examen', 'usuario', 'fecha_respuesta')
    search_fields = ('examen',)
admin.site.register(respuestaexamen, RespuestaExamen)

class Respuesta(admin.ModelAdmin):
    list_display=('respuesta_examen', 'pregunta', 'opcion_seleccionada','es_correcta')
    search_fields = ('examen',)
admin.site.register(respuesta, Respuesta)




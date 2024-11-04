from django.db import models
from django.contrib.auth.models import User

class modalidad(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.TextField() 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.descripcion

class semestre(models.Model):
    id = models.AutoField(primary_key=True)
    periodo = models.IntegerField()
    fechainicio = models.DateField(verbose_name='Fecha inicial', null=True,blank=True)
    fechafinal = models.DateField(verbose_name='Fecha final', null=True,blank=True)
    descripcion = models.TextField() 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.descripcion

class carrera(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, verbose_name='Nombre de la carrera')
    modalidad=models.ForeignKey(modalidad,on_delete=models.CASCADE) 
    semestre=models.ForeignKey(semestre,on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nombre
    
class materia(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, verbose_name='Nombre de la materia')
    carrera=models.ForeignKey(carrera,on_delete=models.CASCADE) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nombre
    
class seccion(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.TextField() 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.descripcion

class planificacion(models.Model):
    id = models.AutoField(primary_key=True)
    materia=models.ForeignKey(materia,on_delete=models.CASCADE) 
    seccion=models.ForeignKey(seccion,on_delete=models.CASCADE) 
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario autenticado', blank=True, null=True )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.materia} - Sección: {self.seccion}"

class examen(models.Model):
    id = models.AutoField(primary_key=True)
    fechainicio = models.DateField(verbose_name='Fecha inicial')
    fechafinal = models.DateField(verbose_name='Fecha final')
    cantidadpreguntas = models.IntegerField(verbose_name='Cantidad de preguntas')
    duracion = models.DurationField(help_text="Duración del examen en minutos")
    nintentos = models.IntegerField(verbose_name='Numero de intentos')
    planificacion=models.ForeignKey(planificacion,on_delete=models.CASCADE) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Planificacion {self.planificacion} "
    
class pregunta(models.Model):
    examen = models.ForeignKey(examen, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pregunta: {self.texto}"
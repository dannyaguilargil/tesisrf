from django.shortcuts import render,redirect
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import examen, pregunta

def staff_required(user):
    return user.is_staff 

def examenes(request):
    username = request.user.username
    es_staff = request.user.is_staff
    return render(request, 'examenes.html', {'username': username, 'es_staff': es_staff})

def presentarexamen(request):
  
    username = request.user.username
    es_staff = request.user.is_staff


    fecha_actual = timezone.now().date()

 
    examen_obj = examen.objects.filter(
        fechainicio__lte=fecha_actual,   
        fechafinal__gte=fecha_actual     
    ).select_related('planificacion').first()  

    if examen_obj:
       
        preguntas = pregunta.objects.filter(examen=examen_obj)
        return render(request, 'presentar_examen.html', {
            'examen': examen_obj,
            'preguntas': preguntas,
            'username': username,
            'es_staff': es_staff
        })
    else:
        
        return render(request, 'examen_no_disponible.html', {
            'mensaje': 'No hay exámenes disponibles en esta fecha.',
            'username': username,
            'es_staff': es_staff
        })
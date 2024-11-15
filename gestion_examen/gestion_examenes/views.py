from django.shortcuts import render,redirect
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import examen, pregunta
import cv2
import base64
import numpy as np
from django.core.files.base import ContentFile
from gestion_usuarios.models import imagenes
from .forms import ExamenForm, PreguntaForm

def staff_required(user):
    return user.is_staff 

def examenes(request):
    username = request.user.username
    es_staff = request.user.is_staff
    fecha_actual = timezone.now().date()

    
    examen_obj = examen.objects.filter(
        fechainicio__lte=fecha_actual,
        fechafinal__gte=fecha_actual
    ).select_related('planificacion').first()

    if request.method == 'POST' and 'image_data' in request.POST:
        # Decodificar la imagen enviada en base64
        image_data = request.POST['image_data']
        format, imgstr = image_data.split(';base64,')
        image_data = ContentFile(base64.b64decode(imgstr), name='captura.png')

        # Convertir la imagen base64 a un formato que OpenCV pueda usar
        np_img = np.frombuffer(image_data.read(), np.uint8)
        captura_image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # Cargar la imagen de referencia del usuario desde el modelo `imagenes`
        try:
            imagen_referencia = imagenes.objects.get(usuario=request.user).imagen.path
            referencia_image = cv2.imread(imagen_referencia)

            # Convertir las imágenes a escala de grises
            gray_captura = cv2.cvtColor(captura_image, cv2.COLOR_BGR2GRAY)
            gray_referencia = cv2.cvtColor(referencia_image, cv2.COLOR_BGR2GRAY)

            # Cargar el clasificador de rostros de OpenCV
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Detectar rostros en ambas imágenes
            rostros_captura = face_cascade.detectMultiScale(gray_captura, scaleFactor=1.1, minNeighbors=5)
            rostros_referencia = face_cascade.detectMultiScale(gray_referencia, scaleFactor=1.1, minNeighbors=5)

            # Verificar si hay un rostro detectado en ambas imágenes
            if len(rostros_captura) > 0 and len(rostros_referencia) > 0:
                # Extraer la primera región de rostro detectada para ambas imágenes
                (x, y, w, h) = rostros_captura[0]
                captura_rostro = gray_captura[y:y+h, x:x+w]

                (x, y, w, h) = rostros_referencia[0]
                referencia_rostro = gray_referencia[y:y+h, x:x+w]

                
                captura_rostro = cv2.resize(captura_rostro, (100, 100))
                referencia_rostro = cv2.resize(referencia_rostro, (100, 100))

              
                hist_captura = cv2.calcHist([captura_rostro], [0], None, [256], [0, 256])
                hist_referencia = cv2.calcHist([referencia_rostro], [0], None, [256], [0, 256])
                correlacion = cv2.compareHist(hist_captura, hist_referencia, cv2.HISTCMP_CORREL)

             
                if correlacion > 0.2: 
                    return render(request, 'examenes.html', {
                        'examen': examen_obj,
                        'preguntas': pregunta.objects.filter(examen=examen_obj),
                        'username': username,
                        'es_staff': es_staff,
                        'mensaje': "Reconocimiento facial exitoso, puedes iniciar el examen."
                        
                    })
                else:
                    return render(request, 'examenes.html', {
                        'mensaje': "El rostro no coincide con el usuario autenticado. Inténtalo de nuevo.",
                        'username': username,
                        'es_staff': es_staff
                    })
            else:
                return render(request, 'examenes.html', {
                    'mensaje': "No se pudo detectar un rostro en la imagen capturada. Inténtalo de nuevo.",
                    'username': username,
                    'es_staff': es_staff
                })
        except imagenes.DoesNotExist:
            return render(request, 'examenes.html', {
                'mensaje': "No se encontró una imagen de referencia para el usuario.",
                'username': username,
                'es_staff': es_staff
            })

    # Si no se envía una imagen, mostrar el examen o el mensaje de no disponible
    if examen_obj:
        preguntas = pregunta.objects.filter(examen=examen_obj)
        return render(request, 'examenes.html', {
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
    
@login_required
def crear_examen(request):
    
    username = request.user.username
    es_staff = request.user.is_staff
    if request.method == 'POST':
        examen_form = ExamenForm(request.POST)
        if examen_form.is_valid():
            # Guardar el examen
            nuevo_examen = examen_form.save()

            # Crear preguntas automáticamente si se especifica una cantidad
            cantidad_preguntas = nuevo_examen.cantidadpreguntas
            preguntas_creadas = []
            for i in range(cantidad_preguntas):
                preguntas_creadas.append(
                    pregunta(examen=nuevo_examen, texto=f'Pregunta {i+1}')
                )
            pregunta.objects.bulk_create(preguntas_creadas)

            return redirect('crear_examen')  # Redirige a una lista de exámenes o donde prefieras
    else:
        examen_form = ExamenForm()

    return render(request, 'crearexamen.html',{
        'examen_form': examen_form,
        'username': username,
        'es_staff': es_staff,

    })
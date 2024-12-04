from django.shortcuts import render,redirect
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import examen, pregunta,opcion, respuestaexamen,respuesta
import cv2
import base64
import numpy as np
from django.core.files.base import ContentFile
from gestion_usuarios.models import imagenes
from .forms import ExamenForm, PreguntaForm,OpcionForm
from django.forms import modelformset_factory, inlineformset_factory
from django.forms import modelformset_factory
from django.contrib import messages

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

    imagen_base64_referencia = None

    try:
      
        imagen_referencia = imagenes.objects.get(usuario=request.user).imagen
        with open(imagen_referencia.path, "rb") as img_file:
            imagen_base64_referencia = base64.b64encode(img_file.read()).decode('utf-8')
    except imagenes.DoesNotExist:
        imagen_base64_referencia = None 

    if request.method == 'POST' and 'image_data' in request.POST:
      
        image_data = request.POST['image_data']
        format, imgstr = image_data.split(';base64,')
        image_data = ContentFile(base64.b64decode(imgstr), name='captura.png')

    
        np_img = np.frombuffer(image_data.read(), np.uint8)
        captura_image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        try:
          
            imagen_referencia = imagenes.objects.get(usuario=request.user).imagen.path
            referencia_image = cv2.imread(imagen_referencia)

            gray_captura = cv2.cvtColor(captura_image, cv2.COLOR_BGR2GRAY)
            gray_referencia = cv2.cvtColor(referencia_image, cv2.COLOR_BGR2GRAY)

      
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

  
            rostros_captura = face_cascade.detectMultiScale(gray_captura, scaleFactor=1.1, minNeighbors=5)
            rostros_referencia = face_cascade.detectMultiScale(gray_referencia, scaleFactor=1.1, minNeighbors=5)

    
            if len(rostros_captura) > 0 and len(rostros_referencia) > 0:
            
                (x, y, w, h) = rostros_captura[0]
                captura_rostro = gray_captura[y:y+h, x:x+w]

                (x, y, w, h) = rostros_referencia[0]
                referencia_rostro = gray_referencia[y:y+h, x:x+w]

                
                captura_rostro = cv2.resize(captura_rostro, (100, 100))
                referencia_rostro = cv2.resize(referencia_rostro, (100, 100))

                # Comparar histogramas
                hist_captura = cv2.calcHist([captura_rostro], [0], None, [256], [0, 256])
                hist_referencia = cv2.calcHist([referencia_rostro], [0], None, [256], [0, 256])
                correlacion = cv2.compareHist(hist_captura, hist_referencia, cv2.HISTCMP_CORREL)

             
                cv2.rectangle(captura_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.rectangle(referencia_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

               
                print(f"Correlación: {correlacion}")

                if correlacion > 0.6:  
                    return render(request, 'examenes.html', {
                        'examen': examen_obj,
                        'preguntas': pregunta.objects.filter(examen=examen_obj),
                        'username': username,
                        'es_staff': es_staff,
                        'mensaje': "Reconocimiento facial exitoso, puedes iniciar el examen.",
                        'imagen_base64_referencia': imagen_base64_referencia,  # Imagen de referencia
                    })
                else:
                    return render(request, 'examenes.html', {
                        'mensaje': "El rostro no coincide con el usuario autenticado. Inténtalo de nuevo.",
                        'username': username,
                        'es_staff': es_staff,
                        'imagen_base64_referencia': imagen_base64_referencia,
                    })
            else:
                return render(request, 'examenes.html', {
                    'mensaje': "No se pudo detectar un rostro en la imagen capturada. Inténtalo de nuevo.",
                    'username': username,
                    'es_staff': es_staff,
                    'imagen_base64_referencia': imagen_base64_referencia,
                })
        except imagenes.DoesNotExist:
            return render(request, 'examenes.html', {
                'mensaje': "No se encontró una imagen de referencia para el usuario.",
                'username': username,
                'es_staff': es_staff,
                'imagen_base64_referencia': imagen_base64_referencia,
            })

    if examen_obj:
        preguntas = pregunta.objects.filter(examen=examen_obj)
        return render(request, 'examenes.html', {
            'examen': examen_obj,
            'preguntas': preguntas,
            'username': username,
            'es_staff': es_staff,
            'imagen_base64_referencia': imagen_base64_referencia,  
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

    if not examen_obj:
        return render(request, 'examen_no_disponible.html', {
            'mensaje': 'No hay exámenes disponibles en esta fecha.',
            'username': username,
            'es_staff': es_staff
        })


    preguntas = pregunta.objects.filter(examen=examen_obj).prefetch_related('opciones')

    if request.method == 'POST':
  
        respuesta_examen = respuestaexamen.objects.create(
            examen=examen_obj,
            usuario=request.user
        )

        correctas = 0
     
        for pregunta_obj in preguntas:
            respuesta_id = request.POST.get(f"respuesta_{pregunta_obj.id}")
            if respuesta_id:
                respuesta_opcion = opcion.objects.get(id=respuesta_id)
                es_correcta = respuesta_opcion.es_correcta

              
                respuesta.objects.create(
                    respuesta_examen=respuesta_examen,
                    pregunta=pregunta_obj,
                    opcion_seleccionada=respuesta_opcion,
                    es_correcta=es_correcta
                )

                if es_correcta:
                    correctas += 1

     
        total_preguntas = preguntas.count()
        resultado = {
            'correctas': correctas,
            'incorrectas': total_preguntas - correctas,
            'total': total_preguntas,
            'porcentaje': (correctas / total_preguntas) * 100
        }

        return render(request, 'resultado_examen.html', {
            'examen': examen_obj,
            'resultado': resultado,
            'username': username,
        })

    return render(request, 'presentar_examen.html', {
        'examen': examen_obj,
        'preguntas': preguntas,
        'username': username,
        'es_staff': es_staff
    })

@login_required
def crear_examen(request):
    username = request.user.username
    es_staff = request.user.is_staff

    PreguntaFormSet = modelformset_factory(
        pregunta,
        form=PreguntaForm,
        extra=1  
    )

    if request.method == 'POST':
        examen_form = ExamenForm(request.POST)
        pregunta_formset = PreguntaFormSet(request.POST, prefix='preguntas')

        if examen_form.is_valid() and pregunta_formset.is_valid():
       
            nuevo_examen = examen_form.save()

           
            for pregunta_form in pregunta_formset:
                if pregunta_form.cleaned_data:
                    nueva_pregunta = pregunta_form.save(commit=False)
                    nueva_pregunta.examen = nuevo_examen
                    nueva_pregunta.save()

                 
                    for i in range(1, 5):  
                        opcion_texto = request.POST.get(f'opciones_{pregunta_form.prefix}_{i}')
                        es_correcta = request.POST.get(f'es_correcta_{pregunta_form.prefix}_{i}')

                        if opcion_texto:
                            nueva_opcion = opcion(
                                pregunta=nueva_pregunta,
                                texto=opcion_texto,
                                es_correcta=(es_correcta == 'on')
                            )
                            nueva_opcion.save()

            messages.success(request, "Examen creado con éxito.")
            return redirect('crear_examen')  

    else:
        examen_form = ExamenForm()
        pregunta_formset = PreguntaFormSet(queryset=pregunta.objects.none(), prefix='preguntas')

    return render(request, 'crearexamen.html', {
        'examen_form': examen_form,
        'pregunta_formset': pregunta_formset,
        'username': username,
        'es_staff': es_staff,
    })

@login_required
def inicioexamen(request):
    username = request.user.username
    es_staff = request.user.is_staff

    # Obtener los exámenes creados por el usuario (puedes filtrar por otros criterios si lo deseas)
    examenes = examen.objects.all().order_by('-fecha_creacion')  # Obtiene los exámenes más recientes primero

    return render(request, 'areapersonal.html', {
        'username': username,
        'es_staff': es_staff,
        'examenes': examenes  # Pasamos los exámenes al template
    })
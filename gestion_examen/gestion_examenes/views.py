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
        # Obtener la imagen de referencia del usuario desde el modelo imagenes
        imagen_referencia = imagenes.objects.get(usuario=request.user).imagen
        with open(imagen_referencia.path, "rb") as img_file:
            imagen_base64_referencia = base64.b64encode(img_file.read()).decode('utf-8')

    except imagenes.DoesNotExist:
        imagen_base64_referencia = None  # Si no hay imagen de referencia

    if request.method == 'POST' and 'image_data' in request.POST:
        # Decodificar la imagen enviada en base64
        image_data = request.POST['image_data']
        format, imgstr = image_data.split(';base64,')
        image_data = ContentFile(base64.b64decode(imgstr), name='captura.png')

        # Convertir la imagen base64 a un formato que OpenCV pueda usar
        np_img = np.frombuffer(image_data.read(), np.uint8)
        captura_image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        try:
            # Cargar la imagen de referencia del usuario desde el modelo imagenes
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

                # Redimensionar rostros para comparación
                captura_rostro = cv2.resize(captura_rostro, (100, 100))
                referencia_rostro = cv2.resize(referencia_rostro, (100, 100))

                # Comparar histogramas
                hist_captura = cv2.calcHist([captura_rostro], [0], None, [256], [0, 256])
                hist_referencia = cv2.calcHist([referencia_rostro], [0], None, [256], [0, 256])
                correlacion = cv2.compareHist(hist_captura, hist_referencia, cv2.HISTCMP_CORREL)

                # Mostrar áreas detectadas en ambas imágenes para debugging
                cv2.rectangle(captura_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.rectangle(referencia_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Mostrar correlación en consola para depuración
                print(f"Correlación: {correlacion}")

                if correlacion > 0.6:  # Reconocimiento facial más estricto
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
            'imagen_base64_referencia': imagen_base64_referencia,  # Imagen de referencia
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

    # Obtener el examen actual en función de la fecha
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

    # Obtener preguntas y opciones relacionadas
    preguntas = pregunta.objects.filter(examen=examen_obj).prefetch_related('opciones')

    if request.method == 'POST':
        # Crear una nueva respuesta para el examen del estudiante
        respuesta_examen = respuestaexamen.objects.create(
            examen=examen_obj,
            usuario=request.user
        )

        correctas = 0
        # Procesar las respuestas enviadas
        for pregunta_obj in preguntas:
            respuesta_id = request.POST.get(f"respuesta_{pregunta_obj.id}")
            if respuesta_id:
                respuesta_opcion = opcion.objects.get(id=respuesta_id)
                es_correcta = respuesta_opcion.es_correcta

                # Guardar la respuesta
                respuesta.objects.create(
                    respuesta_examen=respuesta_examen,
                    pregunta=pregunta_obj,
                    opcion_seleccionada=respuesta_opcion,
                    es_correcta=es_correcta
                )

                if es_correcta:
                    correctas += 1

        # Calcular resultado
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
        extra=1  # Número inicial de preguntas
    )
    OpcionFormSet = modelformset_factory(
        opcion,
        form=OpcionForm,
        extra=4  # Número inicial de opciones
    )

    if request.method == 'POST':
        examen_form = ExamenForm(request.POST)
        pregunta_formset = PreguntaFormSet(request.POST, prefix='preguntas')

        if examen_form.is_valid() and pregunta_formset.is_valid():
            # Guardar el examen
            nuevo_examen = examen_form.save()

            # Procesar las preguntas
            for pregunta_form in pregunta_formset:
                if pregunta_form.cleaned_data:
                    nueva_pregunta = pregunta_form.save(commit=False)
                    nueva_pregunta.examen = nuevo_examen
                    nueva_pregunta.save()

                    # Crear opciones para esta pregunta
                    opciones_data = request.POST.getlist(f'opciones_{pregunta_form.prefix}')
                    es_correcta_data = request.POST.getlist(f'es_correcta_{pregunta_form.prefix}')

                    for texto, es_correcta in zip(opciones_data, es_correcta_data):
                        nueva_opcion = opcion(
                            pregunta=nueva_pregunta,
                            texto=texto,
                            es_correcta=(es_correcta == 'on')
                        )
                        nueva_opcion.save()
            messages.success(request, "Examen creado con éxito.")
            return redirect('crear_examen')  # Redirigir después de guardar

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
def  inicioexamen(request):
     username = request.user.username
     es_staff = request.user.is_staff 
     return render(request, 'areapersonal.html', {'username': username, 'es_staff': es_staff}) 

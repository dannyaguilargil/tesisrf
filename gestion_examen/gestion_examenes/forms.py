from django import forms
from .models import examen, pregunta, planificacion, opcion
from django.forms import modelformset_factory


class ExamenForm(forms.ModelForm):
    class Meta:
        model = examen
        fields = ['fechainicio', 'fechafinal', 'cantidadpreguntas', 'duracion', 'nintentos', 'planificacion']
        widgets = {
            'fechainicio': forms.DateInput(attrs={'type': 'date'}),
            'fechafinal': forms.DateInput(attrs={'type': 'date'}),
            'duracion': forms.TimeInput(attrs={'type': 'time'}),
        }

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = pregunta
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3}),
        }

class OpcionForm(forms.ModelForm):
    class Meta:
        model = opcion
        fields = ['texto', 'es_correcta']

# Formset para opciones
OpcionFormSet = modelformset_factory(
    opcion,
    form=OpcionForm,
    extra=4  # Número de opciones mostradas por defecto
)

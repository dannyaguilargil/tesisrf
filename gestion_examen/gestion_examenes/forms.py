from django import forms
from .models import examen, pregunta, planificacion

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

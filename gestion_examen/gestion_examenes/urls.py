from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.shortcuts import render, redirect

urlpatterns = [
   path('examen', views.examenes, name='examen'),
   path('examen/presentar', views.presentarexamen, name='presentarexamen'),
   path('examen/crear', views.crear_examen, name='crear_examen'),
]

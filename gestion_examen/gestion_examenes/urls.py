from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.shortcuts import render, redirect

urlpatterns = [
   path('examenes', views.presentarexamen, name='examenes'),
]

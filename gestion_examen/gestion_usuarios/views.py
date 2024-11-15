from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import os
from django.contrib.auth import logout as django_logout
# Create your views here.
################LOGIN####################
def home(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    print("Inicio sesion el administrador")
                    return redirect('examen')  
                elif user.groups.filter(name='informes').exists():
                    login(request, user)
                    print("Inicio sesión a gestion de informes")
                    return redirect('informe')
              
            
                else:
                    print("Inicio sesion el contratista")
                    login(request, user)
                    return redirect('identidades')
                   
        else:
            print("Usuario invalido")
            messages.error(request, 'Ingresar credenciales validos para iniciar sesión.')
            return redirect('inicio')
    else:
        print("Renderizado")
        form = AuthenticationForm()

    return render(request, 'home.html', {'form': form})
################LOGIN####################

#logout de la pagina
def logout(request):
    django_logout(request)
    return redirect('login')
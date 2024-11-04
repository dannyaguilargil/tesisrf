from django.shortcuts import render,redirect

def presentarexamen(request):
    username = request.user.username
    return render(request, 'examenes.html', {'username': username})

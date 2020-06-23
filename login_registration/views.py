from django.shortcuts import render


# Create your views here.
def login(request):
    return render(request, "login_registration/login.html")

def registration(request):
    return render(request, "login_registration/registration.html")

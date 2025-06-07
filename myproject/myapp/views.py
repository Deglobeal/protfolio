# views.py
from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')

def profile(request):
    return render(request, 'main/profile.html')

def resume(request):
    return render(request, 'main/resume.html')

def certificate(request):
    return render(request, 'main/certificate.html')  

def skills(request):
    return render(request, 'main/skills.html')

def contact(request):
    return render(request, 'main/contact.html')

def social(request):
    return render(request, 'main/social.html')

def email(request):
    return render(request, 'main/email.html')

def project(request):
    return render(request, 'main/project.html')